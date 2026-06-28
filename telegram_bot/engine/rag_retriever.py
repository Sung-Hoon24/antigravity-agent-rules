# -*- coding: utf-8 -*-
"""
LangChain & Vanilla Python 하이브리드 RAG 지식 검색기 (Chroma DB 및 증분 동기화 고도화 버전)
- 다중 폴더(Obsidian 볼트 및 ai connect 로컬 지식) 스캔 체계를 가동합니다.
- 파일의 마지막 수정 시각(mtime)을 감지하여 sync_cache.json 캐시와 교차 비교합니다.
- 변경된 파일(신규 또는 수정)의 청크들만 골라 임베딩을 요청하는 '스마트 스킵 증분 동기화'를 통해 API 호출을 1초 미만으로 단축시킵니다.
- Chroma DB 적재 시, 수정된 파일의 기존 구버전 청크들을 메타데이터 필터링으로 자동 일괄 삭제(Clean Upsert)하여 데이터 중복 적재를 차단합니다.
"""

import os
import re
import json
import time
from typing import List, Dict, Any

# ────────── [의존성 방어 코드: chromadb 및 langchain 동적 로드] ──────────
try:
    import chromadb

    HAS_CHROMADB = True
except ImportError:
    HAS_CHROMADB = False
    print("⚠️ [RAG] chromadb 패키지가 감지되지 않았습니다. 내장 키워드 매칭 검색 엔진으로 작동합니다.")

try:
    from langchain.text_splitter import RecursiveCharacterTextSplitter

    HAS_LANGCHAIN = True
except ImportError:
    HAS_LANGCHAIN = False

# 대표님의 다중 경로 설정 (Multi-path)
DEFAULT_VAULT_PATHS = [
    r"C:\1인기업\Obsidian",
    r"C:\1인기업\Apps\0312라이브_자동화 루나과제\로컬지식",
    r"c:\1인기업\Apps\유튜브에이전트\로컬지식",
]

DEFAULT_DB_PATH = r"c:\1인기업\Apps\유튜브에이전트\outputs\chroma_db"
SYNC_CACHE_PATH = r"c:\1인기업\Apps\유튜브에이전트\outputs\chroma_db\sync_cache.json"


class VanillaTextSplitter:
    """
    LangChain 미설치 시 가동되는 순수 파이썬 기반의 마크다운 최적화 텍스트 분할기.
    """

    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def split_text(self, text: str) -> List[str]:
        separators = ["\n\n", "\n", " ", ""]
        if len(text) <= self.chunk_size:
            return [text]

        chunks = []
        current_idx = 0
        while current_idx < len(text):
            end_idx = current_idx + self.chunk_size
            if end_idx >= len(text):
                chunks.append(text[current_idx:])
                break

            best_cut = end_idx
            for sep in separators:
                if not sep:
                    continue
                last_sep_pos = text.rfind(sep, current_idx, end_idx)
                if last_sep_pos != -1 and last_sep_pos > current_idx + (
                    self.chunk_size // 2
                ):
                    best_cut = last_sep_pos + len(sep)
                    break

            chunks.append(text[current_idx:best_cut])
            current_idx = max(best_cut - self.chunk_overlap, current_idx + 1)

        return chunks


# ────────── [0. 동기화 캐시 파일 제어 헬퍼 함수] ──────────


def load_sync_cache() -> Dict[str, float]:
    """로컬 동기화 캐시(mtime 데이터)를 디스크에서 로드합니다."""
    if not os.path.exists(SYNC_CACHE_PATH):
        return {}
    try:
        with open(SYNC_CACHE_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"⚠️ [RAG Cache] 동기화 캐시 파일 읽기 실패 (빈 캐시로 시작): {e}")
        return {}


def save_sync_cache(cache: Dict[str, float]) -> None:
    """동기화 완료 후 최신화된 mtime 목록을 디스크에 저장합니다."""
    try:
        os.makedirs(os.path.dirname(SYNC_CACHE_PATH), exist_ok=True)
        with open(SYNC_CACHE_PATH, "w", encoding="utf-8") as f:
            json.dump(cache, f, ensure_ascii=False, indent=2)
        print(f"💾 [RAG Cache] 동기화 캐시 파일 저장 완료. ({len(cache)}개 파일 추적 중)")
    except Exception as e:
        print(f"❌ [RAG Cache] 동기화 캐시 파일 저장 실패: {e}")


# ────────── [1. 다중 경로 마크다운 및 텍스트 파일 스캔] ──────────


def scan_multiple_vaults(
    vault_paths: List[str] = DEFAULT_VAULT_PATHS,
) -> List[Dict[str, Any]]:
    """
    다중 로컬 지식 경로들을 순회하며 내부에 존재하는 .md 및 .txt 파일들을 안전하게 누적 스캔합니다.
    각 파일의 마지막 수정 시각(mtime) 센서 데이터를 획득하여 메타데이터에 포함합니다.
    """
    documents = []

    for vault_path in vault_paths:
        if not os.path.exists(vault_path):
            print(f"⚠️ [RAG Scan Warning] 지식 경로가 존재하지 않아 건너뜁니다: {vault_path}")
            continue

        vault_name = os.path.basename(vault_path)
        if not vault_name:  # 루트 드라이브 경로 처리 대응
            vault_name = (
                vault_path.replace(":", "").replace("\\", "_").replace("/", "_")
            )

        print(f"📂 [RAG Scan] 지식 폴더 탐색 시작: {vault_path}")

        # os.walk를 이용해 하위 모든 파일 재귀적 탐색
        for root, dirs, files in os.walk(vault_path):
            # 💡 [방어 로직] 경로명에 Archived, 보관함, 폐기 등이 포함되면 하위 디렉토리 탐색에서 완전히 제외 (Pruning)
            if any(kw in root for kw in ["Archived", "보관함", "폐기"]):
                dirs.clear()  # 하위 디렉토리 순회 방어
                continue

            for file in files:
                # 마크다운(.md) 및 일반 텍스트(.txt) 지원 (요구사항 반영)
                if file.lower().endswith((".md", ".txt")):
                    file_path = os.path.join(root, file)
                    try:
                        # 1. 파일 수정 시각(mtime) 센서 가동
                        mtime = os.path.getmtime(file_path)

                        # 2. 인코딩 안전 로드 (utf-8 및 cp949 한글 폴백)
                        content = ""
                        try:
                            with open(file_path, "r", encoding="utf-8") as f:
                                content = f.read()
                        except UnicodeDecodeError:
                            with open(file_path, "r", encoding="cp949") as f:
                                content = f.read()

                        # 3. 메타데이터 구성 (출처 vault 명시)
                        metadata = {
                            "source": os.path.abspath(file_path),
                            "filename": file,
                            "relative_path": os.path.relpath(file_path, vault_path),
                            "mtime": mtime,
                            "vault_source": vault_name,
                        }

                        # 마크다운 프론트매터 파싱 분리
                        clean_content = content
                        if file.lower().endswith(".md"):
                            front_matter_match = re.match(
                                r"^---\s*\n(.*?)\n---\s*\n", content, re.DOTALL
                            )
                            if front_matter_match:
                                raw_yaml = front_matter_match.group(1)
                                clean_content = content[front_matter_match.end() :]
                                for line in raw_yaml.split("\n"):
                                    if ":" in line:
                                        key, val = line.split(":", 1)
                                        metadata[key.strip()] = val.strip().strip("\"'")

                        documents.append(
                            {"content": clean_content.strip(), "metadata": metadata}
                        )
                    except Exception as file_err:
                        print(f"⚠️ [RAG Scan Error] 파일 스캔 중 건너뜀 ({file}): {file_err}")

    return documents


def chunk_obsidian_documents(
    documents: List[Dict[str, Any]], chunk_size: int = 800, chunk_overlap: int = 150
) -> List[Dict[str, Any]]:
    """
    파싱된 문서들을 의미적 청크(Chunk) 단위로 분할합니다.
    """
    splitted_chunks = []
    if HAS_LANGCHAIN:
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=["\n\n", "\n", " ", ""],
        )
    else:
        splitter = VanillaTextSplitter(
            chunk_size=chunk_size, chunk_overlap=chunk_overlap
        )

    for doc in documents:
        raw_text = doc["content"]
        metadata = doc["metadata"]
        try:
            chunks = splitter.split_text(raw_text)
            for idx, chunk in enumerate(chunks):
                chunk_meta = metadata.copy()
                chunk_meta["chunk_id"] = (
                    f"{metadata['chunk_id_prefix']}_chunk_{idx}"
                    if "chunk_id_prefix" in metadata
                    else f"{metadata['filename']}_chunk_{idx}"
                )
                splitted_chunks.append(
                    {"content": chunk.strip(), "metadata": chunk_meta}
                )
        except Exception as split_err:
            print(f"⚠️ [RAG Split Error] {metadata['filename']} 분할 실패: {split_err}")

    return splitted_chunks


# ────────── [2. Gemini API 기반 벡터 임베딩 획득] ──────────


def get_gemini_embedding(text: str, api_key: str = None) -> List[float]:
    """
    Gemini API (text-embedding-004)를 활용해 텍스트의 임베딩 벡터를 가져옵니다.
    """
    if not api_key:
        from telegram_bot.config import GEMINI_API_KEY, YOUTUBE_API_KEY

        api_key = GEMINI_API_KEY or YOUTUBE_API_KEY
        if api_key:
            api_key = api_key.split(",")[0].strip()

    if not api_key:
        raise ValueError("Gemini API 키 누락으로 인해 임베딩 조회가 불가능합니다.")

    try:
        from google import genai

        client = genai.Client(api_key=api_key)
        response = client.models.embed_content(
            model="text-embedding-004", contents=text
        )
        return response.embeddings[0].values
    except Exception as e:
        print(f"⚠️ [RAG Embedding Error] Gemini 임베딩 API 호출 에러: {e}")
        raise e


# ────────── [3. 스마트 스킵 임베딩 및 DB 적재 (index_vault_to_chroma) ] ──────────


def index_vault_to_chroma(
    vault_paths: List[str] = DEFAULT_VAULT_PATHS, db_path: str = DEFAULT_DB_PATH
) -> Dict[str, Any]:
    """
    다중 지식 소스를 스캔하고 캐시(sync_cache.json)에 기록된 mtime과 비교하여,
    수정되거나 신규 생성된 파일만 임베딩하여 Chroma DB 컬렉션에 적재(Clean Upsert)합니다.
    - 🚨 [서킷 브레이커]: 업데이트할 청크가 100개를 초과할 경우 안전을 위해 API 호출을 차단합니다.
    - 🚨 [Emergency Stop]: 임베딩 중 API Quota 초과(429 등) 감지 시, 즉시 중단하고 직전 성공 데이터만 저장합니다.
    """
    # 1. mtime 동기화 캐시 로드
    sync_cache = load_sync_cache()

    # 2. 다중 경로 전체 문서 스캔
    raw_docs = scan_multiple_vaults(vault_paths)
    total_files = len(raw_docs)

    if total_files == 0:
        return {
            "status": "success",
            "total_files": 0,
            "updated_files": 0,
            "skipped_files": 0,
            "report_message": "📂 스캔 결과, 읽어올 마크다운 및 텍스트 파일이 없습니다.",
        }

    # 3. 증분 동기화(Incremental Sync) 대상 필터링
    updated_docs = []
    skipped_count = 0
    new_sync_cache = sync_cache.copy()  # 부분 성공 기록을 위한 복사본

    for doc in raw_docs:
        meta = doc["metadata"]
        file_abspath = meta["source"]
        current_mtime = meta["mtime"]

        # 캐시에 이전 기록이 존재하고 mtime이 동일하다면 임베딩 스킵
        last_sync_mtime = sync_cache.get(file_abspath)
        if last_sync_mtime is not None and last_sync_mtime == current_mtime:
            skipped_count += 1
            continue

        doc["metadata"]["chunk_id_prefix"] = os.path.basename(file_abspath)
        updated_docs.append(doc)

    updated_count = len(updated_docs)
    print(
        f"📊 [RAG Index Stats] 총 {total_files}개 문서 중 {updated_count}개 업데이트 필요 ({skipped_count}개 스킵 완료)"
    )

    if updated_count == 0:
        # 모든 파일이 스킵된 경우 캐시 동기화 완료
        # (새 스캔본에 없어진 파일이 있을 수 있으므로 현재 존재하는 파일들의 mtime만 갱신 보존)
        save_sync_cache(
            {d["metadata"]["source"]: d["metadata"]["mtime"] for d in raw_docs}
        )
        return {
            "status": "success",
            "total_files": total_files,
            "updated_files": 0,
            "skipped_files": skipped_count,
            "report_message": f"⚡ *증분 동기화 완료!* (Chroma DB가 최신 상태입니다.)\n• 총 `{total_files}`개 문서 중 `0`개 업데이트됨 (`{skipped_count}`개 스마트 스킵)",
        }

    # 4. 업데이트가 필요한 파일들의 청크화 실행
    updated_chunks = chunk_obsidian_documents(updated_docs)

    # 🚨 1회 최대 동기화 캡 (Hard Limit) 적용
    MAX_EMBED_LIMIT = 100
    if len(updated_chunks) > MAX_EMBED_LIMIT:
        print(
            f"🚨 [RAG Circuit Breaker] 업데이트 대상 청크 수 {len(updated_chunks)}개가 상한선 {MAX_EMBED_LIMIT}개를 초과하여 동기화를 차단합니다."
        )
        return {
            "status": "blocked_limit",
            "reason": f"1회 업데이트 대상 청크가 {MAX_EMBED_LIMIT}개를 초과했습니다. (총 {len(updated_chunks)}개 청크)",
            "solution": "한 번에 너무 많은 파일이 추가되었습니다. 파일을 나누어 이동시킨 후 다시 /index 를 시도해 주세요.",
        }

    # 5. Chroma DB 적재 실행
    if not HAS_CHROMADB:
        # ⚠️ [ChromaDB 부재 시 오프라인 로컬 JSON 캐시 폴백 업데이트]
        backup_file = os.path.join(db_path, "local_fallback_db.json")
        print("💾 [RAG Fallback] chromadb 미감지로 인해 로컬 JSON 백업 파일의 증분 병합을 개시합니다.")

        existing_chunks = []
        if os.path.exists(backup_file):
            try:
                with open(backup_file, "r", encoding="utf-8") as f:
                    existing_chunks = json.load(f)
            except Exception:
                pass

        updated_sources = {doc["metadata"]["source"] for doc in updated_docs}
        filtered_chunks = [
            c for c in existing_chunks if c["metadata"]["source"] not in updated_sources
        ]
        filtered_chunks.extend(updated_chunks)

        try:
            os.makedirs(db_path, exist_ok=True)
            with open(backup_file, "w", encoding="utf-8") as f:
                json.dump(filtered_chunks, f, ensure_ascii=False, indent=2)

            # 오프라인 성공 시에는 전체 동기화 성공으로 처리
            save_sync_cache(
                {d["metadata"]["source"]: d["metadata"]["mtime"] for d in raw_docs}
            )
            return {
                "status": "success",
                "total_files": total_files,
                "updated_files": updated_count,
                "skipped_files": skipped_count,
                "report_message": f"🧹 *오프라인 증분 동기화 완료!* (백업 JSON 캐시 갱신)\n• 총 `{total_files}`개 문서 중 `{updated_count}`개 업데이트됨 (`{skipped_count}`개 스마트 스킵)",
            }
        except Exception as e:
            return {
                "status": "error",
                "total_files": total_files,
                "updated_files": 0,
                "skipped_files": 0,
                "report_message": f"❌ 백업 JSON 갱신 에러: {str(e)}",
            }

    # ChromaDB 가동
    try:
        os.makedirs(db_path, exist_ok=True)
        chroma_client = chromadb.PersistentClient(path=db_path)
        collection = chroma_client.get_or_create_collection(name="obsidian_vault")

        # 🧹 [Clean Upsert 방어 로직]
        # 수정/삭제된 파일의 구버전 청크들이 DB에 그대로 쌓이는 것을 방지하기 위해
        # 이번에 업데이트되는 파일들의 기존 청크를 컬렉션에서 먼저 일괄 삭제(Clear)합니다.
        for doc in updated_docs:
            file_abspath = doc["metadata"]["source"]
            try:
                collection.delete(where={"source": file_abspath})
            except Exception:
                pass

        # 임베딩 획득 및 add
        ids = []
        documents = []
        metadatas = []
        embeddings = []

        success_files_count = 0
        api_quota_triggered = False
        api_err_msg = ""

        print("🔮 [RAG Index] 변경된 지식 청크에 대해 Gemini API 임베딩을 요청하는 중...")

        # 파일 단위 트랜잭션 처리 (부분 API 에러 시 안전 저장 방어)
        for doc in updated_docs:
            file_path = doc["metadata"]["source"]
            current_mtime = doc["metadata"]["mtime"]

            # 해당 단일 파일에 대한 청크들 획득
            file_chunks = chunk_obsidian_documents([doc])
            if not file_chunks:
                # 청크가 없는 파일은 성공한 것으로 마킹
                new_sync_cache[file_path] = current_mtime
                success_files_count += 1
                continue

            file_ids = []
            file_docs = []
            file_metas = []
            file_embeddings = []

            file_success = True
            for idx, chunk in enumerate(file_chunks):
                content = chunk["content"]
                meta = chunk["metadata"]

                # 메타데이터 평탄화
                flat_meta = {}
                for k, v in meta.items():
                    if isinstance(v, (dict, list)):
                        flat_meta[k] = json.dumps(v, ensure_ascii=False)
                    else:
                        flat_meta[k] = v

                try:
                    time.sleep(0.1)  # QPS 딜레이 보호
                    vector = get_gemini_embedding(content)

                    file_ids.append(
                        meta.get("chunk_id", f"{meta['filename']}_chunk_{idx}")
                    )
                    file_docs.append(content)
                    file_metas.append(flat_meta)
                    file_embeddings.append(vector)
                except Exception as embed_err:
                    err_str = str(embed_err).lower()
                    # 429 혹은 할당량 에러 키워드 스크리닝
                    if (
                        "429" in err_str
                        or "quota" in err_str
                        or "exhausted" in err_str
                        or "limit" in err_str
                    ):
                        api_quota_triggered = True
                        api_err_msg = str(embed_err)
                        file_success = False
                        break
                    else:
                        # 일반 에러 시에도 트랜잭션 실패 처리 후 중단
                        file_success = False
                        break

            if api_quota_triggered:
                print(f"🚨 [RAG Emergency Stop] API 할당량 한도 초과 감지: {api_err_msg}")
                break

            if file_success:
                # 단일 파일 임베딩 결과 합산
                ids.extend(file_ids)
                documents.extend(file_docs)
                metadatas.extend(file_metas)
                embeddings.extend(file_embeddings)

                # 이 파일의 동기화 상태는 캐시에 기록
                new_sync_cache[file_path] = current_mtime
                success_files_count += 1
            else:
                print(f"⚠️ [RAG Index] 파일 임베딩 오류 발생으로 인해 스킵: {file_path}")
                # 일반 오류가 났을 때는 루프를 멈추지 않고 부분 성공 적재 후 종료 처리 가능
                # 여기서는 안전하게 다음 파일로 넘어갑니다.

        # 임베딩이 성공적으로 모인 양만큼 최종 적재 (Emergency Stop 직전 데이터까지 적재)
        if ids:
            collection.add(
                ids=ids, documents=documents, metadatas=metadatas, embeddings=embeddings
            )
            print(f"✅ [RAG Index] {len(ids)}개 청크 신규 임베딩 벡터 적재 성공.")

        # 성공한 부분까지 캐시 파일 업데이트 영속화 (비용 절감 방어)
        save_sync_cache(new_sync_cache)

        # 할당량 에러로 루프가 강제 중단되었을 경우 처리
        if api_quota_triggered:
            return {
                "status": "blocked_api",
                "reason": "구글 API 할당량 초과 또는 과부하(429/Quota)가 감지되었습니다.",
                "solution": "약 1분 뒤에 다시 /index 를 입력해 보세요. (중단되기 전까지 작업된 데이터는 안전하게 자동 저장되었습니다.)",
            }

        return {
            "status": "success",
            "total_files": total_files,
            "updated_files": success_files_count,
            "skipped_files": skipped_count + (updated_count - success_files_count),
            "report_message": f"⚡ *Chroma DB 증분 동기화 완료!*\n• 총 `{total_files}`개 문서 중 `{success_files_count}`개 업데이트됨 (`{skipped_count + (updated_count - success_files_count)}`개 스마트 스킵)",
        }

    except Exception as e:
        print(f"🚨 [RAG Index Error] Chroma DB 증분 인덱싱 중 전반 실패: {e}")
        return {
            "status": "error",
            "total_files": total_files,
            "updated_files": 0,
            "skipped_files": 0,
            "report_message": f"🚨 *증분 인덱싱 실패*: `{str(e)}`",
        }


# ────────── [4. 유사도 기반 지식 검색 (Retrieve) 함수] ──────────


def retrieve_relevant_knowledge(
    query: str, limit: int = 3, db_path: str = DEFAULT_DB_PATH
) -> str:
    """
    기획 중인 쿼리와 가장 밀접한 다중 지식 청크들을 찾아 반환합니다.
    """
    print(f"🔍 [RAG Retrieve] 다중 지식 통합 검색 (Query: '{query}')")

    if not HAS_CHROMADB:
        return _fallback_keyword_retrieve(query, limit, db_path)

    try:
        if not os.path.exists(db_path):
            print("⚠️ [RAG Retrieve] Chroma DB 폴더 미부재로 키워드 매칭으로 우회합니다.")
            return _fallback_keyword_retrieve(query, limit, db_path)

        chroma_client = chromadb.PersistentClient(path=db_path)
        collections = chroma_client.list_collections()
        has_col = any(c.name == "obsidian_vault" for c in collections)
        if not has_col:
            return _fallback_keyword_retrieve(query, limit, db_path)

        collection = chroma_client.get_collection(name="obsidian_vault")

        # 쿼리 임베딩
        query_vector = get_gemini_embedding(query)

        # 조회
        results = collection.query(query_embeddings=[query_vector], n_results=limit)

        if not results or not results["documents"] or not results["documents"][0]:
            return ""

        context_str = "\n\n📚 === [로컬 지식 베이스 (Obsidian & AI Connect RAG)] ===\n"
        for i in range(len(results["documents"][0])):
            doc_content = results["documents"][0][i]
            meta = results["metadatas"][0][i]
            filename = meta.get("filename", "알 수 없는 문서")
            vault_source = meta.get("vault_source", "기타 로컬지식")

            context_str += f"\n📂 *출처: {filename} (소속: {vault_source})*\n"
            context_str += f"{doc_content.strip()}\n"
            context_str += "--------------------------------------\n"

        return context_str

    except Exception as e:
        print(f"⚠️ [RAG Retrieve Error] Chroma DB 조회 실패. 키워드 검색으로 우회 (에러: {e})")
        return _fallback_keyword_retrieve(query, limit, db_path)


def _fallback_keyword_retrieve(query: str, limit: int, db_path: str) -> str:
    """
    [Safety Fallback] Chroma DB 혹은 임베딩 실패 시 가동되는 로컬 키워드 가중치 검색기.
    """
    backup_file = os.path.join(db_path, "local_fallback_db.json")
    if not os.path.exists(backup_file):
        return ""

    try:
        with open(backup_file, "r", encoding="utf-8") as f:
            chunks = json.load(f)

        keywords = [
            kw.lower().strip() for kw in re.split(r"\s+", query) if len(kw.strip()) > 1
        ]
        matched_chunks = []

        for chunk in chunks:
            content = chunk["content"].lower()
            score = 0
            for kw in keywords:
                if kw in content:
                    score += content.count(kw)
            if score > 0:
                matched_chunks.append((score, chunk))

        matched_chunks = sorted(matched_chunks, key=lambda x: x[0], reverse=True)[
            :limit
        ]
        if not matched_chunks:
            return ""

        context_str = "\n\n📚 === [로컬 지식 베이스 (오프라인 키워드 매칭)] ===\n"
        for score, chunk in matched_chunks:
            meta = chunk["metadata"]
            context_str += f"\n📂 *출처: {meta.get('filename')} (소속: {meta.get('vault_source')}) (매칭점수: {score})*\n"
            context_str += f"{chunk['content'].strip()}\n"
            context_str += "--------------------------------------\n"

        return context_str
    except Exception as fe:
        print(f"⚠️ [RAG Fallback Fail] 키워드 백업 로드 실패: {fe}")
        return ""


# ────────── [ RAG 동기화 및 1단계 스캔 단독 테스트 실행기 ] ──────────


def test_rag_skeleton(vault_paths: List[str] = DEFAULT_VAULT_PATHS) -> Dict[str, Any]:
    """RAG 지식 스캔이 에러 없이 스캔할 수 있는지 탐색합니다."""
    print("🔍 [RAG Test] 옵시디언/로컬지식 스캔 개시...")
    raw_docs = scan_multiple_vaults(vault_paths)
    chunks = chunk_obsidian_documents(raw_docs)
    return {
        "status": "success",
        "loaded_documents_count": len(raw_docs),
        "created_chunks_count": len(chunks),
        "sample_chunk": chunks[0] if chunks else None,
    }

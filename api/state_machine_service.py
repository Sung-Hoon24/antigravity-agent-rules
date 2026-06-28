# -*- coding: utf-8 -*-
"""
유튜브 에이전트 콘솔 가디언 서비스 - 상태 머신 & 런봇 실시간 동기화 제어판 백엔드 API
- 텔레그램 봇들의 라이프사이클(가동/중단) 관리
- 봇 에러 실시간 추적 및 대시보드 HUD 전송
- CORS 보안 우회 지원 및 상태 머신 트랜지션 검증
- [NEW] 와치독(Watchdog) 자동 자가복구 데몬 루프 탑재
- [NEW] urllib 기반 무의존성 텔레그램 감성 장애 경보 모듈 장착
- [NEW] psutil 메모리 보호 및 렌더링 락 기반 세션 큐잉 가드 시스템 장착
"""

import json
import os
import sys
import time
import threading
import subprocess
import logging
import urllib.request
import urllib.parse
import psutil

# 💡 [한글 주석] 프로젝트 루트 디렉토리를 파이썬 모듈 탐색 경로(sys.path)에 수동 등록합니다.
# 이를 통해 api/ 서브폴더 내에서도 상위 폴더의 telegram_bot 패키지를 자유롭게 임포트할 수 있게 방어합니다.
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
if project_root not in sys.path:
    sys.path.append(project_root)

# 로거 설정: 에러 추적 및 가디아 보안 감사 추적용
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("StateMachineService")

from flask import Flask, request, jsonify

app = Flask(__name__)


# --- 🛡️ CORS 안전 우회 미들웨어 ---
@app.before_request
def handle_options():
    """OPTIONS Preflight 요청을 가로채 200 OK를 리턴합니다."""
    if request.method == "OPTIONS":
        return "", 200


@app.after_request
def add_cors_headers(response):
    """모든 응답에 브라우저가 신뢰할 수 있는 CORS 헤더를 추가합니다."""
    response.headers.add("Access-Control-Allow-Origin", "*")
    response.headers.add("Access-Control-Allow-Headers", "Content-Type,Authorization")
    response.headers.add("Access-Control-Allow-Methods", "GET,PUT,POST,DELETE,OPTIONS")
    return response


# --- 🛠️ [실시간 로깅 및 관리 변수] ---
# 에러 로그 수집 메모리 버퍼 (최대 100개 기록)
ERROR_LOGS = []

# [와치독 전용 관리 메모리]
# 대표님이 대시보드로 기동해 둔 봇의 목표 제어 상태 (ON / OFF)
BOT_TARGET_STATES = {"aura": "OFF", "rofi": "OFF"}
# 연속 자동 복구 재시도 카운터 (최대 3회 작동)
BOT_RETRY_COUNT = {"aura": 0, "rofi": 0}

# [세션 큐잉 전용 락 지표]
RENDERING_LOCK = threading.Lock()
IS_RENDERING_ACTIVE = False
RENDERING_SESSION_OWNER = None


def monitor_bot_output(bot_type: str, process: subprocess.Popen):
    """
    💡 [한글 주석] 봇 프로세스의 표준 출력(stdout + stderr)을 실시간으로 감시합니다.
    출력물 중 에러 징후를 발견 시 메모리 큐에 등록하여 대시보드 HUD에 즉시 뿌려줍니다.
    """
    logger.info(f"[{bot_type.upper()}] 실시간 에러 로깅 스레드가 기동되었습니다.")
    while True:
        line = process.stdout.readline()
        if not line:
            break
        try:
            line_str = line.decode("utf-8", errors="ignore").strip()
        except Exception:
            continue

        if not line_str:
            continue

        # 에러 관련 키워드 검출
        is_err = False
        lower_line = line_str.lower()
        err_keywords = [
            "error",
            "exception",
            "failed",
            "critical",
            "traceback",
            "🚨",
            "❌",
            "unauthorized",
        ]
        if any(k in lower_line for k in err_keywords):
            is_err = True

        if is_err:
            timestamp = time.strftime("%H:%M:%S")
            # 최대 100개까지만 보존하여 메모리 누수를 방어합니다.
            if len(ERROR_LOGS) > 100:
                ERROR_LOGS.pop(0)
            ERROR_LOGS.append(
                {
                    "timestamp": timestamp,
                    "error_message": f"[{bot_type.upper()}] {line_str}",
                }
            )
            logger.warning(f"🚨 [검출오류] {bot_type.upper()}: {line_str}")


def get_bot_status(bot_type: str) -> str:
    """
    💡 [한글 주석] psutil을 이용해 시스템 전체 프로세스를 조사하여
    해당 봇의 가동 상태를 ON/OFF 문자열로 확실히 반환합니다.
    """
    for proc in psutil.process_iter(["pid", "cmdline"]):
        try:
            cmd = proc.info.get("cmdline")
            if cmd:
                cmd_str = " ".join(cmd)
                # 윈도우/리눅스 환경의 경로 표기 차이를 방어하기 위해 조각 키워드로 검색
                if (
                    "telegram_bot" in cmd_str
                    and "bot.py" in cmd_str
                    and bot_type in cmd_str
                ):
                    return "ON"
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue
    return "OFF"


# --- 🚨 [NEW] urllib 기반 텔레그램 감성 알림 헬퍼 ---
def send_telegram_alert(message: str):
    """
    💡 [한글 주석] 패키지 의존성 없이 표준 urllib 라이브러리만을 활용하여,
    텔레그램 봇 토큰과 허용된 대표님의 chat_id로 크래시 현황 및 자가 복구 결과를 전송합니다.
    """
    try:
        # 순환 참조 및 미기동 크래시 방지를 위해 함수 내에서 안전하게 로드합니다.
        from telegram_bot.config import TELEGRAM_rubia_smart_bot_TOKEN, ALLOWED_USER_IDS

        # 설정이 비어있으면 전송을 안전하게 건너뜁니다.
        if not TELEGRAM_rubia_smart_bot_TOKEN or not ALLOWED_USER_IDS:
            logger.warning("텔레그램 경보 스킵: 봇 토큰 또는 ALLOWED_USER_IDS 가 설정되지 않았습니다.")
            return

        chat_id = ALLOWED_USER_IDS[0]
        token = TELEGRAM_rubia_smart_bot_TOKEN

        url = f"https://api.telegram.org/bot{token}/sendMessage"
        payload = {"chat_id": chat_id, "text": message, "parse_mode": "Markdown"}

        data = urllib.parse.urlencode(payload).encode("utf-8")
        req = urllib.request.Request(url, data=data)
        # 5초 타임아웃을 걸어 대시보드 응답성을 방어합니다.
        with urllib.request.urlopen(req, timeout=5) as response:
            response.read()
            logger.info(f"📬 텔레그램 경보 발송 완료: {message}")
    except Exception as e:
        logger.error(f"❌ 텔레그램 경보 발송 중 오류 발생: {e}")


# --- ⚙️ [NEW] 봇 백그라운드 프로세스 기동 공통 헬퍼 ---
def start_bot_process(bot_type: str) -> bool:
    """
    💡 [한글 주석] 가상환경(venv) 또는 시스템 파이썬을 자동으로 찾아
    봇 프로세스를 백그라운드로 띄우고 출력 감시 스레드를 작동시킵니다.
    """
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir)
    python_bin = sys.executable

    venv_path = os.path.join(project_root, ".venv", "Scripts", "python.exe")
    venv_std_path = os.path.join(
        project_root, ".venv_standard", "Scripts", "python.exe"
    )

    if os.path.exists(venv_path):
        python_bin = venv_path
    elif os.path.exists(venv_std_path):
        python_bin = venv_std_path

    cmd = [python_bin, "telegram_bot/bot.py", bot_type]

    # 💡 [한글 주석] 윈도우 환경에서 봇 기동 시 빈 콘솔 창이 깜빡이거나 팝업되는 현상을 방지하기 위한 startupinfo 설정
    startupinfo = None
    creation_flags = 0
    if os.name == "nt":
        creation_flags = 0x08000000  # CREATE_NO_WINDOW
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        startupinfo.wShowWindow = 0  # SW_HIDE (창 숨김)

    env = os.environ.copy()
    env["PYTHONUNBUFFERED"] = "1"  # 실시간 로그 출력 보장

    try:
        proc = subprocess.Popen(
            cmd,
            cwd=project_root,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            env=env,
            creationflags=creation_flags,
            startupinfo=startupinfo,
        )

        # 비동기 로그 모니터링 스레드 기동
        t = threading.Thread(
            target=monitor_bot_output, args=(bot_type, proc), daemon=True
        )
        t.start()

        logger.info(f"🚀 [{bot_type.upper()}] 봇 백그라운드 기동 성공 (PID: {proc.pid})")
        return True
    except Exception as e:
        logger.error(f"❌ [{bot_type.upper()}] 기동 실패: {e}")
        return False


# --- ⚙️ [NEW] 백그라운드 자가 복구 와치독 데몬 스레드 루프 ---
def watchdog_thread_loop():
    """
    💡 [한글 주석] 10초 주기로 무한 반복하며 봇들의 가동 상태를 감시합니다.
    목표 상태가 ON인데 프로세스가 예기치 않게 오프라인이 된 경우 자동으로 복구를 개시합니다.
    """
    logger.info("🛡️ [와치독] 자가 복구 감시 데몬 루프가 가동되었습니다.")
    while True:
        try:
            time.sleep(10)
            for bot_type in ["aura", "rofi"]:
                target_state = BOT_TARGET_STATES[bot_type]
                current_state = get_bot_status(bot_type)

                # 비정상 종료가 감지된 상황 (대시보드는 ON인데 프로세스는 죽은 경우)
                if target_state == "ON" and current_state == "OFF":
                    retries = BOT_RETRY_COUNT[bot_type]

                    if retries < 3:
                        BOT_RETRY_COUNT[bot_type] += 1
                        logger.warning(
                            f"🚨 [와치독] {bot_type.upper()} 봇 다운 감지! 자동 복구를 기동합니다. (시도: {BOT_RETRY_COUNT[bot_type]}/3)"
                        )

                        # 감성적 알림 전송
                        send_telegram_alert(
                            f"🚨 *[시스템 경보]*\n"
                            f"• 봇 ID: `{bot_type.upper()}`\n"
                            f"• 상태: *비정상 종료 감지*\n"
                            f"• 조치: *와치독 자동 복구 시도* (시도: `{BOT_RETRY_COUNT[bot_type]}`/3회)"
                        )

                        # 자동 재시작 시도
                        success = start_bot_process(bot_type)
                        time.sleep(2.5)  # 기동 안정화 대기

                        if success and get_bot_status(bot_type) == "ON":
                            BOT_RETRY_COUNT[bot_type] = 0  # 복구 성공 시 카운트 리셋
                            send_telegram_alert(
                                f"✅ *[자가 복구 성공]*\n"
                                f"• 봇 ID: `{bot_type.upper()}`\n"
                                f"• 복구 상태: *ONLINE 복귀 완료*\n"
                                f"• 시스템 감시가 실시간으로 재개되었습니다."
                            )
                            logger.info(f"✅ [와치독] {bot_type.upper()} 봇이 정상적으로 복구되었습니다.")
                        else:
                            logger.error(f"❌ [와치독] {bot_type.upper()} 봇 자동 기동 재시도 실패.")

                    elif retries == 3:
                        # 3회 초과 실패 시 영구 경보 발송 후 카운트를 4로 올려 중복 메시지 방지
                        BOT_RETRY_COUNT[bot_type] += 1
                        send_telegram_alert(
                            f"🔥 *[자가 복구 최종 실패]*\n"
                            f"• 봇 ID: `{bot_type.upper()}`\n"
                            f"• 상태: *3회 연속 자동 복구 실패*\n"
                            f"• 조치: *수동 점검 필요* (네트워크 상태 또는 로컬 환경을 검사하십시오)"
                        )
                        logger.critical(
                            f"🔥 [와치독] {bot_type.upper()} 봇 3회 연속 복구 실패. 자가 진단 중단."
                        )
        except Exception as e:
            logger.error(f"⚠️ [와치독] 감시 루프 실행 도중 예외 발생: {e}")


# --- 🛠️ [핵심 구조체] State Machine 계약 정의 ---
STATE_MACHINE_RULES = {
    "INITIAL": {
        "HOOK_A": "시청자 관심을 끄는 초기 정보 제공 단계",
        "HOOK_B": "질문을 던져 지적 호기심을 유발하는 도입부",
        "INPUT": "텔레그램 영상 제작 파이프라인의 에셋 및 자연어 입력 수신 단계",
    },
    "HOOK_A": {
        "GAP_ENTRY": "정보 과부하로 인한 논리적 공백 발생 (Knowledge Gap)",
        "END_OF_ACT": "다음 섹션으로 자연스러운 전환 완료",
    },
    "HOOK_B": {
        "GAP_ENTRY": "논리적 모순 발견 -> 지식의 간극 유발",
        "FAIL_TRANSITION": "사용자 입력 실패 또는 외부 시스템 오류 (VOID)",
    },
    "KNOWLEDGE_GAP": {
        "PAYWALL_TRIGGER": "지적 결핍 최대치 도달, 유료 게이트 진입 시도",
        "EXIT_SUCCESS": "솔루션을 발견하고 다음 단계로 성공적으로 이동",
    },
    "INPUT": {
        "LOCAL_LLM_RUNNING": "로컬 LLM JSON 구조화 엔진 가동 단계",
        "RENDERING": "로컬 PC 환경의 영상 렌더링 엔진 호출 및 구동 단계",
    },
    "LOCAL_LLM_RUNNING": {
        "JSON_PARSE_SUCCESS": "로컬 LLM JSON 변환 및 정형화 검증 성공 단계",
        "JSON_PARSE_FAILED": "로컬 LLM 분석 장애 또는 JSON 파싱 오류 단계",
    },
    "JSON_PARSE_FAILED": {"CLOUD_FALLBACK": "클라우드(Gemini API) 엔진으로 즉각적인 안전 폴백 전이"},
    "CLOUD_FALLBACK": {
        "JSON_PARSE_SUCCESS": "클라우드 폴백 엔진을 통한 구조화 JSON 데이터 확보 성공",
        "FAIL_TRANSITION": "클라우드 엔진마저 실패하여 대기/종료 단계로 전이",
    },
    "JSON_PARSE_SUCCESS": {"RENDERING": "정형 JSON 메타데이터 기반의 비디오 자동 병합 및 인코딩 가동"},
    "RENDERING": {"REVIEW": "렌더링 완료 후 사용자/에이전트 리뷰를 위한 결과물 송출 및 검수 대기"},
    "REVIEW": {
        "APPROVE": "비디오 검수가 통과되어 대표님의 승인 시그널이 도달한 단계",
        "INPUT": "검수 실패/반려되어 다시 기획/에셋 입력 단계로 롤백",
    },
    "APPROVE": {"REPORT": "유튜브 API 업로드 실행 후 업로드 결과 보고 및 세션 큐 정리 단계"},
    "REPORT": {"INPUT": "워크플로우가 완전히 종료되고 다음 새로운 기획을 대기하는 상태"},
}


class APIError(Exception):
    """Funnel State Machine 전용 커스텀 예외 클래스."""

    def __init__(self, message: str, code: str, status_code: int = 400):
        super().__init__(message)
        self.error_code = code
        self.status_code = status_code


def void_transition_failure(
    current_state: str, next_state: str, payload: dict = None, reason: str = None
):
    """VOID Transition Failure를 강제하는 함수 (논리적 공백 연출 및 디버깅 데이터 로깅 강화)."""
    log_msg = (
        f"🚨 [VOID Transition Alert] [{current_state}] -> [{next_state}] 부적절한 전이 감지."
    )
    if reason:
        log_msg += f" 사유: {reason}"
    if payload:
        log_msg += f" | Payload: {json.dumps(payload, ensure_ascii=False)}"
    logger.warning(log_msg)

    raise APIError(
        message=f"데이터 흐름 오류: 현재 상태에서 '{next_state}'로의 논리적 연결 고리가 누락되었습니다. (System Void Detected: {reason or '규칙 위배'})",
        code="ERROR_4001_VOID",
        status_code=422,
    )


def invalid_state_transition(current_state: str, next_state: str):
    """State Machine 규칙 위반 시 발생하는 일반 오류."""
    raise APIError(
        message=f"시스템 상태 불일치: '{current_state}'에서 '{next_state}'로의 직접적인 전환은 허용되지 않습니다. 논리적 경로를 점검해야 합니다.",
        code="ERROR_4002_INVALID_STATE",
        status_code=403,
    )


# --- 📡 API 엔드포인트 구현 (Flask 라우팅) ---


@app.route("/api/v1/transition", methods=["POST"])
def transition_state():
    """Funnel State Machine의 상태 전환을 처리하는 핵심 게이트웨이."""
    data = request.get_json()
    if not data or "current_state" not in data or "next_state" not in data:
        return (
            jsonify(
                {"status": "fail", "message": "필수 파라미터 (current_state, next_state) 누락"}
            ),
            400,
        )

    current = data["current_state"].upper()
    next_s = data["next_state"].upper()
    payload = data.get("payload", {})
    reason = data.get("reason")

    try:
        if current not in STATE_MACHINE_RULES:
            raise APIError(
                f"알 수 없는 상태입니다. 시스템에 정의되지 않은 Current State '{current}'입니다.",
                code="ERROR_4003_UNKNOWN_STATE",
                status_code=400,
            )

        # --- [NEW] 세션 큐잉 및 메모리 가드 구현 ---
        # 1. RENDERING 단계로 진입을 원할 때
        if next_s == "RENDERING":
            # 물리적 메모리가 85% 이상 고갈된 상태인지 확인합니다.
            mem_usage = psutil.virtual_memory().percent
            if mem_usage > 85.0:
                logger.warning(
                    f"⚠️ [메모리 가드] 현재 로컬 메모리 점유율({mem_usage}%)이 한계치를 초과하여 렌더링을 지연시킵니다."
                )
                return (
                    jsonify(
                        {
                            "status": "wait",
                            "message": f"시스템 물리 메모리가 임계치({mem_usage}%)를 초과했습니다. 메모리 안정화를 대기합니다.",
                            "error_code": "ERROR_429_MEMORY_FULL",
                        }
                    ),
                    202,
                )  # 202 Accepted: 요청은 받았으나 보류 대기 상태를 나타냅니다.

            # 이중 렌더링 락 점유 상태 검사
            with RENDERING_LOCK:
                global IS_RENDERING_ACTIVE, RENDERING_SESSION_OWNER
                if IS_RENDERING_ACTIVE:
                    logger.warning(
                        f"🔒 [세션 큐잉] 렌더링 슬롯이 이미 점유되어 있습니다. (소유자: {RENDERING_SESSION_OWNER})"
                    )
                    return (
                        jsonify(
                            {
                                "status": "wait",
                                "message": f"현재 다른 에이전트({RENDERING_SESSION_OWNER})가 비디오 렌더링 작업을 실행 중입니다. 대기열에 진입합니다.",
                                "error_code": "ERROR_429_QUEUE_ACTIVE",
                            }
                        ),
                        202,
                    )
                else:
                    # 렌더링 독점 슬롯 점유 획득
                    IS_RENDERING_ACTIVE = True
                    RENDERING_SESSION_OWNER = payload.get("bot_name", current)
                    logger.info(
                        f"🔒 [렌더링 락 획득] 렌더링을 독점 개시합니다. 소유자: {RENDERING_SESSION_OWNER}"
                    )

        # 2. RENDERING 단계가 종료되어 다음 상태로 넘어갈 때 락을 풀어줍니다.
        if current == "RENDERING":
            with RENDERING_LOCK:
                if IS_RENDERING_ACTIVE:
                    logger.info(
                        f"🔓 [렌더링 락 해제] 렌더링이 종료되어 락을 해제합니다. (이전 소유자: {RENDERING_SESSION_OWNER})"
                    )
                    IS_RENDERING_ACTIVE = False
                    RENDERING_SESSION_OWNER = None

        allowed_transitions = STATE_MACHINE_RULES[current]
        if next_s not in allowed_transitions:
            void_transition_failure(current, next_s, payload=payload, reason=reason)

        logger.info(f"✅ [성공] {current} -> {next_s} 상태 전환 요청 수신. Payload 유효성 검사 시작.")

        if "PAYWALL" in next_s and payload.get("user_status") != "PREMIUM":
            return (
                jsonify(
                    {
                        "status": "fail",
                        "message": "유료 게이트 통과 실패. Premium Payload가 필요합니다.",
                        "error_code": "ERROR_4013_PAYWALL_FAIL",
                    }
                ),
                403,
            )

        return (
            jsonify(
                {
                    "status": "success",
                    "message": f"상태 전환 성공: {current}에서 {next_s}로 논리적 흐름을 확보했습니다.",
                    "new_state": next_s,
                    "transition_details": allowed_transitions[next_s],
                }
            ),
            200,
        )

    except APIError as e:
        logger.error(f"❌ [{e.error_code}] State Transition Failed: {str(e)}")
        return (
            jsonify({"status": "fail", "message": str(e), "error_code": e.error_code}),
            e.status_code,
        )
    except Exception as e:
        logging.critical(f"🔥 [시스템 크리티컬 에러] 처리 불가 예외 발생: {e}", exc_info=True)
        return (
            jsonify(
                {
                    "status": "fail",
                    "message": "서버 내부 오류가 감지되었습니다. 잠시 후 다시 시도해주세요.",
                    "error_code": "ERROR_5000_INTERNAL",
                }
            ),
            500,
        )


# --- 📡 런봇 관리 API 구현 (대시보드 실시간 동기화) ---


@app.route("/api/v1/runbot/status", methods=["GET"])
def runbot_status():
    """
    💡 [한글 주석] 각 봇들의 구동 상태(ON / OFF)를 확인하는 API입니다.
    대시보드가 3초마다 지속적으로 호출합니다.
    """
    try:
        return (
            jsonify(
                {
                    "status": "success",
                    "data": {
                        "aura": get_bot_status("aura"),
                        "rofi": get_bot_status("rofi"),
                    },
                }
            ),
            200,
        )
    except Exception as e:
        logger.error(f"봇 상태 조회 중 오류 발생: {e}")
        return jsonify({"status": "fail", "message": f"상태 조회 실패: {str(e)}"}), 500


@app.route("/api/v1/runbot/control", methods=["POST"])
def runbot_control():
    """
    💡 [한글 주석] 대시보드 토글 스위치에 반응하여
    봇 프로세스를 백그라운드로 띄우거나(START), 강제 중단(STOP)합니다.
    """
    data = request.get_json()
    if not data or "bot_type" not in data or "action" not in data:
        return (
            jsonify({"status": "fail", "message": "필수 파라미터 (bot_type, action) 누락"}),
            400,
        )

    bot_type = data["bot_type"].lower().strip()
    action = data["action"].upper().strip()

    if bot_type not in ["aura", "rofi"]:
        return jsonify({"status": "fail", "message": f"올바르지 않은 봇 타입: {bot_type}"}), 400

    if action not in ["START", "STOP"]:
        return jsonify({"status": "fail", "message": f"올바르지 않은 명령: {action}"}), 400

    current_status = get_bot_status(bot_type)

    if action == "START":
        # 💡 [NEW] 사용자가 켜기로 의도했으므로 목표 가동 상태를 ON으로 기록하고 카운트를 초기화합니다.
        BOT_TARGET_STATES[bot_type] = "ON"
        BOT_RETRY_COUNT[bot_type] = 0

        if current_status == "ON":
            return (
                jsonify(
                    {
                        "status": "success",
                        "message": f"{bot_type.upper()} 봇이 이미 가동 중입니다.",
                    }
                ),
                200,
            )

        # 공통 기동 헬퍼 함수를 호출합니다.
        success = start_bot_process(bot_type)

        if success:
            return (
                jsonify(
                    {
                        "status": "success",
                        "message": f"{bot_type.upper()} 봇 프로세스가 가동되었습니다.",
                    }
                ),
                200,
            )
        else:
            return (
                jsonify({"status": "fail", "message": "봇 기동 중 내부 프로세스 실행 에러가 발생했습니다."}),
                500,
            )

    elif action == "STOP":
        # 💡 [NEW] 사용자가 명시적으로 끄기로 했으므로 목표 상태를 OFF로 돌려 와치독이 재기동하지 못하게 막습니다.
        BOT_TARGET_STATES[bot_type] = "OFF"
        BOT_RETRY_COUNT[bot_type] = 0

        if current_status == "OFF":
            return (
                jsonify(
                    {
                        "status": "success",
                        "message": f"{bot_type.upper()} 봇이 이미 중지되었습니다.",
                    }
                ),
                200,
            )

        # psutil로 실행 중인 프로세스를 핀포인트 검사하여 프로세스를 격리 처분(종료)합니다.
        killed = False
        for proc in psutil.process_iter(["pid", "cmdline"]):
            try:
                cmd = proc.info.get("cmdline")
                if cmd:
                    cmd_str = " ".join(cmd)
                    if (
                        "telegram_bot" in cmd_str
                        and "bot.py" in cmd_str
                        and bot_type in cmd_str
                    ):
                        proc.terminate()
                        try:
                            proc.wait(timeout=3)
                        except psutil.TimeoutExpired:
                            proc.kill()
                        killed = True
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

        if killed:
            logger.info(f"✅ [{bot_type.upper()}] 봇 프로세스가 정상 중지되었습니다.")
            return (
                jsonify(
                    {
                        "status": "success",
                        "message": f"{bot_type.upper()} 봇 프로세스가 중지되었습니다.",
                    }
                ),
                200,
            )
        else:
            return jsonify({"status": "fail", "message": "중지할 프로세스를 발견하지 못했습니다."}), 500


@app.route("/api/v1/runbot/errors", methods=["GET"])
def runbot_errors():
    """
    💡 [한글 주석] 봇 동작 중 실시간으로 수집된 오류 항목들을 모아 대시보드 HUD에 넘겨줍니다.
    대시보드가 3초마다 지속적으로 호출합니다.
    """
    return jsonify({"status": "success", "data": ERROR_LOGS}), 200


if __name__ == "__main__":
    print("===========================================")
    print("🚀 API State Machine & Runbot Controller Service")
    print("- Listening on: http://127.0.0.1:5000")
    print("- Self-healing Watchdog: ACTIVE (10s intervals)")
    print("- Session Queueing & Memory Guard: ACTIVE")
    print("===========================================")

    # 💡 [NEW] 백그라운드 자가 복구 와치독 데몬 스레드 가동
    watchdog_thread = threading.Thread(target=watchdog_thread_loop, daemon=True)
    watchdog_thread.start()

    # debug=False로 가동하여 안전성을 극대화합니다.
    app.run(host="127.0.0.1", port=5000, debug=False)

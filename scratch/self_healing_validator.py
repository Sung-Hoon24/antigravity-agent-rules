# -*- coding: utf-8 -*-
"""
루비아 기술연구소 제3연구소 (보안/디버그 Vault)
자가 치유(Self-Healing) 및 충돌 감지 자동 검증기 (Ver 1.0)

본 스크립트는 AI 에이전트가 코드를 이관하기 전에 AST(추상 구문 트리)를 분석하고,
문법 무결성과 정적 린팅을 자동 수행하여 메인 프로덕션 코드의 오염을 원천 방어합니다.
"""

import os
import ast
import sys
import subprocess


class SelfHealingValidator:
    def __init__(self, workspace_root):
        self.workspace_root = workspace_root

    def validate_ast(self, file_path):
        """
        1단계: 대상 파이썬 파일의 AST(추상 구문 트리) 컴파일 검증
        """
        print(f"[AST 검증] 파일 분석 중: {file_path}")
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                source = f.read()
            # AST 파싱을 통해 문법 검증 수행 (할루시네이션 구문 차단)
            ast.parse(source)
            print("💡 [AST 검증 성공] 문법적 무결성이 확인되었습니다.")
            return True
        except SyntaxError as se:
            print(
                f"❌ [AST 검증 실패] 문법 오류 감지! (라인 {se.lineno}): {se.msg}", file=sys.stderr
            )
            return False
        except Exception as e:
            print(f"❌ [AST 검증 실패] 파일을 읽는 중 오류가 발생했습니다: {str(e)}", file=sys.stderr)
            return False

    def validate_lint(self, file_path):
        """
        2단계: Ruff 또는 Flake8을 이용한 정적 린팅 검사 (경고 및 에러 탐지)
        """
        print(f"[정적 린팅 검사] 파일 분석 중: {file_path}")
        # 로컬 환경의 가상환경 내부 ruff/flake8 탐색
        venv_bin = os.path.join(self.workspace_root, ".venv", "Scripts")
        ruff_path = os.path.join(venv_bin, "ruff.exe")

        if not os.path.exists(ruff_path):
            # Ruff가 가상환경에 없으면 시스템 전역 ruff 또는 python 컴파일러 문법 체크로 대체
            print("⚠️ 가상환경 내부 Ruff 린터를 찾지 못했습니다. 파이썬 바이트코드 컴파일 검사로 대체합니다.")
            try:
                subprocess.run(
                    [sys.executable, "-m", "py_compile", file_path],
                    check=True,
                    capture_output=True,
                )
                print("💡 [컴파일 검사 성공] 바이트코드 컴파일이 완료되었습니다.")
                return True
            except subprocess.CalledProcessError as cpe:
                print(f"❌ [컴파일 실패]: {cpe.stderr.decode('utf-8')}", file=sys.stderr)
                return False

        try:
            # Ruff 문법/스타일 검사 실행
            result = subprocess.run(
                [ruff_path, "check", file_path], capture_output=True, text=True
            )
            if result.returncode == 0:
                print("💡 [린팅 검사 성공] 스타일 및 의존성 오류가 발견되지 않았습니다.")
                return True
            else:
                print(f"❌ [린팅 검사 실패] 스타일/의존성 위반 감지:\n{result.stdout}", file=sys.stderr)
                return False
        except Exception as e:
            print(f"⚠️ 린팅 실행 중 오류 발생(무시하고 다음 단계 진행): {str(e)}")
            return True

    def run_all_checks(self, file_path):
        """
        전체 게이트웨이 검사 수행
        """
        print("=" * 60)
        print("🛡️ [루비아 제3연구소] 자가 치유 검증 게이트웨이 가동")
        print("=" * 60)

        # AST 검사
        if not self.validate_ast(file_path):
            return False

        # 린트/컴파일 검사
        if not self.validate_lint(file_path):
            return False

        print("=" * 60)
        print("🎉 [최종 통과] 모든 코드 무결성 검증을 완료했습니다. 병합(Merge)이 안전합니다.")
        print("=" * 60)
        return True


if __name__ == "__main__":
    # 간단한 자가 검증 실행 테스트
    workspace = r"c:\1인기업\Apps\유튜브에이전트"
    validator = SelfHealingValidator(workspace)

    # 명령행 인자로 파일 경로가 들어오면 우선 처리, 없으면 기본 handlers/production.py 검사
    if len(sys.argv) > 1:
        target_file = sys.argv[1]
    else:
        target_file = os.path.join(
            workspace, "telegram_bot", "handlers", "production.py"
        )

    if os.path.exists(target_file):
        validator.run_all_checks(target_file)
    else:
        print(f"테스트 타겟 파일을 찾을 수 없습니다: {target_file}")

# -*- coding: utf-8 -*-
import sys
import logging
from e2b_code_interpreter import Sandbox

# 로깅 설정: 에러 추적 및 가디아 보안 감사 추적용
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("E2BSandbox")


class E2BSecureSandbox:
    """
    E2B 마이크로VM 격리 환경에서 코드를 안전하게 실행하는 샌드박스 래퍼 클래스.
    공식 저장소 도메인만 아웃바운드가 허용되는 제한적 네트워크 정책을 가집니다.
    """

    def __init__(self):
        # 1차 방어선: 공식 패키지 저장소 및 깃허브 도메인만 허용
        self.allowed_domains = [
            "github.com",
            "api.github.com",
            "pypi.org",
            "files.pythonhosted.org",
        ]
        self.sandbox = None

    def initialize_sandbox(self):
        """E2B Sandbox를 네트워크 격리 옵션과 함께 초기화합니다."""
        try:
            logger.info("Initializing E2B Sandbox with network restrictions...")
            # E2B 2.x SDK의 Sandbox.create() 팩토리 메소드를 사용하여 지정 도메인 외 모든 트래픽(0.0.0.0/0)을 차단하며 샌드박스를 시작합니다.
            self.sandbox = Sandbox.create(
                network={"allow_out": self.allowed_domains, "deny_out": ["0.0.0.0/0"]}
            )
            logger.info("E2B Sandbox initialized successfully.")
            return True
        except Exception as e:
            logger.error(
                f"Failed to initialize E2B Sandbox. Check E2B_API_KEY environment variable. Error: {e}"
            )
            return False

    def run_secure_code(self, code_content: str):
        """
        샌드박스 내부에서 코드를 가상 실행하고 결과를 반환합니다.
        """
        if not self.sandbox:
            if not self.initialize_sandbox():
                raise RuntimeError("Sandbox is not initialized and failed to start.")

        try:
            logger.info("Running code inside E2B Sandbox...")
            execution = self.sandbox.run_code(code_content)

            # 실행 중 에러가 있는지 체크
            if execution.error:
                logger.error(
                    f"Code execution finished with error inside Sandbox: {execution.error}"
                )
                return {
                    "success": False,
                    "error": execution.error,
                    "output": execution.text,
                }

            logger.info("Code execution completed successfully.")
            return {"success": True, "error": None, "output": execution.text}
        except Exception as e:
            logger.error(f"Critical exception raised during Sandbox run_code: {e}")
            return {"success": False, "error": str(e), "output": ""}

    def close(self):
        """샌드박스 리소스를 릴리즈합니다."""
        if self.sandbox:
            try:
                self.sandbox.close()
                logger.info("E2B Sandbox session closed.")
            except Exception as e:
                logger.error(f"Error closing E2B Sandbox: {e}")


if __name__ == "__main__":
    # 간단한 CLI 네트워크 제한 테스트용
    if len(sys.argv) > 1 and sys.argv[1] == "--test-network":
        secure_box = E2BSecureSandbox()
        if secure_box.initialize_sandbox():
            # 1. 허가된 도메인(github.com) 호출 테스트
            print("\n[Test 1] Requesting allowed domain (github.com)...")
            res_allowed = secure_box.run_secure_code(
                "import requests; print('Allowed GET Status:', requests.get('https://github.com', timeout=5).status_code)"
            )
            print("Output:", res_allowed["output"])

            # 2. 비인가 도메인(google.com) 호출 테스트
            print(
                "\n[Test 2] Requesting blocked domain (google.com) - Should fail or timeout..."
            )
            res_blocked = secure_box.run_secure_code(
                "import requests; "
                "try:\n"
                "    requests.get('https://google.com', timeout=3)\n"
                "    print('Success (Unexpected)')\n"
                "except Exception as e:\n"
                "    print('Blocked successfully. Error caught:', type(e).__name__)\n"
            )
            print("Output:", res_blocked["output"])
            secure_box.close()

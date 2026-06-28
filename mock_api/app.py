from flask import Flask, request, jsonify

# 시스템 에러 코드 정의 (회사 표준)
ERROR_CODES = {
    "SUCCESS": "OK",
    "INPUT_VALIDATION_FAILED": "ERROR_4001",  # Void Transition Failure Trigger Code
    "DATA_OVERLOAD": "ERROR_5003",  # System Overload Code
}

app = Flask(__name__)


@app.route("/api/v1/process_data", methods=["POST"])
def process_data():
    """
    [Mock Backend Gateway] 데이터 처리 시뮬레이션 API 엔드포인트.
    데이터 유효성 및 과부하 여부를 검증하는 핵심 모듈.
    """
    try:
        data = request.get_json()
    except Exception:
        return (
            jsonify(
                {
                    "status": "FAIL",
                    "code": ERROR_CODES["INPUT_VALIDATION_FAILED"],
                    "message": "Invalid JSON format.",
                }
            ),
            400,
        )

    payloads = data.get("payload", [])
    current_state = data.get("state", "INITIAL")
    attempt_count = data.get("attempts", 1)

    # 1. [핵심 검증] 입력 유효성 체크 (Payload Validation)
    if not payloads or len(payloads) < 3:
        return (
            jsonify(
                {
                    "status": "FAIL",
                    "code": ERROR_CODES["INPUT_VALIDATION_FAILED"],
                    "message": f"[{ERROR_CODES['INPUT_VALIDATION_FAILED']}] 필수 Payload가 부족합니다. 최소 3개 필요.",
                }
            ),
            400,
        )

    # 2. [핵심 검증] 데이터 과부하 체크 (DATA_OVERLOAD)
    if len(payloads) > 15 or attempt_count >= 3:
        return (
            jsonify(
                {
                    "status": "FAIL",
                    "code": ERROR_CODES["DATA_OVERLOAD"],
                    "message": f"[{ERROR_CODES['DATA_OVERLOAD']}] 데이터 과부하가 감지되었습니다. 시스템 자원 부족으로 처리를 중단합니다.",
                }
            ),
            503,
        )

    # 모든 검증 통과 시 성공 로직
    if current_state == "INITIAL":
        return (
            jsonify(
                {
                    "status": "SUCCESS",
                    "code": ERROR_CODES["SUCCESS"],
                    "message": "데이터 처리에 성공했습니다. Funnel 다음 단계로 진입합니다.",
                    "next_step": "/api/v1/success_state",
                }
            ),
            200,
        )

    return (
        jsonify(
            {
                "status": "SUCCESS",
                "code": ERROR_CODES["SUCCESS"],
                "message": "정상적으로 상태를 업데이트했습니다.",
            }
        ),
        200,
    )


@app.route("/api/v1/success_state", methods=["GET"])
def success_state():
    """성공 후 다음 단계로 넘기는 가짜 API."""
    return (
        jsonify(
            {
                "status": "SUCCESS",
                "code": ERROR_CODES["SUCCESS"],
                "message": "다음 콘텐츠 섹션으로 이동합니다.",
            }
        ),
        200,
    )


if __name__ == "__main__":
    # 실제 환경에서는 포트를 지정하는 것이 좋습니다.
    app.run(debug=True, port=5000)

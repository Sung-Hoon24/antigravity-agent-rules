import os
from flask import Flask, request, jsonify
from pydantic import BaseModel, Field

# from typing import Literal # Python 3.8+

# --- [설정] ---
app = Flask(__name__)
# API 키 검증을 위한 환경 변수 로드 (보안 필수)
API_KEY = os.environ.get("FUNNEL_GATEWAY_SECRET_KEY", "DUMMY_DEV_KEY")


# ---------------------------------------------------
# [데이터 구조 정의] - pydantic 사용 권장 (실제 배포 시)
# Client가 보내는 요청 데이터의 형식을 강제로 규정합니다.
class FunnelTriggerRequest(BaseModel):
    user_id: str = Field(..., description="고유 사용자 식별자")
    current_state: str = Field(..., description="현재 콘텐츠 블록 상태 (e.g., 'Hook', 'Void')")
    trigger_event: str = Field(
        ..., description="발생한 이벤트 트리거 (e.g., 'GapObserved', 'VideoEnd', 'CTAClick')"
    )
    data_params: dict = Field({}, description="추가 메타 데이터 (예: 특정 질문 ID)")


# ---------------------------------------------------
# [상태 머신 로직 정의] - 핵심 검증 테이블
# 이 테이블은 Funnel State Machine의 유일한 진실 공급원(Single Source of Truth)입니다.
VALID_TRANSITIONS = {
    ("Hook", "GapObserved"): {
        "next_state": "Void",
        "action": "Load_Information_Gap",
        "required_key": "GAP_OVERLAY",
    },
    ("Void", "FailedToUnderstand"): {
        "next_state": "Gate",
        "action": "Display_Logical_Void",
        "required_key": "VOID_GATE",
    },
    # ... 필요한 모든 상태 전이 로직을 정의합니다.
}


def validate_transition(
    current_state: str, trigger_event: str
) -> tuple[str, dict] | None:
    """상태와 이벤트를 기반으로 다음 상태 및 동작을 결정하는 핵심 함수."""
    key = (current_state, trigger_event)
    if key in VALID_TRANSITIONS:
        return VALID_TRANSITIONS[key]
    return None


# ---------------------------------------------------
# [엔드포인트 정의]
@app.route("/api/v1/funnel_state", methods=["POST"])
def funnel_state_router():
    """
    클라이언트(영상 플레이어)로부터 트리거를 받아 상태 전이 및 다음 액션을 결정합니다.
    """
    # 1. 보안 검증 (최우선 순위)
    request_api_key = request.headers.get("X-API-Key", "")
    if request_api_key != API_KEY:
        return jsonify({"error": "Unauthorized Access", "code": 403}), 403

    try:
        # 2. 요청 데이터 파싱 및 유효성 검증 (Pydantic 활용)
        data = request.get_json()
        if not data:
            return jsonify({"error": "Invalid JSON payload"}), 400

        # 실제 운영 환경에서는 Pydantic 모델을 사용하여 입력 데이터를 강제합니다.
        validated_request = FunnelTriggerRequest(**data)

    except Exception as e:
        print(f"Validation Error: {e}")
        return jsonify({"error": "Bad Request Data Format", "details": str(e)}), 400

    # 3. 핵심 상태 전이 로직 실행 (The Core Logic)
    transition_info = validate_transition(
        validated_request.current_state, validated_request.trigger_event
    )

    if not transition_info:
        return (
            jsonify(
                {
                    "status": "Failure",
                    "message": f"Invalid state transition attempt from {validated_request.current_state} with trigger {validated_request.trigger_event}.",
                    "action_required": None,  # 아무것도 하지 않음
                }
            ),
            409,
        )  # Conflict: 현재 상태에서 해당 이벤트는 불가능함

    # 4. 성공적인 전이 및 액션 결정
    next_state = transition_info["next_state"]
    action = transition_info["action"]
    required_key = transition_info["required_key"]

    response = {
        "status": "Success",
        "message": f"State transition successful. Moving to '{next_state}'.",
        "next_state": next_state,
        "action_type": action,  # 클라이언트에게 어떤 모듈을 로드할지 지시
        "required_asset_id": required_key,  # 필요한 에셋 ID (GAP_OVERLAY 등)
        # 실제로는 여기서 DB에 트래킹 로그를 기록해야 함.
    }

    return jsonify(response), 200


if __name__ == "__main__":
    print("--- Funnel State Machine API Starting Up ---")
    # 보안 경고: 개발용으로만 사용하며, 운영 환경에서는 WSGI 서버를 사용해야 합니다.
    app.run(debug=True, port=5000)

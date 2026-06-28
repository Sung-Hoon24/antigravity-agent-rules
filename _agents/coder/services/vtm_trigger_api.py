from flask import Flask, request, jsonify

app = Flask(__name__)


# --- [CORE LOGIC] ---
def _determine_visual_state(shock: float, conflict: str, stage: str) -> dict:
    """
    주어진 파라미터 조합에 따라 시각적 상태와 텍스트 출력을 결정하는 핵심 로직.
    이 함수가 콘텐츠의 '지적 충격'을 코드로 구현합니다.
    """
    state = {
        "visual_overlay": "none",
        "color_palette": "#1a1a2e",  # Deep Indigo Base
        "text_effect": "normal",
        "pacing_adjustment_ms": 0,  # 내레이션 속도 조절 (마일초)
        "required_assets": [],
    }

    # 1. 충격 강도(Shock Intensity)에 따른 기본 변수 설정
    if shock >= 0.8:
        state["visual_overlay"] = "glitch_effect_high"
        state["color_palette"] = "#ff006e"  # 경고색 (Magenta/Red)
        state["text_effect"] = "stuttering_text"
        state["pacing_adjustment_ms"] = 150  # 잠깐의 정지 시간 부여
    elif shock >= 0.4:
        state["visual_overlay"] = "data_noise_medium"
        state["color_palette"] = "#3a3f6e"  # 중립적이지만 불안한 색상
        state["text_effect"] = "subtle_fade"
        state["pacing_adjustment_ms"] = 50
    else:
        # 충격이 낮으면 안정적인 아카이브 톤 유지
        pass

    # 2. 데이터 불일치 수준(Data Conflict Level)에 따른 로직 오버라이드
    if conflict == "HIGH":
        state["visual_overlay"] = "critical_data_failure"  # 최상위 충격 효과
        state["color_palette"] = "#cc0000"  # 경고 빨강
        state["text_effect"] = "breaking_cipher"
        state["pacing_adjustment_ms"] = 300
        state["required_assets"].append("CRITICAL_ERROR_SOUND.mp3")

    elif conflict == "MEDIUM":
        # 중급 충돌: 시각적 왜곡과 질문형 아웃포커싱 조합
        if state["visual_overlay"] != "critical_data_failure":  # HIGH가 이미 덮어썼을 경우 무시
            state["visual_overlay"] = "temporal_distortion"
            state["pacing_adjustment_ms"] += 100

    # 3. 논지 전개 단계(Narrative Stage)에 따른 콘텐츠 지침 추가 (MVP 버전에서는 단순 로그 기록)
    if stage == "QUALIA_PROBLEM":
        state["required_assets"].append("MARYS_ROOM_IMAGE.png")
        state["visual_overlay"] = (
            state["visual_overlay"] or "abstract_concept"
        )  # Fallback

    return state


@app.route("/api/vtm/trigger", methods=["POST"])
def vtm_trigger():
    """
    VTM Trigger 서비스 엔드포인트. 시청자의 인지적 불일치 순간을 감지하고,
    비주얼/텍스트 출력 지침을 동적으로 반환합니다.

    Expected JSON Payload:
    {
        "time_code": "06:15",
        "shock_intensity": 0.75,   // 0.0 ~ 1.0 (높을수록 충격적)
        "data_conflict_level": "HIGH", // LOW, MEDIUM, HIGH
        "narrative_stage": "QUALIA_PROBLEM" // 현재 논지 단계 식별자
    }
    """
    try:
        data = request.get_json(force=True)

        # 필수 파라미터 유효성 검사 (Robustness Check)
        if not all(
            k in data
            for k in ["shock_intensity", "data_conflict_level", "narrative_stage"]
        ):
            return jsonify({"error": "Missing required payload parameters."}), 400

        shock = float(data["shock_intensity"])
        conflict = str(data["data_conflict_level"]).upper()
        stage = str(data["narrative_stage"]).upper()

        # 핵심 로직 호출
        visual_state = _determine_visual_state(shock, conflict, stage)

        return jsonify(
            {
                "status": "success",
                "trigger_time": data.get("time_code", "N/A"),
                "logic_applied": {
                    "description": f"{stage} 논지 단계에서 충격 강도 {shock:.2f}와 데이터 불일치 레벨 {conflict} 감지.",
                    "parameters_used": {
                        "shock": shock,
                        "conflict": conflict,
                        "stage": stage,
                    },
                },
                "output_instructions": visual_state,
            }
        )

    except Exception as e:
        print(f"API Error: {e}")
        return (
            jsonify(
                {"error": f"Internal Server Error during trigger processing: {str(e)}"}
            ),
            500,
        )


if __name__ == "__main__":
    # 개발 환경에서 테스트용으로 실행 가능하도록 설정
    app.run(debug=True, port=5001)

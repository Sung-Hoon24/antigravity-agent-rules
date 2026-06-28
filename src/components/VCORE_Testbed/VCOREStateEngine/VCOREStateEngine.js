/**
 * @description VCOREStateEngine: 사운드 파라미터 변화에 따른 콘텐츠의 논리적 상태(State)와 다음 액션을 결정합니다.
 * 이 부분이 비즈니스 로직의 핵심입니다. (데이터 흐름 검증 지점)
 */
const processSoundParameters = (currentParams, previousState) => {
    let newStateName = 'Stable'; // 기본값: 안정적 상태
    let anomalyActive = false;

    // --- 1. [V-CORE 로직] 파라미터 변화 기반의 상태 결정 ---
    // 예시: Amplitude가 급격히 낮아지거나 (정보 손실), Frequency가 특정 임계치를 벗어날 때(충돌)는 'Knowledge Gap' 발생으로 정의합니다.
    if (currentParams.amplitude < 0.4 && currentParams.frequency > 350) {
        newStateName = 'KnowledgeGap_Triggered'; // 지식적 결핍 유발 상태로 강제 전환
        anomalyActive = true;
    } else if (Math.abs(currentParams.amplitude - previousState.currentParams.amplitude) > 0.3 && Math.abs(currentParams.frequency - previousState.currentParams.frequency) > 50) {
         // 파라미터 변화의 급격함이 클 경우: 시스템 오류 감지
        newStateName = 'AnomalySignal_Detected';
        anomalyActive = true;
    } else if (newStateName === 'KnowledgeGap_Triggered' && currentParams.amplitude > 0.7) {
         // Gap 이후, 다시 정보가 주입될 때: 해결 단계 진입 시도
        newStateName = 'ResolutionAttempt';
        anomalyActive = false;
    } else {
        newStateName = 'Stable'; // 정상적인 논리 흐름 유지
    }

    return {
        stateName: newStateName,
        currentParams: currentParams,
        anomalyActive: anomalyActive,
        // 필요하다면 다음 CTA를 결정하는 로직도 여기에 추가됨
    };
};

export default { processSoundParameters };

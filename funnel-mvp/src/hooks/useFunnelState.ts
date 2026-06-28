import { useState, useCallback } from 'react';

// 💡 State Machine 정의: Funnel의 모든 논리적 상태를 명확히 합니다.
type FunnelState = 'HOOK' | 'KNOWLEDGE_GAP' | 'TENSION_BUILDUP' | 'CTA_GATE' | 'COMPLETE';

interface FunnelContext {
    currentState: FunnelState;
    setCurrentState: (state: FunnelState, duration?: number) => Promise<void>;
    // 사용자의 행동 데이터를 수집하는 함수 추가 (LTV 추적 목적)
    logUserAction: (actionType: string, detail: any) => void;
}

export const useFunnelState = () => {
    const [state, setState] = useState<FunnelState>('HOOK');

    // State Transition 로직 정의
    const setCurrentState = useCallback(async (newState: FunnelState, durationSeconds: number = 0) => {
        console.log(`[STATE TRANSITION] -> ${newState}`);
        setState(newState);

        if (durationSeconds > 0) {
            await new Promise(resolve => setTimeout(resolve, durationSeconds * 1000));
        }
    }, []);

    // 사용자 행동 로그 기록 (데이터 수집의 핵심)
    const logUserAction = useCallback((actionType: string, detail: any) => {
        console.log(`[USER ACTION LOG] Type: ${actionType}, Detail:`, detail);
        // 실제 환경에서는 API 호출을 통해 데이터를 전송해야 함
    }, []);

    return { currentState: state, setCurrentState, logUserAction };
};

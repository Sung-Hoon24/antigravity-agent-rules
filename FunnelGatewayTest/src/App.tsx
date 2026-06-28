import React, { useState, useEffect } from 'react';
import FunnelGatewayAsset from './components/FunnelGatewayAsset';
// 임시로 StateMachineContext를 App.tsx에 통합합니다. 실제로는 Context Provider에서 처리됩니다.

const App = () => {
    const [state, setState] = useState('IDLE');
    const [timeElapsedMs, setTimeElapsedMs] = useState(0);

    useEffect(() => {
        // 시뮬레이션 타이머: 시간 흐름을 강제로 구현합니다.
        const timer = setInterval(() => {
            setTimeElapsedMs(prev => prev + 100); // 100ms 간격으로 시간 증가
        }, 100);

        return () => clearInterval(timer);
    }, []);

    // 상태 전이 로직 (가장 중요한 비즈니스 로직)
    const handleStateChange = (newState, targetTimeMs) => {
        setState(newState);
        console.log(`[STATE CHANGE] State transitioned to: ${newState} at T+${targetTimeMs}ms.`);
    };

    // 시뮬레이션 버튼 핸들러 (테스트용 액션 트리거)
    const handleTestTrigger = () => {
        if (timeElapsedMs > 250 && timeElapsedMs < 600) {
            // T+320ms ~ T+510ms 구간 진입 시도
            handleStateChange('GLITCH_TRANSITION', Math.floor(Math.random() * 200) + 320);
        } else if (timeElapsedMs >= 600) {
             // 다음 단계로 강제 전이
            handleStateChange('RESOLUTION', timeElapsedMs);
        } else {
             handleStateChange('HOOK_ACTIVE', timeElapsedMs);
        }
    };

    return (
        <div style={{ padding: '20px' }}>
            <h1>Funnel Gateway State Machine Prototype</h1>
            <p>Current Time Elapsed: {timeElapsedMs}ms | Current State: <strong>{state}</strong></p>
            <button onClick={handleTestTrigger}>Simulate Next State (Manual Trigger)</button>

            <div style={{ margin: '30px', border: '1px solid #ccc', padding: '20px' }}>
                <FunnelGatewayAsset state={state} timeElapsedMs={timeElapsedMs} />
            </div>
        </div>
    );
};

export default App;

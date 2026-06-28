// Information Gap (Module A) - Skeletal Component
import React, { useState } from 'react';
import './InformationGapModuleA.css';

interface State {
    isGapDetected: boolean; // 지식 간극 감지 여부
    gapData: string | null;  // 손실된 데이터 또는 질문
}

const InformationGapModuleA: React.FC = () => {
    const [state, setState] = useState<State>({ isGapDetected: false, gapData: null });

    // 🚨 이 부분에 Designer가 제공할 '오류/데이터 손실' 로직이 들어갑니다.
    const handleTransitionFailure = (errorDetail: string) => {
        console.error("⚠️ State Transition Failed:", errorDetail);
        setState({ isGapDetected: true, gapData: errorDetail });
        // 실제로는 애니메이션 및 뷰 상태 변경 로직 호출
    };

    return (
        <div className="module-a-container">
            <h2>Module A: Information Gap</h2>
            {state.isGapDetected ? (
                <div className={`error-state error-${state.gapData.includes('MISSING') ? 'data' : 'logic'}`}>
                    <p>🚨 경고: 데이터 손실 발생</p>
                    <pre>{state.gapData}</pre>
                    <p>(상태 머신 실패 처리 로직 실행 중...)</p>
                </div>
            ) : (
                <>
                    <div className="content-placeholder">진행 중인 콘텐츠 내용...</div>
                    <button onClick={() => handleTransitionFailure("MISSING: Module A transition requires 'Academic_Level' parameter.")}>
                        [테스트] 간극 유발 시도
                    </button>
                </>
            )}
        </div>
    );
};

export default InformationGapModuleA;

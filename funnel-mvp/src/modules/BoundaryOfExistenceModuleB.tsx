// Boundary of Existence (Module B) - Skeletal Component
import React, { useState } from 'react';
import './BoundaryOfExistenceModuleB.css';

interface State {
    isBoundaryReached: boolean; // 경계 도달 여부
    errorDetail: string | null;  // 오류 상세 내용
}

const BoundaryOfExistenceModuleB: React.FC = () => {
    const [state, setState] = useState<State>({ isBoundaryReached: false, errorDetail: null });

    // 🚨 이 부분에 Designer가 제공할 '오류/데이터 손실' 로직이 들어갑니다.
    const handleTransitionFailure = (errorDetail: string) => {
        console.error("⚠️ Boundary Transition Failed:", errorDetail);
        setState({ isBoundaryReached: true, errorDetail });
    };

    return (
        <div className="module-b-container">
            <h2>Module B: Boundary of Existence</h2>
            {state.isBoundaryReached ? (
                <div className={`error-state error-${state.errorDetail.includes('NON_EXIST') ? 'data' : 'logic'}`}>
                    <p>🌌 존재의 경계 초과 오류</p>
                    <pre>{state.errorDetail}</pre>
                    <p>(시스템 로직이 비논리적 전환점을 감지했습니다.)</p>
                </div>
            ) : (
                <>
                    <div className="content-placeholder">경계에 근접하는 콘텐츠 내용...</div>
                    <button onClick={() => handleTransitionFailure("NON_EXIST: Cannot proceed without 'Cognitive_Bias' validation.")}>
                        [테스트] 경계 초과 시도
                    </button>
                </>
            )}
        </div>
    );
};

export default BoundaryOfExistenceModuleB;

import React, { useState, useEffect, useCallback } from 'react';
import * as gsap from 'gsap';
// NOTE: Canvas API는 실제 구현 시 별도의 hook이나 Context로 분리해야 합니다. 여기서는 로직 흐름만 정의합니다.

/**
 * @typedef {'HOOK' | 'KNOWLEDGE_GAP' | 'TENSION_PEAK' | 'CTA_GATE'} FunnelState
 */

// --- 서브 컴포넌트 임포트 (실제 파일 경로를 가정) ---
import { KnowledgeGapModule } from './KnowledgeGapModule';
import { ConfirmationBiasModule } from './ConfirmationBiasModule'; // 이미 생성된 모듈 활용
import { CTAGateWidget } from './CTAGateWidget';

/**
 * 메인 비디오 Funnel 상태 머신 컴포넌트.
 * Hook -> Gap -> Peak Tension -> CTA Gate 순서로 사용자 경험을 제어합니다.
 */
const VideoFunnelStateMachine = () => {
    const [currentState, setCurrentState] = useState('HOOK');
    const [timeElapsed, setTimeElapsed] = useState(0);

    // 1. 상태 전환 로직 (핵심)
    const handleAdvanceState = useCallback((newState) => {
        console.log(`[System]: State Transitioning from ${currentState} to ${newState}`);
        setCurrentState(newState);
        // GSAP을 사용한 시각적 전이점 애니메이션 시작
        gsap.timeline()
            .to(".container", { opacity: 0, duration: 0.5 }) // 기존 컴포넌트 Fade Out
            .call(() => {
                setTimeout(() => {
                    // 새 상태의 내용 로드 (여기서 실제 모듈을 렌더링)
                    document.getElementById('funnel-container').innerHTML = '';
                    const newComponent = renderModule(newState);
                    document.getElementById('funnel-container').appendChild(newComponent);
                }, 300); // 충분한 시간차를 두어 부드러운 전환 구현
            })
            .to(".container", { opacity: 1, duration: 0.5 });
    }, [currentState]);

    // 모듈별 컴포넌트 렌더링 함수 (가상)
    const renderModule = (state) => {
        let Component;
        switch (state) {
            case 'HOOK':
                Component = <div className="module"><h2>[Hook] 논리적 역설 제시</h2><p>시청자의 주의를 사로잡는 초기 정보 폭격 구간입니다.</p></div>;
                break;
            case 'KNOWLEDGE_GAP':
                // 지식적 간극 모듈이 활성화되면, 다음 단계 진행 버튼을 비활성화하고 타이머만 보이게 할 수 있음.
                Component = <KnowledgeGapModule />;
                break;
            case 'TENSION_PEAK':
                // 이 구간에서 Canvas API 기반의 배경 레이어(필터링 오염 효과)가 최고조에 달해야 함.
                Component = <div className="module"><h2>[Tension Peak] 데이터 실패와 지식 단절</h2><p>사용자가 가장 큰 인지 부조화를 느끼는 시점입니다.</p></div>;
                break;
            case 'CTA_GATE':
                // 최종 상품 Funnel로의 진입점. 모든 것이 여기서 수렴합니다.
                Component = <CTAGateWidget />;
                break;
        }
        return Component;
    };

    // 상태별 다음 단계 진행 핸들러
    const handleTransitionLogic = () => {
        if (currentState === 'HOOK') {
            handleAdvanceState('KNOWLEDGE_GAP');
        } else if (currentState === 'KNOWLEDGE_GAP') {
             // KnowledgeGapModule 내부에서 특정 조건을 만족해야만 Peak로 이동 가능하도록 설계할 수 있음.
            setTimeout(() => handleAdvanceState('TENSION_PEAK'), 2000);
        } else if (currentState === 'TENSION_PEAK') {
            handleAdvanceState('CTA_GATE');
        }
    };

    return (
        <div className="container" id="funnel-container" style={{ opacity: 1 }}>
             <h1>Funnel Prototype Status: {currentState}</h1>
             {/* 실제 모듈은 내부에서 renderModule에 의해 삽입됩니다. */}
             <p>현재 상태를 기반으로 시각적 전환이 일어납니다.</p>
             <button onClick={handleTransitionLogic} disabled={currentState === 'CTA_GATE'}>
                다음 논리 단계로 진행 ({currentState} -> {['HOOK', 'KNOWLEDGE_GAP', 'TENSION_PEAK', 'CTA_GATE'][Object.keys(VideoFunnelStateMachine).indexOf('funnelState')]})
            </button>
        </div>
    );
};

export default VideoFunnelStateMachine;

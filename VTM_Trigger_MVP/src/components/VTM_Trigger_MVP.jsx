import React, { useState, useEffect, useCallback } from 'react';
/* Stylesheet import (실제 프로젝트에서는 패키지 방식으로 관리) */
// import './styles/Variables.css';

/**
 * VTM Trigger Module MVP Component
 * @param {object} props - Props for controlling the module state and parameters.
 * @param {number} props.initialLoad - 초기 Cognitive Load 값 (0-10).
 * @param {function} props.onTriggered - 트igger 발생 시 호출할 콜백 함수 (예: 다음 콘텐츠 API 요청).
 */
const VTM_Trigger_MVP = ({ initialLoad, onTriggered }) => {
    // 1. State Management for Parameters
    const [state, setState] = useState({
        cognitiveLoad: initialLoad, // 핵심 제어 변수
        archiveDepth: 0.1 + (initialLoad / 20), // Load에 비례하여 Depth 초기화
        isTriggered: false, // 트리거 발생 여부 플래그
    });

    // 2. Effect Hook for Parameter Application & Simulation Logic
    useEffect(() => {
        // CSS 변수 업데이트 로직 (파라미터 기반 스타일링)
        document.documentElement.style.setProperty('--cognitive-load', state.cognitiveLoad);
        document.documentElement.style.setProperty('--archive-depth', state.archiveDepth);

        let triggerTimeout;

        // 시뮬레이션: 5초 동안 Cognitive Load를 점진적으로 증가시키고 임계치를 체크합니다.
        const interval = setInterval(() => {
            setState(prev => {
                if (prev.cognitiveLoad >= 10 || prev.isTriggered) return prev; // 최대치 도달 또는 이미 발동

                // 다음 로드 계산 (느리게 증가하도록 조정)
                const newLoad = Math.min(10, prev.cognitiveLoad + Math.random() * 0.5);

                if (!prev.isTriggered && newLoad >= 8.5) { // 임계치 설정: 8.5 (패러독스 발생 지점)
                    clearInterval(interval);
                    // 트igger 발동 처리
                    setState(p => ({ ...p, isTriggered: true }));

                    // 부모 컴포넌트에 이벤트를 전달하여 다음 액션 유도
                    if (onTriggered) {
                        onTriggered(newLoad);
                    }

                } else {
                    return { ...prev, cognitiveLoad: newLoad };
                }
            });
        }, 1000); // 매 초마다 로드 업데이트 시뮬레이션

        // Cleanup function
        return () => clearInterval(interval);

    }, [state.cognitiveLoad, state.isTriggered, onTriggered]);


    // 3. JSX Rendering (MVP Component)
    return (
        <div className="vtm-container" style={{ opacity: state.isTriggered ? '1' : '0.9' }}>
            {/* Background Layer - Depth에 따라 변화 */}
            <div className="archive-overlay"></div>

            {/* 데이터 흐름 시각화 (항상 재생) */}
            <div className="data-stream"></div>

            {/* 핵심 모듈 컴포넌트 */}
            <div
                className={`vtm-module ${state.isTriggered ? 'triggered' : ''}`}
                style={{
                    // 현재 Load 값에 따라 색상 강조 정도를 시각적으로 반영할 수 있음
                    backgroundColor: state.isTriggered ? 'rgba(255, 193, 7, 0.1)' : 'transparent',
                    boxShadow: `0 0 ${state.cognitiveLoad * 0.5}px rgba(255, 193, 7, ${state.cognitiveLoad / 10})` // Load가 높을수록 그림자 증가
                }}
            >
                {/* 현재 상태 정보 (개발용 디버그 UI) */}
                <p style={{ fontSize: '0.8em', color: '#aaa' }}>
                    [DEBUG] C_Load: {state.cognitiveLoad.toFixed(2)} | Depth: {(state.archiveDepth * 100).toFixed(0)}%
                </p>

                {/* 패러독스 메시지 (트리거 발생 시 표시) */}
                <h1 className="paradox-text" style={{ transition: 'color var(--transition-speed)' }}>
                    {state.isTriggered ? "⚠️ PARADOX DETECTED ⚠️" : "ARCHIVE ACCESSING..."}
                </h1>

                {/* 핵심 논지 전달 메시지 */}
                <p className="vtm-message">
                    {state.isTriggered
                        ? "Critical Information Gap Detected. Deep Dive Required."
                        : "Processing Existential Data Stream..."}
                </p>

                {/* 사용자 액션 유도 (개발 단계에서는 주석 처리) */}
                {!state.isTriggered && <button disabled className="cta-button">Wait for Trigger...</button>}
            </div>
        </div>
    );
};

export default VTM_Trigger_MVP;

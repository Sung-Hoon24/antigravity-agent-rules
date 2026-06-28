import React, { useState, useCallback } from 'react';
import './VideoFunnelStateMachine.css'; // CSS 파일을 가정합니다.

// ====================================================
// 🚨 PLACEHOLDER API & UTILITIES (실제 구현 시 대체 필요)
// Deep Indigo/Glitch Cyan 필터링 및 모션 연출을 위한 가상 함수입니다.
const applyDeepIndigoFilter = (elementId, durationMs) => {
  console.log(`[API CALL] Applying Deep Indigo filter to #${elementId} for ${durationMs}ms.`);
  // 실제로는 WebGL이나 CSS 애니메이션 API를 사용합니다.
};

const applyGlitchCyanFilter = (elementId, intensityLevel) => {
  console.log(`[API CALL] Applying Glitch Cyan filter to #${elementId} with intensity ${intensityLevel}.`);
}

// State Machine 정의: Funnel의 논리적 단계를 정의합니다.
const STATES = {
  HOOK: 'hook', // 1. 시청자 주의 집중 (Attention Grab)
  SETUP: 'setup', // 2. 배경 지식 제공 및 권위 확립 (Authority Building)
  DEFICIT_TRIGGER: 'deficit_trigger', // 3. 논리적 결핍 발생 (Systemic Deficiency!) - Peak Tension Zone
  CTA_GATE: 'cta_gate' // 4. 강제 이탈/다음 단계 유도 (Forced Transition)
};

/**
 * 메인 Funnel State Machine 컴포넌트
 * @param {string} platform - 'youtube' 또는 'instagram'
 */
const VideoFunnelStateMachine = ({ platform }) => {
  const [currentState, setCurrentState] = useState(STATES.HOOK);
  const [isDeficitActive, setIsDeficitActive] = useState(false);

  // 상태 전환 로직 (이것이 핵심 State Management입니다)
  const transitionTo = useCallback((newState) => {
    if (!Object.values(STATES).includes(newState)) return;
    console.log(`[State Change]: ${currentState} -> ${newState}`);
    setCurrentState(newState);
  }, [currentState]);

  // -------------------- 핵심 이벤트 핸들러 --------------------

  const handleDeficiencyActivation = () => {
    if (currentState !== STATES.SETUP) return;

    setIsDeficitActive(true);
    applyDeepIndigoFilter('main-content', 500); // Deep Indigo Start
    applyGlitchCyanFilter('main-content', 'High'); // Glitch Cyan Start

    // T+1200ms: Peak Tension Zone (가장 중요한 타이밍)
    setTimeout(() => {
      console.log("[SYSTEM ALERT] DEFICIT PEAK ACHIEVED!");
      transitionTo(STATES.DEFICIT_TRIGGER);
    }, 1200);
  };

  const handleCtaClick = () => {
    if (currentState !== STATES.CTA_GATE) return;
    // 실제 LTV 추적 로직 및 다음 Funnel 페이지 이동을 여기서 처리합니다.
    console.log(`[LTV TRACKING] CTA Click Detected on ${platform}. Transitioning to Paid Gateway.`);
  };

  // -------------------- 렌더링 로직 (Current State에 따라 UI 변화) --------------------

  const renderContent = () => {
    switch (currentState) {
      case STATES.HOOK:
        return <div className="state-hook">Hook Content: 시청자의 주의를 사로잡는 강력한 질문 던지기...</div>;

      case STATES.SETUP:
        // A-POINT 직전, 결핍 유도를 위해 버튼을 활성화합니다.
        const setupAction = (
          <button
            onClick={handleDeficiencyActivation}
            className="btn-activate"
          >
            🤔 논리적 공백 확인하기 (A-Point)
          </button>
        );
        return <div className="state-setup">Setup Content: 권위 확립. 모든 것이 완벽해 보입니다... {setupAction}</div>;

      case STATES.DEFICIT_TRIGGER:
        // 가장 긴장되는 순간, 시각적 결핍을 극대화합니다.
        const deficitStyle = isDeficitActive ? 'glitch-active' : '';
        return (
          <div className={`state-deficit ${deficitStyle}`}>
            💥 시스템 오류 연출! (Deep Indigo/Glitch Cyan Max) <br/>
            [T+1200ms] 논리적 결핍(Deficiency) 발생. 당신이 놓친 무언가가 있다.
          </div>
        );

      case STATES.CTA_GATE:
        // Funnel Gateway, 다음 행동을 강제합니다.
        return (
          <div className="state-cta">
            ✅ 이제 필요한 것은 이 결핍을 채우는 지식입니다.<br/>
            {/* 사용자의 시선을 중앙 CTA 영역으로 흡입시키는 로직 */}
            <button onClick={handleCtaClick} className="btn-final">다음 단계로 이동 (클릭)</button>
          </div>
        );

      default:
        return <div className="state-loading">Loading Funnel...</div>;
    }
  };

  return (
    <div className={`funnel-container ${platform}`}>
      <h1>Funnel State Machine ({platform.toUpperCase()})</h1>
      <p>현재 상태: <strong>{currentState}</strong></p>
      <hr />
      <div id="main-content" className={isDeficitActive ? 'glitch-active' : ''}>
        {renderContent()}
      </div>

      {/* 디버깅/테스트용 컨트롤 */}
      <div className="controls">
        <button onClick={() => transitionTo(STATES.HOOK)}>Test: HOOK</button>
        <button onClick={() => transitionTo(STATES.SETUP)}>Test: SETUP</button>
        <button onClick={() => transitionTo(STATES.DEFICIT_TRIGGER)}>Test: DEFICIT (강제)</button>
        <button onClick={() => transitionTo(STATES.CTA_GATE)}>Test: CTA GATE</button>
      </div>
    </div>
  );
};

export default VideoFunnelStateMachine;

import React, { useState, useCallback } from 'react';
import useTimeTrigger from './hooks/useTimeTrigger';
import styled from 'styled-components';

// --------------------- Styled Components (UI 정의) ----------------------
const GatewayContainer = styled.div`
  padding: 40px;
  border: 3px solid ${props => props.state === 'GAP' ? '#5c00ff' : '#1e90ff'}; /* Deep Indigo */
  background-color: ${props => props.state === 'GLITCH' ? '#0a0a0f' : '#ffffff'};
  min-height: 300px;
  transition: all 0.5s ease-in-out;
`;

const StatusDisplay = styled.p`
    font-size: 1.2em;
    margin-bottom: 20px;
    color: ${props => props.isActive ? 'red' : 'black'};
`;

// --------------------- State Machine Logic ----------------------
const FUNNEL_STATES = {
  HOOK: 'HOOK',             // 초기 상태: 흥미 유발 (T=0ms)
  DISCOVERY: 'DISCOVERY',   // 권위 제시 단계
  A_POINT_START: 'A_POINT_START', // 결핍 발생 직전 지연 구간
  GAP: 'GAP',               // 핵심: Knowledge Gap 발생 및 Funnel Gateway 활성화 (T=Xms)
  DECISION: 'DECISION'      // 최종 CTA/결정 단계
};

const initialTimestamp = Date.now(); // 시뮬레이션 시작 시간
const A_POINT_TRIGGER_TIME = initialTimestamp + 3000; // 가상으로 3초 후 Gap 발생 가정 (실제로는 v3.0 타임라인 기반)

function FunnelStateMachine() {
  const [currentState, setCurrentState] = useState(FUNNEL_STATES.HOOK);
  const [isGapActive, setIsGapActive] = useState(false);

  // 훅을 사용하여 A-POINT 발생 시점 검증 (핵심 기능)
  const gapIsTriggered = useTimeTrigger(A_POINT_TRIGGER_TIME, 50); // ±50ms 정밀 체크

  const handleTransition = useCallback((newState) => {
    if (newState === FUNNEL_STATES.GAP && !gapIsTriggered) {
      console.warn("⚠️ [ERROR] Funnel Gateway가 작동하지 않습니다. A-POINT 타이밍을 기다려야 합니다.");
      return;
    }

    setCurrentState(newState);
    // 상태 변화에 따른 부수 효과 및 로직 호출 (예: 애니메이션 트리거, API 호출)
    if (newState === FUNNEL_STATES.GAP) {
        setIsGapActive(true);
        console.log("✅ [SYSTEM] Funnel Gateway 활성화: 지적 결핍 발생.");
    } else if (newState !== FUNNEL_STATES.HOOK) {
        setIsGapActive(false);
        console.log(`⚙️ [SYSTEM] 상태 전이 완료: ${newState}`);
    }

  }, [gapIsTriggered]);


  // --------------------- Render Logic ----------------------
  return (
    <GatewayContainer state={currentState}>
      <h2>Funnel Gateway MVP Test</h2>
      <StatusDisplay isActive={isGapActive} />
      <p>현재 상태: <strong>{currentState.replace('_', ' ')}</strong></p>

      {/* 디버깅 및 테스트용 버튼 */}
      <div>
        <button onClick={() => handleTransition(FUNNEL_STATES.HOOK)} disabled={currentState === FUNNEL_STATES.HOOK}>1. HOOK (시작)</button>
        <button onClick={() => handleTransition(FUNNEL_STATES.DISCOVERY)} disabled={currentState === FUNNEL_STATES.DISCOVERY || gapIsTriggered}>2. DISCOVERY</button>
        {/* A-POINT는 타이밍에 의해 자동 전이되거나, 타이머가 활성화된 경우만 작동해야 함 */}
        <button onClick={() => handleTransition(FUNNEL_STATES.GAP)} disabled={currentState === FUNNEL_STATES.GAP || gapIsTriggered}>3. A-POINT (Gap)</button>
        {/* Gap 상태에서만 다음 단계로 진입 가능 */}
        <button onClick={() => handleTransition(FUNNEL_STATES.DECISION)} disabled={!(currentState === FUNNEL_STATES.GAP && isGapActive)}>4. CTA/결정</button>
      </div>

      <p style={{marginTop: '30px', fontSize: '0.9em'}}>* A-POINT (Gap) 진입은 타이밍(T+3s, ±50ms)이 검증되어야만 다음 단계가 가능합니다.</p>
    </GatewayContainer>
  );
}

export default FunnelStateMachine;

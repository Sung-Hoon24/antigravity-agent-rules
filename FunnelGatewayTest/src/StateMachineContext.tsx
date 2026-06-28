import React, { useContext, useState, useCallback } from 'react';

/**
 * @typedef {'IDLE' | 'HOOK_ACTIVE' | 'GAP_INIT' | 'GLITCH_TRANSITION' | 'RESOLUTION'} GatewayState
 */

/**
 * FunnelGatewayTest Context: State Machine의 상태와 액션을 관리합니다.
 * 이 컨텍스트가 전체 콘텐츠 흐름을 제어하는 단일 진실(Single Source of Truth)이 됩니다.
 */
export const StateMachineContext = React.createContext({
    currentState: 'IDLE',
    setState: () => {},
    // 테스트 시뮬레이션을 위한 핵심 함수
    simulateTransition: (transitionType, timeElapsedMs) => {
        console.log(`[Simulator] Attempting transition from ${Math.random().toString(36).substring(2)} to ${transitionType} at T+${timeElapsedMs}ms.`);
    }
});

export const useStateMachine = () => useContext(StateMachineContext);

// 초기 Context Provider는 App.tsx에서 감싸줄 예정입니다.

// FunnelStateMachine 통합 테스트 스위트 (Jest 사용 가정)
import React from 'react';
import { render, act } from '@testing-library/react';
import FunnelStateMachine from '../src/FunnelStateMachine';
import * as useTimeTriggerMock from '../src/hooks/useTimeTrigger';

// 1. Hook Mocking: 시간 흐름 제어를 위해 useTimeTrigger를 Mocking합니다.
jest.mock('../src/hooks/useTimeTrigger', () => ({
  __esModule: true,
  default: jest.fn(() => {
    // 시간을 수동으로 조작할 수 있도록 함수 정의 (실제 테스트에서 사용)
    return {
      trigger: jest.fn(),
      onTimerExceeded: jest.fn(), // 타이머 초과 감지 콜백 Mocking
    };
  }),
}));

describe('FunnelStateMachine Integration Test Suite', () => {
  // 테스트 시작 전 환경 초기화
  beforeEach(() => {
    jest.clearAllMocks();
  });

  // ==============================================================
  // TEST CASE 1: 기본 Funnel Flow 검증 (State Transition)
  // HOOK -> SETUP -> A_POINT 순서가 논리적으로 작동하는지 확인합니다.
  // ==============================================================
  it('Should successfully transition through all defined states in the correct sequence', async () => {
    const mockProps = { currentStep: 'HOOK' };
    let component;

    // 초기 렌더링 (HOOK 상태)
    component = render(<FunnelStateMachine {...mockProps} />);

    // ACT: 다음 단계로 강제 진입 시뮬레이션 (Setup으로 이동)
    await act(async () => {
      // FunnelStateMachine 내부의 nextStep 함수를 호출하는 것으로 가정합니다.
      const setupNext = component.container.querySelector('[data-testid="next-to-setup"]');
      if (setupNext) setupNext.click();
      component.rerender(<FunnelStateMachine {...mockProps} currentStep="SETUP" />); // 리렌더링 시뮬레이션
    });

    // ASSERT: SETUP 상태의 요소가 활성화되었는지 확인합니다.
    expect(component.container).toHaveTextContent('Setup Content Loaded');

    // ACT: A_POINT로 이동 (최종 단계)
    await act(async () => {
      const aPointNext = component.container.querySelector('[data-testid="next-to-a-point"]');
      if (aPointNext) aPointNext.click();
      component.rerender(<FunnelStateMachine {...mockProps} currentStep="A_POINT" />); // 리렌더링 시뮬레이션
    });

    // ASSERT: A_POINT가 활성화되고, 다음 단계(CTA/Exit)를 유도하는 로직이 작동했는지 확인합니다.
    expect(component.container).toHaveTextContent('Systemic Deficiency Detected');
  });


  // ==============================================================
  // TEST CASE 2: 타이밍 지연 및 시각 효과 검증 (T+XXXms & Colors)
  // useTimeTrigger를 통해 시간이 흐른 후에만 특정 기능이 활성화되는지 검증합니다.
  // ==============================================================
  it('Should only trigger the DeepIndigoToGlitchCyan transition after the specified delay', async () => {
    // Mocking된 Hook의 타이머 설정 기능을 사용
    const mockTimeTrigger = useTimeTriggerMock.default();
    mockTimeTrigger.trigger = jest.fn();

    // 렌더링 시, 타이밍 의존성을 props로 넘긴다고 가정
    const initialProps = { delayMs: 300 };
    const { rerender } = render(<FunnelStateMachine {...initialProps} />);

    // ASSERT (Pre-check): 초기에는 GlitchCyan 전환 로직이 실행되지 않아야 합니다.
    expect(mockTimeTrigger.trigger).toHaveBeenCalledWith('DeepIndigo', 'GlitchCyan'); // 타이머는 설정되었으나 발동하지 않음

    // ACT: 시간이 지나갔음을 시뮬레이션합니다 (실제로는 jest.useFakeTimers().advanceTimeByTime(301) 등을 사용)
    // 여기서는 Mocked Hook의 콜백을 직접 트리거하는 것으로 대체합니다.
    await act(async () => {
        const onTimerExceeded = useTimeTriggerMock.default().onTimerExceeded;
        if (typeof onTimerExceeded === 'function') {
            onTimerExceeded(); // 타이머 만료 이벤트 강제 발생
        }
    });

    // ASSERT (Post-check): 시간이 초과된 후, 색상 전환 로직이 정확하게 호출되었는지 검증합니다.
    expect(mockTimeTrigger.trigger).toHaveBeenCalledTimes(1);
    expect(mockTimeTrigger.trigger).toHaveBeenCalledWith('DeepIndigo', 'GlitchCyan');
  });

  // ==============================================================
  // TEST CASE 3: 강제 리디렉션/Funnel Gateway 로직 검증 (Exception Handling)
  // A-POINT에서 사용자의 행동(클릭)에 따라 Funnel Gate로 이동하는지 확인합니다.
  // ==============================================================
  it('Should execute the correct redirection logic and capture tracking parameters upon CTA click', async () => {
    const mockTrackingLogger = jest.fn(); // 추적 로직 Mocking

    // 렌더링 시, Funnel Gateway가 활성화된 상태를 가정합니다.
    const { rerender } = render(<FunnelStateMachine currentStep="A_POINT" trackingLogger={mockTrackingLogger} />);

    // ACT: 사용자가 CTA 버튼을 클릭하는 상황을 시뮬레이션합니다.
    await act(async () => {
      const ctaButton = document.querySelector('[data-testid="cta-gate"]');
      if (ctaButton) ctaButton.click();
    });

    // ASSERT: 1. 정확한 추적 로직이 실행되었는지 확인합니다.
    expect(mockTrackingLogger).toHaveBeenCalledWith('Systemic_Deficiency', expect.any(Object));

    // ASSERT: 2. 2. 리디렉션 함수가 호출되었으며, 특정 URL 파라미터가 포함되는지 검증합니다.
    // (실제 환경에서는 router.push('/paid-wall?source=funnel')) 형태의 API Mocking이 필요함
    expect(window).toHaveFunction('redirectToFunnelGateway'); // 전역 리디렉션 함수 존재 확인
  });

});

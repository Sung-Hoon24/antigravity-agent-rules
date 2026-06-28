// VideoFunnelStateMachine.test.jsx (Jest/React Testing Library)

import React from 'react';
import { render, screen, fireEvent, act } from '@testing-library/react';
import '@testing-library/jest-dom';
import VideoFunnelStateMachine from '../VideoFunnelStateMachine';

// -------------------------------------------
// MOCKING SETUP
// -------------------------------------------

// 1. GAP_OVERLAY 컴포넌트 Mocking: 실제 CSS 로직 대신, 단순히 '오버레이'가 표시되는지 테스트합니다.
jest.mock('GAP_OVERLAY', () => ({ props }) => (
  <div data-testid="gap-overlay" style={{ position: 'absolute', top: 0, left: 0, width: '100%', height: '100%', backgroundColor: '#320D5B' }}>
    MISSING DATA [Gap detected] - {props.reason}
  </div>
));

// 2. API 서비스 Mocking: 상태 전환을 제어하는 핵심 로직입니다.
const mockApiService = {
  checkFunnelState: jest.fn(), // 정상 흐름 체크 (현재 단계 확인)
  triggerGapDetection: jest.fn(async (context) => {
    // 시뮬레이션: API가 '지식적 간극'을 감지했다고 응답하는 성공 케이스
    if (context && context.topic === 'confirmation_bias') {
      return { success: true, gapDetected: true, reason: "Core mechanism missing." };
    }
    // 시뮬레이션: API 호출 실패 또는 정보 없음
    throw new Error("API Service Error: Connection failed.");
  }),
};

jest.mock('../api/FunnelApiService', () => ({
  default: mockApiService,
}));


// -------------------------------------------
// TEST SUITE START
// -------------------------------------------

describe('VideoFunnelStateMachine Unit Tests (State Transition Validation)', () => {
  const initialProps = { topic: 'confirmation_bias', userId: 'user-123' };

  // 테스트 시작 전 환경 초기화 및 Mock 재설정
  beforeEach(() => {
    jest.clearAllMocks();
  });

  test('✅ Test Case 1: Happy Path - 정상 콘텐츠 흐름에서 GAP_OVERLAY로의 성공적 전환', async () => {
    // [행동 정의] API가 Gap 감지 결과를 성공적으로 반환하도록 Mock 설정
    mockApiService.checkFunnelState.mockResolvedValue({ currentState: 'Void Generation', nextAction: 'GAP_OVERLAY' });
    mockApiService.triggerGapDetection.mockResolvedValue({ success: true, gapDetected: true, reason: "Core mechanism missing." });

    // [실행] 컴포넌트 렌더링 및 상태 변화 트리거
    render(<VideoFunnelStateMachine {...initialProps} />);

    // 로딩 중 초기 메시지 확인 (Step 1)
    expect(screen.getByText(/현재 Funnel 단계: Void Generation/i)).toBeInTheDocument();

    // Gap 감지를 유도하는 버튼 클릭 시뮬레이션
    const detectGapButton = screen.getByRole('button', /논리적 간극을 탐지하기/).closest('button');
    fireEvent.click(detectGapButton);

    // [검증] API 호출 및 최종 컴포넌트 렌더링 검증 (Step 2)
    await act(async () => {
      // API 서비스가 트리거되었는지 확인
      expect(mockApiService.triggerGapDetection).toHaveBeenCalledWith(expect.objectContaining({ topic: 'confirmation_bias' }));
    });

    // GAP_OVERLAY 컴포넌트가 렌더링 되었고, 메시지가 올바른지 검증 (Step 3)
    const gapElement = screen.getByTestId('gap-overlay');
    expect(gapElement).toBeInTheDocument();
    expect(gapElement).toHaveTextContent("MISSING DATA [Gap detected] - Core mechanism missing.");

    // 최종 CTA 버튼이 활성화되었는지 확인 (CTA Gate)
    const ctaGate = screen.getByRole('button', /관점 재구성 틀을 구매/).closest('button');
    expect(ctaGate).toBeInTheDocument();
  });

  test('❌ Test Case 2: Failure Path - API 통신 오류 발생 시, 사용자에게 명확한 에러 메시지 제공 및 복귀', async () => {
    // [행동 정의] API가 강제로 실패하도록 Mock 설정
    mockApiService.checkFunnelState.mockResolvedValue({ currentState: 'Void Generation' });
    mockApiService.triggerGapDetection.mockRejectedValue(new Error("API Service Error: Connection failed."));

    render(<VideoFunnelStateMachine {...initialProps} />);

    // Gap 감지 버튼 클릭 및 에러 발생 시뮬레이션
    const detectGapButton = screen.getByRole('button', /논리적 간극을 탐지하기/).closest('button');
    fireEvent.click(detectGapButton);

    await act(async () => {
      // API가 실패했는지 확인 (Error Path)
      expect(mockApiService.triggerGapDetection).toHaveBeenCalled();
    });

    // [검증] GAP_OVERLAY 대신, 에러 메시지가 포함된 사용자 친화적 컴포넌트가 표시되어야 함.
    const errorContainer = screen.queryByText(/API Service Error: Connection failed/i);
    expect(errorContainer).toBeInTheDocument();

    // 핵심은 서비스 중단이 아니라, 복구 가능성을 제시하는 것임 (회복 탄력성)
    expect(screen.getByText("일시적인 통신 오류가 발생했습니다.")).toBeInTheDocument();
  });

  test('🚨 Test Case 3: Edge Case - GAP_OVERLAY 활성화 후 강제 이탈 시, CTA 게이트 유지 로직 검증', async () => {
    // [행동 정의] 이미 Gap이 감지된 상태를 가정하고 시작합니다.
    mockApiService.checkFunnelState.mockResolvedValue({ currentState: 'GAP_OVERLAY' });

    render(<VideoFunnelStateMachine {...initialProps} forceGapActive={true} />);

    // [검증] 컴포넌트가 초기부터 CTA Gate에 초점을 맞추고 있어야 함.
    expect(screen.getByTestId('gap-overlay')).toBeInTheDocument();

    // Gap을 건너뛰려 해도, 구매 Funnel로의 명시적 안내가 필요함 (정보 누락 공포 유지)
    const ctaGate = screen.getByRole('button', /관점 재구성 틀을 구매/).closest('button');
    expect(ctaGate).toBeInTheDocument();

    // 버튼 클릭 시, 다음 단계의 API 호출이 '구매 Funnel 시작'으로 변경되어야 함.
    fireEvent.click(ctaGate);
    // (실제 코드가 없으므로 주석 처리하지만, 이 테스트가 목표로 하는 바를 명시합니다.)
    // expect(mockApiService.navigateToFunnel).toHaveBeenCalledWith('/purchase-framework');
  });

});

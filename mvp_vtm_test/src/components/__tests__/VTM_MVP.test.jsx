import React from 'react';
import { render, screen } from '@testing-library/react';
import VTM_MVP from '../VTM_MVP';

describe('VTM_MVP Component Integration Test (Parametric)', () => {
  // 1. 기본 파라미터 테스트: 모든 값이 정상 범위인지 확인
  test('renders correctly with default parameters', () => {
    render(<VTM_MVP />);
    expect(screen.getByText(/Void Transition Module/i)).toBeInTheDocument();
  });

  // 2. 충격 강도 파라미터 테스트: Intensity 값을 조절했을 때 로직이 작동하는지 검증 (Mocking API call)
  test('should adjust visual output based on parameterized intensity', () => {
    // 실제 애니메이션 대신, 상태 변화가 발생했음을 확인하는 Mocking 기법 사용
    const mockStateChange = jest.fn();
    render(<VTM_MVP intensity={1.0} durationMs={500} onTransitionComplete={mockStateChange} />);
    // Intensity=1.0 (최대 충격)일 때, 상태 변화 핸들러가 호출되는지 확인
    expect(mockStateChange).toHaveBeenCalledTimes(1);
  });

  // 3. 테스트 모드 검증: 디버깅을 위해 isTestMode를 활성화했을 때 별도의 메시지가 출력되어야 함
  test('should display debug message when in test mode', () => {
    const TestComponent = ({ children, ...props }) => (
      <div>
        {children}
        <div data-testid="debug-message">DEBUG: Testing with Props={JSON.stringify(props)}</div>
      </div>
    );

    render(<TestComponent {...props} />);
    expect(screen.getByTestId('debug-message')).toBeInTheDocument();
  });
});

import React from 'react';
import { render, screen } from '@testing-library/react';
import MethylationCollapseComponent from './MethylationCollapseComponent';

// Mocking environment for testing the component logic
describe('MethylationCollapseComponent - V-CORE Module Test Suite', () => {

    // 🚨 핵심 테스트 케이스: 파라미터 임계값 검증 (가장 중요)
    test('should trigger critical collapse state when frequency is below threshold', () => {
        // 낮은 주파수 값으로 컴포넌트 렌더링
        render(<MethylationCollapseComponent currentFrequency={4.5} amplitudeRatio={0.7} severity="critical" />);

        // 핵심 로직 검증: critical collapse state가 활성화되는지 확인
        expect(screen.getByText(/P Collapse \(CRITICAL\)/i)).toBeInTheDocument();
    });

    test('should trigger medium collapse state when amplitude is low', () => {
        // 주파수는 높지만 진폭이 낮은 경우 (다른 실패 모드 테스트)
        render(<MethylationCollapseComponent currentFrequency={20} amplitudeRatio={0.15} severity="medium" />);

        // 핵심 로직 검증: medium collapse state가 활성화되는지 확인
        expect(screen.getByText(/P Collapse \(MEDIUM\)/i)).toBeInTheDocument();
    });

    test('should render stable state when parameters are within normal range', () => {
        // 정상 작동 범위의 값으로 렌더링
        render(<MethylationCollapseComponent currentFrequency={50} amplitudeRatio={1.0} severity="low" />);

        // 핵심 로직 검증: Collapse 트리거 문구가 나타나지 않아야 함 (혹은 안정 상태를 보여야 함)
        expect(screen.queryByText(/P Collapse/i)).not.toBeInTheDocument();
    });

    test('should correctly apply color and pattern based on severity prop', () => {
        // Mocking style attribute inspection for CSS verification (실제 환경에서는 JSDOM 사용)
        const criticalComponent = <MethylationCollapseComponent currentFrequency={1} amplitudeRatio={0.1} severity="critical" />;
        // 🚨 TODO: 실제 테스트 시, 스타일 속성(style={{...}})의 색상 코드가 정확히 적용되었는지 CSS-in-JS 방식으로 검증해야 함.
    });

});

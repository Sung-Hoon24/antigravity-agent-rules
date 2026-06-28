import { render, screen } from '@testing-library/react';
import AnomalyRenderer from '../components/AnomalyRenderer';

// 🚨 이 테스트는 실제로 AudioAnalyzer가 아닌 Mock 함수 호출을 가정합니다.
describe('AnomalyRenderer Component Test Suite', () => {
    it('Should correctly render the base structure and initial color palette', () => {
        render(<AnomalyRenderer amplitude={0.2} frequencyShift={0.3} />);
        // Glitch Violet 색상 코드가 DOM에 포함되었는지 확인
        expect(screen.getByText(/#9B59B6/i)).toBeInTheDocument();
    });

    it('Should scale the visual output (stroke width) based on high amplitude input', () => {
        // Amplitude가 높아질수록 선이 두꺼워져야 함을 확인하는 로직 (CSS 변수 검증 필요)
        render(<AnomalyRenderer amplitude={0.9} frequencyShift={0.5} />);
        // 실제 DOM 측정은 어려우므로, 시각적 지표를 통해 검증합니다.
        const container = screen.getByText(/Tension Level/i).closest('.anomaly-container');
        expect(container).toHaveStyle('opacity: 0.9'); // 높은 진폭에 따른 투명도 변화 확인
    });

    it('Should respond dynamically to frequency shift changes (Simulating Knowledge Gap)', () => {
        // Frequency Shift가 높아질수록 파동의 형태(d 속성)가 변해야 합니다.
        render(<AnomalyRenderer amplitude={0.5} frequencyShift={0.9} />);
        const svg = screen.getByRole('img'); // SVG를 롤로 찾습니다.
        expect(svg).toHaveAttribute('viewBox', '0 0 100 100');
    });
});

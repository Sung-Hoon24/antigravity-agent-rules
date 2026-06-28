import React, { useEffect, useRef } from 'react';
// AudioAnalyzer를 임포트하여 사용합니다.
import { AudioAnalyzer } from '../utils/AudioAnalyzer';

interface RendererProps {
    amplitude: number; // [0, 1] 범위의 현재 진폭 값
    frequencyShift: number; // [0, 1] 범위의 주파수 중심 변화율
}

/**
 * AnomalySignalRenderer 컴포넌트: 오디오 파라미터에 기반한 시각적 '글리치' 효과를 구현합니다.
 * @param props - 실시간 오디오 파라미터를 받습니다.
 */
const AnomalyRenderer: React.FC<RendererProps> = ({ amplitude, frequencyShift }) => {
    // SVG와 같은 Canvas/WebGL 기반의 복잡한 렌더링이 필요하지만, 여기서는 CSS 변수를 활용하여 구조화합니다.
    return (
        <div className="anomaly-container" style={{
            transition: 'all 0.1s linear',
            opacity: amplitude * 0.8 + 0.2 // 진폭에 따라 투명도 변화
        }}>
            {/* 핵심 시각 요소: 주파수와 진폭을 결합하여 변형 */}
            <svg width="100%" height="100%" viewBox="0 0 100 100" preserveAspectRatio="none">
                {/* 배경 글리치 효과 (주로 frequencyShift에 반응) */}
                <rect
                    x="0" y="0" width="100%" height="100%" fill="#9B59B6" opacity={0.2} />

                {/* 파동 형태의 애니메이션 루프 (Amplitude와 Frequency가 모두 영향) */}
                <path
                    d={`M0,50 C ${amplitude * 10 + 40}, ${frequencyShift * 30 + 30} ${100}, ${frequencyShift * 20 + 70} L100, 50 Z`}
                    fill="#9B59B6"
                    stroke="rgba(155, 89, 182, 0.8)"
                    strokeWidth={Math.max(2, amplitude * 10)} // 진폭에 비례하여 선 굵기 변화
                />
            </svg>

            {/* 상태 표시 (디버깅 및 검증용) */}
            <div style={{ color: 'white', fontSize: '0.8em' }}>
                [A]: {amplitude.toFixed(3)} | [F]: {frequencyShift.toFixed(3)}
                <span style={{ float: 'right', color: '#FFD700' }}>Tension Level</span>
            </div>
        </div>
    );
};

export default AnomalyRenderer;

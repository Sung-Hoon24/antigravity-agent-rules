import React from 'react';

/**
 * @component MethylationCollapseComponent
 * @description 측정 가능한 파라미터($P$)의 붕괴(Collapse)를 시각화하는 모듈.
 *              주파수 감소, 진폭 하락 등 공학적 시스템 실패를 표현합니다.
 * @param {object} props - 컴포넌트 속성
 * @param {number} props.currentFrequency - 현재 파라미터 주파수 값 (Hz)
 * @param {number} props.amplitudeRatio - 진폭 비율 (0.0 ~ 1.0)
 * @param {string} [props.severity='low'] - 오류 심각도 ('low', 'medium', 'critical')
 * @returns {JSX.Element} Collapse 애니메이션을 포함한 JSX 요소
 */
const MethylationCollapseComponent = ({ currentFrequency, amplitudeRatio, severity = 'low' }) => {
    // 파라미터 임계점 정의 (Spec v1.0 기반)
    const CRITICAL_FREQ_THRESHOLD = 5; // Hz 이하일 때 치명적
    const COLLAPSE_TRIGGERED = currentFrequency < CRITICAL_FREQ_THRESHOLD || amplitudeRatio < 0.2;

    // 심각도에 따른 색상 코드와 패턴 변형 정의 (Hex Code / CSS)
    let colorCode, patternEffect;
    switch (severity) {
        case 'critical':
            colorCode = '#FF4136'; // 빨간색 계열 (Danger)
            patternEffect = 'stutter-high-frequency';
            break;
        case 'medium':
            colorCode = '#FFDC00'; // 노란색 계열 (Warning)
            patternEffect = 'ripple-moderate';
            break;
        case 'low':
        default:
            colorCode = '#39CCCC'; // 기본 청록색 (Normal)
            patternEffect = 'subtle-pulse';
    }

    // 붕괴 상태에 따른 시각적 변형 로직
    const collapseScale = COLLAPSE_TRIGGERED ? Math.max(0, amplitudeRatio * 1.5) : 1;

    return (
        <div
            className={`v-core-container ${patternEffect}`}
            style={{
                backgroundColor: colorCode + '22', // 투명도 적용된 배경색
                transform: `scale(${collapseScale})`,
                transition: 'all 0.3s ease-out'
            }}
        >
            <div className="visual-data-display" style={{ border: `1px solid ${colorCode}`, animation: `${patternEffect} 1s infinite` }}>
                {/* 실제 애니메이션은 Lottie/SVG로 대체되어야 함. 여기는 구조적 임시 placeholder */}
                <p>Frequency: {currentFrequency.toFixed(2)} Hz | Amplitude Ratio: {(amplitudeRatio * 100).toFixed(0)}%</p>
                <div style={{ fontSize: `${Math.max(10, collapseScale * 30)}px`, color: colorCode }}>
                    P Collapse ({severity.toUpperCase()})
                </div>
            </div>
        </div>
    );
};

export default MethylationCollapseComponent;

/**
 * AnomalySignalRenderer: 오디오 파라미터에 동기화되는 KGAS 시각적 오류 신호 컴포넌트 (V3.0)
 * @param audioParams - useAudioAnalysis로부터 받은 실시간 분석 파라미터
 */
import React from 'react';
import useAudioAnalysis from '../hooks/useAudioAnalysis';

// 타입 정의
interface AudioParameters {
    frequencyMagnitude: number; // 0 ~ 1 (주파수 에너지)
    isAnomaly: boolean;        // true = S1 진입 임계값 초과
}

const AnomalySignalRenderer: React.FC<{ audioStream: MediaStream }> = ({ audioStream }) => {
    // Hook을 통해 실시간 오디오 파라미터 받아오기
    const audioParams = useAudioAnalysis(audioStream);

    // --- State Machine Logic 구현 (S0 <-> S1) ---
    let currentStatus = 'S0'; // 기본 상태: Idle/Normal
    let intensity = 0;        // 시각적 불안정성 강도 (0~1)

    if (audioParams.isAnomaly || audioParams.frequencyMagnitude > 0.5) {
        currentStatus = 'S1'; // Anomaly Detected
        intensity = Math.min(1, audioParams.frequencyMagnitude * 2); // 진폭에 비례하여 강도 증가
    } else if (audioParams.frequencyMagnitude < 0.1) {
        currentStatus = 'S0'; // 정상 상태로 복귀
        intensity = 0;
    }

    // --- Renderer Logic: SVG 기반 시각적 오류 구현 ---
    const glitchStyle = {
        opacity: currentStatus === 'S0' ? 0.05 : Math.min(1, intensity * 1.2), // S0에서는 배경 노이즈로만 존재
        transform: `scale(${1 + intensity * 0.1})`, // 강도에 따라 약간 확대 효과
        transition: 'all 0.1s linear', // 빠른 반응성 확보
    };

    const GlitchVisual = (
        <svg className="glitch-overlay" width="100%" height="100%" style={glitchStyle}>
            {/* 노이즈 레이어 */}
            <rect x="0" y="0" width="100%" height="100%" fill="#9B59B6" opacity={0.1} />
            {/* 데이터 흐름 파괴 시각화 (직사각형 패턴) */}
            {currentStatus === 'S1' && (
                <g className="data-disruption">
                    <rect x={Math.random() * 10}% y={Math.random() * 10}% width={`${(intensity * 5 + 2)}%`} height={3} fill="#9B59B6" opacity={0.7}/>
                    <rect x={(Math.sin(Date.now()/100) * 50)%100}% y={(Math.cos(Date.now()/100) * 50)%100}% width={`${(intensity * 4 + 2)}%`} height={3} fill="#9B59B6" opacity={0.7}/>
                </g>
            )}
        </svg>
    );


    return (
        <div className="anomaly-renderer">
            {/* 실제 비디오 플레이어 위에 오버레이되는 영역 시뮬레이션 */}
            {GlitchVisual}

            {/* 디버그 UI: 현재 상태와 파라미터 값 출력 */}
            <div style={{
                position: 'absolute', top: '10px', left: '10px',
                background: 'rgba(0,0,0,0.7)', color: 'white', padding: '8px',
                borderRadius: '5px', fontSize: '14px'
            }}>
                <strong>[Status]</strong> {currentStatus} (Intensity: {intensity.toFixed(2)})<br/>
                {/* 오디오 파라미터 디버그 값 출력 */}
                <small>Freq Mag: {audioParams.frequencyMagnitude.toFixed(3)} | Anomaly: {String(audioParams.isAnomaly)}</small>
            </div>

             {/* CSS 애니메이션 적용을 위한 컨테이너 역할 */}
            <style>{`
                .glitch-overlay * { pointer-events: none; }
                .anomaly-renderer { position: relative; width: 100%; height: 300px; background: #2c3e50; overflow: hidden; border: 1px solid #9B59B6; }
            `}</style>
        </div>
    );
};

export default AnomalySignalRenderer;

import React, { useState, useEffect } from 'react';
import useAudioAnalyser from '../hooks/useAudioAnalyser';

// 가상의 오디오 스트림 (실제 구현 시 <audio> 태그의 ref에서 받아와야 함)
const MockStream = () => {
    console.warn("⚠️ 경고: 이 컴포넌트는 실제 MediaStream 없이 로직 테스트를 위해 제작되었습니다.");
    return null;
};

/**
 * @description 오디오 분석 결과에 반응하는 Anomaly Signal Renderer의 독립적 동작 테스트 환경.
 */
const AudioInputTestComponent: React.FC = () => {
    // 1. 실제로는 useAudioAnalyser(stream)을 사용해야 하지만, 일단 Mock Stream으로 시작합니다.
    const audioData = useAudioAnalyser(MockStream());

    const [audioFreqs, setAudioFreqs] = useState<Float32Array>(new Float32Array(1));
    const [distortion, setDistortion] = useState(0);

    // Web Audio Hook에서 데이터를 받아오는 과정 (실제로는 useAudioAnalyser가 상태를 관리)
    useEffect(() => {
        if (audioData) {
            setAudioFreqs(audioData.frequencies);
            setDistortion(audioData.distortionLevel);
        }
    }, [audioData]);

    // --- 시뮬레이션 및 디버깅 영역 ---
    return (
        <div style={{ border: '2px dashed #cc00ff', padding: '20px', margin: '20px' }}>
            <h2>🧪 Anomaly Signal Renderer 테스트 환경</h2>
            <p>Status: {audioData ? "✅ Active" : "⏳ Waiting for Audio Stream..."}</p>

            {/* 1. 핵심 파라미터 표시 */}
            <div style={{ marginBottom: '20px', padding: '10px', background: '#330066', color: '#e0c0ff' }}>
                <h4>📊 분석 결과 (실시간 데이터 시뮬레이션)</h4>
                <p>📉 **현재 왜곡 레벨 (Distortion Level):** {(distortion * 100).toFixed(2)}% (Max: 100%)</p>
                <p>🧬 **주파수 배열 크기:** {audioFreqs.length} bins</p>
            </div>

            {/* 2. AnomalySignalRenderer 시각화 영역 */}
            <div style={{ width: '100%', height: '150px', border: '1px solid #ccc' }}>
                {/* 실제 Renderer가 이 데이터를 받아 SVG/Canvas에 그릴 것입니다. */}
                <p>🎨 [SVG/Canvas Placeholder]: Distortion Level ({distortion})을 기반으로 시각적 파형이 여기에 그려져야 합니다.</p>
            </div>

            {/* 3. 디버깅 콘솔 출력 (실제 데이터 확인용) */}
            <details style={{ marginTop: '20px' }}>
                <summary>🔍 로그 및 원본 주파수 배열 샘플 보기</summary>
                <pre style={{ backgroundColor: '#1e1e1e', color: '#aaffaa', padding: '10px', overflowX: 'auto' }}>
                    {/* 실제 디버깅 시, 이 콘솔에 데이터를 출력합니다. */}
                    Simulated Freq Data Sample (first 5): [{audioFreqs[0].toFixed(4)}, {audioFreqs[1].toFixed(4)}, ... ]
                </pre>
            </details>
        </div>
    );
};

export default AudioInputTestComponent;

/**
 * useAudioAnalysis Hook: Web Audio API를 활용하여 실시간 오디오 파라미터를 분석합니다.
 * @param audioStream - 입력받을 MediaStream (예: 마이크나 외부 오디오 소스)
 * @returns {object} 분석된 오디오 메트릭 (frequency, amplitude 등)
 */
import { useState, useEffect } from 'react';

const useAudioAnalysis = (audioStream: MediaStream | null): { frequencyMagnitude: number; isAnomaly: boolean } => {
    const [analysisData, setAnalysisData] = useState<{ frequencyMagnitude: number; isAnomaly: boolean }>({
        frequencyMagnitude: 0,
        isAnomaly: false,
    });

    useEffect(() => {
        if (!audioStream) return;

        const AudioContextClass = window.AudioContext || (window as any).webkitAudioContext;
        if (!AudioContextClass) {
            console.error("Web Audio API를 지원하지 않는 브라우저입니다.");
            return;
        }

        const audioContext = new AudioContextClass();
        const source = audioContext.createMediaStreamSource(audioStream);
        const analyser = audioContext.createAnalyser();
        analyser.fftSize = 2048;
        source.connect(analyser);

        // 데이터 버퍼 설정
        const bufferLength = analyser.frequencyBinCount;
        const dataArray = new Uint8Array(bufferLength);

        const updateAnalysis = () => {
            requestAnimationFrame(() => {
                analyser.getByteFrequencyData(dataArray);

                let sumMagnitude = 0;
                for (let i = 0; i < bufferLength; i++) {
                    sumMagnitude += dataArray[i];
                }

                const averageMagnitude = sumMagnitude / bufferLength; // 평균 진폭 값
                const frequencyMagnitude = Math.min(1, averageMagnitude / 255); // 0~1 스케일링

                // 디버깅 로직: 특정 임계값을 넘으면 'Anomaly'로 간주 (S1 트리거 시뮬레이션)
                const isAnom = frequencyMagnitude > 0.6;

                setAnalysisData({
                    frequencyMagnitude,
                    isAnomaly: isAnom,
                });
            });
        };

        // 분석 루프 시작
        updateAnalysis();
        const animationFrameId = setInterval(updateAnalysis, 50); // 매 50ms마다 업데이트

        return () => {
            clearInterval(animationFrameId);
            audioContext.close();
        };
    }, [audioStream]);

    return analysisData;
};

export default useAudioAnalysis;

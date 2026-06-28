import { useState, useEffect, useRef } from 'react';

/**
 * @description 오디오 스트림을 분석하고 주기적인 파라미터 데이터를 제공하는 커스텀 훅.
 * Web Audio API의 AnalyserNode를 활용하며, 브라우저 환경에서만 동작합니다.
 * @param stream - 오디오 스트림 (MediaStream)
 * @returns {object} { frequencies: Float32Array, distortionLevel: number }
 */
const useAudioAnalyser = (stream: MediaStream | null): { frequencies: Float32Array; distortionLevel: number } => {
    const [data, setData] = useState<{ frequencies: Float32Array; distortionLevel: number } | null>(null);
    const audioContextRef = useRef<AudioContext | null>(null);
    const analyserRef = useRef<AnalyserNode | null>(null);

    useEffect(() => {
        if (!stream) return;

        // 1. Context 초기화 및 연결
        const audioContext = new (window.AudioContext || window['webkitSpeechRecognition'])(window.AudioContext ? window.AudioContext : window['webkitAudioContext']);
        audioContextRef.current = audioContext;

        const source = audioContext.createMediaStreamSource(stream);
        const analyser = audioContext.createAnalyser();
        analyser.fftSize = 2048; // FFT 크기 설정 (주파수 해상도)
        source.connect(analyser);
        analyser.connect(audioContext.destination);

        analyserRef.current = analyser;
        const bufferLength = analyser.frequencyBinCount;
        const dataArray: Float32Array = new Float32Array(bufferLength);

        // 2. 데이터 분석 루프 설정 (Animation Frame)
        const animationLoop = () => {
            if (!analyserRef.current || !audioContextRef.current) return;

            // 주파수 데이터를 추출합니다.
            analyserRef.current.getFloatTimeDomainData(dataArray);

            // 시간 도메인 데이터 기반으로 Distortion Level을 계산 (간단한 RMS 근사치 사용)
            let sum = 0;
            for (let i = 0; i < bufferLength; i++) {
                sum += dataArray[i] * dataArray[i];
            }
            const rms = Math.sqrt(sum / bufferLength);

            // 데이터 상태 업데이트
            setData({ frequencies: dataArray, distortionLevel: Math.min(1.0, rms * 5) }); // 값 스케일링 조정

            requestAnimationFrame(animationLoop);
        };

        // 애니메이션 루프 시작
        const animationId = requestAnimationFrame(animationLoop);

        // Cleanup 함수
        return () => {
            cancelAnimationFrame(animationId);
            source.disconnect();
            audioContext.close();
        };
    }, [stream]); // stream이 변경될 때만 재실행

    return data || { frequencies: new Float32Array(1), distortionLevel: 0 };
};

export default useAudioAnalyser;

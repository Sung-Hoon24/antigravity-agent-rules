import { useState, useEffect } from 'react';
import { AudioParameters } from '../components/renderer/AnomalySignalRenderer';

/**
 * useAudioStreamMock: 실제 오디오 데이터를 모의(Mocking)하여 스트림을 시뮬레이션하는 커스텀 훅.
 * 통합 테스트를 위해 임계값 경계를 통과하는 패턴을 주입합니다.
 * @returns {AudioParameters} 현재 가상의 오디오 파라미터
 */
export const useAudioStreamMock = () => {
    const [params, setParams] = useState<AudioParameters>({
        rmsDelta: 0.10, // 초기값 (Normal)
        freqDeviation: 15.0,
        spectralComplexity: 0.8,
    });

    useEffect(() => {
        // 시뮬레이션 주기 설정 (실제로는 Web Audio API의 분석기에서 데이터가 도착함)
        const interval = setInterval(() => {
            let newParams: Partial<AudioParameters>;

            // --- 테스트 케이스 로직 주입 ---
            // 1. Normal Mode (초기 상태 유지)
            if (Date.now() % 3000 < 1500) {
                newParams = { rmsDelta: 0.1 + Math.random() * 0.05, freqDeviation: 10 + Math.random() * 5, spectralComplexity: 0.7 + Math.random() * 0.2 };
            }
            // 2. Warning Mode (임계값 근접 -> 지식적 결핍 유도)
            else if (Date.now() % 3000 < 2500) {
                newParams = { rmsDelta: 0.08, freqDeviation: 3 + Math.random(), spectralComplexity: 0.4 + Math.random() * 0.1 };
            }
            // 3. Critical Mode (붕괴 임계값 진입 -> Anomaly Signal)
            else {
                newParams = { rmsDelta: 0.015, freqDeviation: 0.8, spectralComplexity: 0.2 }; // V5.0 Threshold 이하로 강제 설정
            }

            setParams(prev => ({
                rmsDelta: newParams!['rmsDelta'] as number,
                freqDeviation: newParams!['freqDeviation'] as number,
                spectralComplexity: newParams!['spectralComplexity'] as number,
            }));
        }, 100); // 100ms 마다 업데이트하여 실시간 느낌 부여

        return () => clearInterval(interval);
    }, []);

    return params as AudioParameters;
};

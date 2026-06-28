import React, { useState, useEffect } from 'react';
// AudioAnalyzer를 임포트합니다. (실제 프로젝트에서는 Web Worker로 분리 권장)
import { AudioAnalyzer } from './utils/AudioAnalyzer';
import AnomalyRenderer from './components/AnomalyRenderer';

const App: React.FC = () => {
    const [amplitude, setAmplitude] = useState(0);
    const [frequencyShift, setFrequencyShift] = useState(0);
    // AudioAnalyzer 인스턴스를 컴포넌트 생명주기 동안 유지하여 리소스 누수 방지
    const analyzerRef = useRef<AudioAnalyzer | null>(null);

    useEffect(() => {
        analyzerRef.current = new AudioAnalyzer();
        console.log("✅ Anomaly Renderer Sandbox initialized.");

        // *** Mocking: 실제 오디오 스트림 연결 대신, 타이머를 사용해 가상의 데이터 주입을 시뮬레이션합니다.
        let intervalId: NodeJS.Timeout;
        const mockUpdateLoop = () => {
            // 가짜 파라미터를 주기적으로 생성 (테스트 환경 확보)
            const mockAmp = Math.random() * 0.8 + 0.2; // [0.2, 1.0]
            const mockFreq = Math.sin(Date.now() / 500) * 0.4 + 0.6; // 주기적인 변화 유도
            setAmplitude(mockAmp);
            setFrequencyShift(mockFreq);
        };

        intervalId = setInterval(() => {
            mockUpdateLoop();
        }, 100); // 100ms 마다 업데이트 (실시간 느낌 부여)


        // 클린업 함수: 컴포넌트 언마운트 시 반드시 타이머와 리소스를 정리해야 합니다.
        return () => {
            clearInterval(intervalId);
            if (analyzerRef.current) {
                analyzerRef.current.dispose(); // 리소스 해제 호출
            }
        };
    }, []);

    return (
        <div style={{ width: '80%', margin: '50px auto', background: '#1a1a2e', padding: '40px', borderRadius: '10px' }}>
            <h1>Anomaly Signal Renderer Sandbox</h1>
            <p>현재 오디오 파라미터에 의해 구동되는 실시간 테스트베드입니다. (Mock Data Running)</p>
            <div style={{ border: '2px dashed #9B59B6', padding: '10px' }}>
                <AnomalyRenderer
                    amplitude={amplitude}
                    frequencyShift={frequencyShift}
                />
            </div>
        </div>
    );
};

export default App;

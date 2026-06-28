import React, { useState, useEffect } from 'react';
import SoundInputSimulator from '../SoundInputSimulator/SoundInputSimulator';
import VCOREStateEngine from '../VCOREStateEngine/VCOREStateEngine';
import AnomalySignalRenderer from '../AnomalySignalRenderer/AnomalySignalRenderer';

/**
 * @description 통합 테스트베드: 사운드 파라미터 입력에 따른 시스템 상태 변화 검증.
 * 이 컴포넌트는 모든 핵심 로직을 한 곳에서 실행하며, 디버깅의 진입점 역할을 합니다.
 */
const VCORE_Testbed = () => {
    // 1. 테스트 초기 상태 정의 (Initial State)
    const [currentState, setCurrentState] = useState({
        stateName: 'KnowledgeGapPreHook', // Hook 시작 전 기본 상태
        currentParams: null,
        anomalyActive: false,
        logHistory: []
    });

    // 2. 사운드 파라미터 시뮬레이션 및 State Transition 트리거 (핵심 루프)
    const [soundData, setSoundData] = useState({ frequency: 100, amplitude: 0.5 });

    useEffect(() => {
        // 매 500ms마다 새로운 가상 사운드 데이터를 발생시키고 상태를 업데이트하는 시뮬레이션 루프
        const interval = setInterval(() => {
            // Mock Sound Data Generation (실제로는 Web Audio API에서 받아옴)
            const newFreq = Math.random() * 400 + 100; // 100Hz ~ 500Hz
            const newAmp = Math.random() * 0.8 + 0.2;  // 0.2 ~ 1.0

            setSoundData({ frequency: newFreq, amplitude: newAmp });

        }, 500);

        return () => clearInterval(interval);
    }, []);

    // soundData가 바뀔 때마다 State Engine을 거쳐 상태와 애니메이션을 업데이트합니다.
    useEffect(() => {
        if (!soundData) return;

        console.log(`[Testbed] Input Params Received: Freq=${soundData.frequency.toFixed(2)}, Amp=${soundData.amplitude.toFixed(2)}`);

        // 🚀 핵심 로직 호출: State Engine에 현재 사운드 데이터를 전달하여 다음 상태를 계산
        const newState = VCOREStateEngine.processSoundParameters({
            ...soundData,
            timestamp: Date.now()
        }, currentState);

        setCurrentState(prev => ({
            ...newState, // 새로운 상태 및 애니메이션 플래그 적용
            currentParams: soundData,
            logHistory: [...prev.logHistory, `[${new Date().toLocaleTimeString()}] Transition to ${newState.stateName}`]
        }));
    }, [soundData]);

    return (
        <div className="vcore-testbed p-8 bg-gray-900 text-white min-h-screen">
            <h2 className="text-3xl font-bold mb-6 border-b pb-2 text-red-400">V-CORE & Anomaly Signal 통합 테스트베드 (Simulation)</h2>

            {/* 1. 시각적 출력 영역: 애니메이션 컴포넌트 */}
            <div className="w-full h-[350px] bg-black border-4 border-gray-700 flex items-center justify-center relative mb-8">
                <AnomalySignalRenderer isActive={currentState.anomalyActive} params={{ frequency: soundData.frequency, amplitude: soundData.amplitude }} />
            </div>

            {/* 2. 상태 정보 및 디버깅 로그 */}
            <div className="grid grid-cols-3 gap-6 mb-8">
                <div className="bg-gray-800 p-4 rounded shadow-xl col-span-1">
                    <h3 className="text-lg font-semibold text-yellow-400 mb-2">Current State</h3>
                    <p className="text-2xl font-bold">{currentState.stateName}</p>
                </div>
                <div className="bg-gray-800 p-4 rounded shadow-xl col-span-1">
                    <h3 className="text-lg font-semibold text-yellow-400 mb-2">Input Params</h3>
                    <p>Frequency: {soundData.frequency.toFixed(2)} Hz</p>
                    <p>Amplitude: {soundData.amplitude.toFixed(2)}</p>
                </div>
                 <div className="bg-gray-800 p-4 rounded shadow-xl col-span-1">
                    <h3 className="text-lg font-semibold text-yellow-400 mb-2">Anomaly Flag</h3>
                    <p className={`text-xl ${currentState.anomalyActive ? 'text-red-500 animate-pulse' : 'text-green-400'}`}>
                        {currentState.anomalyActive ? 'ACTIVE' : 'STABLE'}
                    </p>
                </div>
            </div>

            {/* 3. 디버깅 로그 */}
             <div className="bg-gray-800 p-4 rounded shadow-xl col-span-full">
                <h3 className="text-xl font-semibold text-yellow-400 mb-2">System Log</h3>
                <pre className="text-sm overflow-auto max-h-64 bg-gray-900 p-3 rounded whitespace-pre-wrap">{currentState.logHistory.slice(-10).join('\n')}</pre>
            </div>
        </div>
    );
}

export default VCORE_Testbed;

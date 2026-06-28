import React, { useState, useEffect } from 'react';
import AnomalySignalRenderer from './renderer/AnomalySignalRenderer';
import useAudioStreamMock from '../hooks/useAudioStreamMock';

/**
 * @component SandboxTestComponent
 * E2E 통합 테스트 환경을 시뮬레이션하는 컴포넌트.
 * Mock Audio Data Stream이 들어와 Renderer가 실시간으로 반응하는지 검증합니다.
 */
const SandboxTestComponent = () => {
    // 1. 데이터 파라미터 스트림 연결 (Mocking)
    // useAudioStreamMock은 주기적으로 변화하는 { frequency, amplitude, delta } 객체를 반환한다고 가정합니다.
    const mockAudioData = useAudioStreamMock();

    // 2. 테스트 상태 관리: 시뮬레이션 시작/종료 플래그
    const [isTesting, setIsTesting] = useState(false);

    useEffect(() => {
        if (mockAudioData && isTesting) {
            console.log("✅ E2E Sandbox Activated: Data stream detected.");
        } else if (!mockAudioData) {
             console.warn("⚠️ Mock Audio Stream not ready. Cannot run test.");
        }
    }, [mockAudioData, isTesting]);

    return (
        <div style={{ padding: '20px', fontFamily: 'monospace' }}>
            <h2>🔬 E2E Sandbox Test Environment</h2>
            <p><strong>목표:</strong> Mock Data Stream ({JSON.stringify(mockAudioData?.frequency || 0)} Hz, {JSON.stringify(mockAudioData?.amplitude || 0)})을 받아 AnomalySignalRenderer가 실시간으로 시각화되는지 검증합니다.</p>

            <div style={{ marginBottom: '20px' }}>
                <button
                    onClick={() => setIsTesting(!isTesting)}
                    style={{ padding: '10px', marginRight: '10px', cursor: 'pointer' }}
                >
                    {isTesting ? '⏸️ 테스트 일시 정지 (Pause Test)' : '▶️ E2E Sandbox 시작 (Start Test)'}
                </button>
                <span style={{ color: isTesting ? 'green' : 'gray' }}>
                    상태: {isTesting ? 'RUNNING 🟢' : 'STOPPED 🔴'}
                </span>
            </div>

            {/* 핵심 컴포넌트 연결 및 테스트 */}
            <div style={{ border: '1px solid #ccc', padding: '20px', minHeight: '300px' }}>
                <h3>AnomalySignalRenderer Output Window</h3>
                <AnomalySignalRenderer
                    audioParams={mockAudioData} // Mock 데이터 직접 주입
                    isCriticalState={!isTesting || mockAudioData.amplitude > 0.8} // 임계값 기반 상태 결정
                />
            </div>

            {/* 디버깅 정보 패널 */}
            <div style={{ marginTop: '20px', fontSize: '0.9em' }}>
                <h4>[Debug Info]</h4>
                <pre>{JSON.stringify(mockAudioData, null, 2)}</pre>
                <p class="note">⚠️ 테스트 성공 기준: amplitude가 임계값을 초과하는 순간 (isCriticalState=true), AnomalySignalRenderer의 시각적 출력이 즉시 변해야 함.</p>
            </div>
        </div>
    );
};

export default SandboxTestComponent;

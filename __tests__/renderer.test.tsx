import React from 'react';
import { render, screen } from '@testing-library/react';
import AnomalySignalRenderer from '../components/renderer/AnomalySignalRenderer';

// ----------------------------------------------------
// 테스트 유틸리티: 임계값 경계를 넘나드는 가짜 데이터셋 정의
// ----------------------------------------------------
const mockTestCases = [
    { name: "T0_NormalOperation", params: { rmsDelta: 0.12, freqDeviation: 18.5, spectralComplexity: 0.9 } }, // 정상 범위
    { name: "T1_WarningTrigger", params: { rmsDelta: 0.03, freqDeviation: 2.5, spectralComplexity: 0.45 } }, // Warning (두 개 이상 근접)
    { name: "T2_CriticalCollapse", params: { rmsDelta: 0.01, freqDeviation: 0.5, spectralComplexity: 0.1 } }  // Critical (모든 임계값 하회)
];

test('AnomalySignalRenderer는 다양한 오디오 파라미터에 따라 올바른 상태를 판별하고 시각화한다.', () => {
    mockTestCases.forEach(testCase => {
        console.log(`\n--- Running Test Case: ${testCase.name} ---`);

        // 렌더링 실행
        render(<AnomalySignalRenderer audioParams={testCase.params} />);

        // 상태별 기대 결과 검증 (Asserting the displayed message/state)
        if (testCase.name === "T0_NormalOperation") {
            expect(screen.getByText(/안정적 상태: 콘텐츠 흐름 유지 중/i)).toBeInTheDocument();
            expect(screen.queryByText(/논리적 붕괴 임계점 도달/i)).not.toBeInTheDocument();
        } else if (testCase.name === "T1_WarningTrigger") {
            // Warning은 두 개 이상이 근접해야 함 -> 현재는 RMS와 Complexity가 충분히 근접함
            expect(screen.getByText(/시스템 이상 징후 포착/i)).toBeInTheDocument();
        } else if (testCase.name === "T2_CriticalCollapse") {
            // Critical은 모든 임계값을 만족해야 함
            expect(screen.getByText(/논리적 붕괴 임계점 도달: 정보의 근본적 결핍 감지/i)).toBeInTheDocument();
        }
    });
});

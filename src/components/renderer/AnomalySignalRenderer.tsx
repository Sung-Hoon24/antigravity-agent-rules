import React, { useState, useEffect } from 'react';

/**
 * @typedef {object} AudioParameters
 * @property {number} rmsDelta - 진폭 변화율 (RMS Decay Rate)
 * @property {number} freqDeviation - 주파수 편차 (Frequency Deviation)
 * @property {number} spectralComplexity - 스펙트로그램 복잡도
 */

/**
 * AnomalySignalRenderer: 오디오 파라미터의 이상 징후를 시각화하는 핵심 컴포넌트.
 * V5.0 사양서에 정의된 임계값(Threshold)을 기반으로 상태 변화를 감지합니다.
 * @param {object} props - Component Props
 * @param {AudioParameters} props.audioParams - 실시간 오디오 분석 결과 파라미터
 */
const AnomalySignalRenderer = ({ audioParams }) => {
    // 1. V5.0 사양서 기반의 임계값 정의 (상수화)
    const THRESHOLD_RMS = 0.02; // RMS < 0.02 & Rate(Decay) > 3sigma
    const THRESHOLD_FREQ = 1;   // |Delta f| < 1 Hz & Variance(Harmonics) > 0.9
    const THRESHOLD_COMPLEXITY = 0.4; // C < 0.4

    /**
     * 상태 정의 및 논리적 검증 (State Machine Trigger)
     * @param {AudioParameters} params - 현재 파라미터
     * @returns {'NORMAL' | 'WARNING' | 'CRITICAL'} 현재 시스템의 상태
     */
    const determineState = (params) => {
        // 1. Critical Check: 모든 지표가 동시에 임계값 미만일 때 (붕괴 증명 단계)
        if (params.rmsDelta < THRESHOLD_RMS && params.freqDeviation < THRESHOLD_FREQ && params.spectralComplexity < THRESHOLD_COMPLEXITY) {
            return 'CRITICAL'; // Knowledge Gap 발생 지점
        }

        // 2. Warning Check: 최소 두 개 이상의 지표가 임계값에 근접할 때 (이상 징후 감지 단계)
        let warningCount = 0;
        if (params.rmsDelta < THRESHOLD_RMS * 1.5) { warningCount++; }
        if (params.freqDeviation < THRESHOLD_FREQ * 2) { warningCount++; }
        if (params.spectralComplexity < THRESHOLD_COMPLEXITY * 1.5) { warningCount++; }

        if (warningCount >= 2) {
            return 'WARNING'; // Anomaly Signal Renderer 활성화
        }

        return 'NORMAL';
    };

    // 상태 계산 및 스타일링 로직
    const currentState = determineState(audioParams);

    let visualizationColor;
    let message;

    switch (currentState) {
        case 'CRITICAL':
            visualizationColor = '#FF0055'; // 붕괴/경고 색상
            message = "!!! 논리적 붕괴 임계점 도달: 정보의 근본적 결핍 감지 !!!";
            break;
        case 'WARNING':
            visualizationColor = '#FFFF00'; // 경고색
            message = "⚠️ 시스템 이상 징후 포착: 분석 파라미터 재검토 필요.";
            break;
        case 'NORMAL':
        default:
            visualizationColor = '#33CC33'; // 정상 작동 색상
            message = "✅ 안정적 상태: 콘텐츠 흐름 유지 중.";
    }

    // 렌더링 (SVG 대신 Div로 간소화하여 로직 검증에 집중)
    return (
        <div style={{
            padding: '20px',
            border: `3px solid ${visualizationColor}`,
            backgroundColor: currentState === 'CRITICAL' ? '#1a0007' : '#0d1a0e',
            color: '#fff',
            textAlign: 'center'
        }}>
            <h2>Anomaly Signal Renderer (V5.0)</h2>
            <p style={{ color: visualizationColor, fontSize: '1.2em', fontWeight: 'bold' }}>{message}</p>
            <p>Current State: <strong>{currentState}</strong></p>
            <div style={{ marginTop: '15px', borderTop: '1px dashed #444', paddingTop: '10px' }}>
                <h4>Input Parameters (Mocked)</h4>
                <ul>
                    <li>$\text{RMS}_{\Delta}$: {audioParams.rmsDelta.toFixed(4)}</li>
                    <li>$\Delta f$: {audioParams.freqDeviation.toFixed(2)} Hz</li>
                    <li>$\mathcal{C}_{complexity}$: {audioParams.spectralComplexity.toFixed(2)}</li>
                </ul>
            </div>
        </div>
    );
};

export default AnomalySignalRenderer;

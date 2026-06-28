import React from 'react';
/**
 * FunnelGatewayAsset: Designer가 제공한 Lottie 또는 WebGL Shader 기반의 시각적 에셋 컴포넌트입니다.
 * 이 파일은 실제 모션 엔진과의 통합 지점을 명확히 합니다.
 */
const FunnelGatewayAsset = ({ state, timeElapsedMs }) => {
    let visualOutput = '';
    let className = 'funnel-gateway';

    switch (state) {
        case 'GAP_INIT':
            visualOutput = `[WebGL Shader] Initializing Systemic Deficiency Glitch Pattern. T+${timeElapsedMs}ms`;
            className += ' glitch-start';
            break;
        case 'GLITCH_TRANSITION':
            // 핵심 구간: T+320ms ~ T+510ms의 상태 전이 로직을 시각화하는 부분입니다.
            visualOutput = `[Lottie/WebGL] State Transition Active! Time Critical Zone (${Math.max(320, Math.min(510, timeElapsedMs))}ms). Error Code: ${Math.floor(Math.random() * 999)}`;
            className += ' transition-active';
            break;
        case 'RESOLUTION':
            visualOutput = `[System Reset] Transition Complete. Moving to Resolution State.`;
            className += ' resolved';
            break;
        default:
            visualOutput = 'Stable System Flow.';
    }

    return (
        <div className={`gateway-container ${className}`}>
            <h2>Funnel Gateway ({state})</h2>
            <p>{visualOutput}</p>
            {/* 여기에 실제 Lottie/WebGL 뷰포트가 들어갑니다. */}
        </div>
    );
};

export default FunnelGatewayAsset;

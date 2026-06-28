// src/api/EffectsAPI.js
/**
 * @description [Mock API Layer] 모든 시각/청각 효과는 모듈형으로 분리됩니다. (Designer Spec 기반)
 * 실제 프로젝트에서는 이 파일들이 네이티브 WebGL/Canvas 라이브러리로 대체됩니다.
 */

// VTM: Void Transition Module - 물리적 왜곡 및 파괴 오류 시각화
export const VTM_GlitchEffect = ({ intensity = 0.5 }) => {
    const style = {
        position: 'absolute', top: 0, left: 0, width: '100%', height: '100%',
        zIndex: 10, opacity: intensity * 0.8, mixBlendMode: 'screen'
    };
    return <div style={style}>VTM Glitch Layer (Intensity: {intensity})</div>;
};

// FlashingOverlay: 정보 과부하 유도용 깜빡임 효과 (Writer Trigger 기반)
export const FlashingOverlay = ({ frequency = 2, duration = 1 }) => {
    const style = {
        position: 'absolute', top: 0, left: 0, width: '100%', height: '100%',
        zIndex: 15, animation: `flash ${(duration * 2)}s linear infinite`, // CSS 애니메이션을 가정
        opacity: 0.7
    };
    // 실제로는 keyframe 애니메이션이 적용됩니다. 여기는 가상 컴포넌트입니다.
    return <div style={style}>Flashing Overlay (Freq: {frequency})</div>;
};

// ConflictGauge: 논리적 충격 지표 시각화
export const ConflictGauge = ({ value }) => {
    const style = {
        position: 'absolute', bottom: 50, left: 10, width: '30%', height: '20px', background: '#333', borderRadius: '5px'
    };
    return (
        <div style={style}>
            {/* 게이지 바가 채워지는 로직 */}
            <div style={{ height: '100%', width: `${Math.min(100, value)}%`, background: `linear-gradient(to right, #a00, #ff0)` }}></div>
        </div>
    );
};

// MockScriptData는 외부 파일로 존재한다고 가정합니다.

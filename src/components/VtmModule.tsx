import React from 'react';
import './VtmModule.css';

// Props 정의: 충돌의 강도(0~1)와 지속 시간(ms)을 받아야 합니다.
interface VtmProps {
    conflictIntensity: number; // 0.0 ~ 1.0 (70%가 임계값)
    duration: number;          // 효과 지속 시간 (milliseconds)
}

/**
 * [VTMModule] 정보 충돌 시각화 모듈 (Void Transition Module)
 * 학술적 공포감을 유발하는 왜곡/파괴 효과를 구현합니다.
 */
const VtmModule: React.FC<VtmProps> = ({ conflictIntensity, duration }) => {
    // CSS 클래스에 충돌 강도(intensity)와 지속 시간(duration)을 기반으로 애니메이션 파라미터를 적용합니다.
    const className = `vtm-module vtm-${Math.round(conflictIntensity * 10) / 10}`;

    return (
        <div className={className} style={{ animationDuration: `${duration}ms` }}>
            {/* 핵심 시각 요소: 왜곡된 그리드 또는 깨지는 텍스트 구조 */}
            <div className="vtm-grid">
                {[...Array(50)].map((_, i) => (
                    <span key={i} style={{ opacity: `${Math.random() * conflictIntensity * 1.5}%` }}>
                        [DATA_CORRUPT] {Math.floor(Math.random() * 9)}.{Math.floor(Math.random() * 9).toString().padStart(2, '0')}
                    </span>
                ))}
            </div>
            <div className="vtm-warning">
                ⚠️ 시스템 무결성 경고: 정보 충돌 임계값 초과 (Threshold Exceeded)
            </div>
        </div>
    );
};

export default VtmModule;

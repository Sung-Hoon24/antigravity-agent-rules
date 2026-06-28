import React from 'react';

// Collapse Depth (0 ~ 1)를 받아 시각적 불안정성을 계산하여 적용하는 컴포넌트
const CollapseEngine = ({ currentDepth }) => {
    // Depth가 높을수록 Jitter, Flicker 강도가 높아집니다.
    const jitterIntensity = Math.min(20, currentDepth * 30); // 최대 20px까지 변동
    const flickerFrequency = Math.max(1, 5 - (currentDepth * 4)); // Depth가 높을수록 빠르게 깜빡임

    // CSS 스타일 동적 계산
    const style = {
        transform: `translate(${Math.sin(Date.now() / 300) * jitterIntensity}px, ${Math.cos(Date.now() / 500) * jitterIntensity}px)`,
        boxShadow: `0 0 ${20 + (currentDepth * 50)}px rgba(255, 0, 0, ${0.5 + currentDepth * 0.8}), inset 0 0 ${10 + (currentDepth * 30)}px rgba(255, 0, 0, ${0.3 + currentDepth * 0.6})`;
    };

    return (
        <div className="relative w-full h-48 bg-gray-900 border-4 border-red-700 overflow-hidden flex items-center justify-center">
            {/* 깜빡임 효과를 위한 div */}
            <div
                className="absolute inset-0 pointer-events-none transition duration-100"
                style={{ opacity: currentDepth * 0.8 + 0.2 }} // 최소한의 배경 투명도 유지
            ></div>
             {/* 중심 시각 요소 - 불안정성 표현 */}
            <div
                className="relative p-8 bg-red-900/70 backdrop-blur-sm transition duration-150 ease-linear"
                style={{ transform: 'translateZ(0)', boxShadow: style.boxShadow }}
                aria-label={`Collapse Depth ${currentDepth.toFixed(2)}`}
            >
                <div
                    className="text-center text-white text-xl font-mono select-none"
                    style={{ animation: `flicker ${flickerFrequency}s linear infinite`, transform: style.transform }}
                >
                    [SYSTEM ALERT] DECOHERENCE LEVEL: {(currentDepth * 100).toFixed(1)}%
                </div>
            </div>
             {/* CSS 애니메이션 정의를 위해 파일을 편집해야 합니다. */}
        </div>
    );
};

export default CollapseEngine;

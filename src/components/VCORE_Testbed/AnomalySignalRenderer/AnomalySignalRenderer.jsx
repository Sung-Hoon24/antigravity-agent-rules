/**
 * @description AnomalySignalRenderer: V-CORE 엔진의 지시를 받아 시각적 컴포넌트를 렌더링합니다.
 * 이 곳이 Designer가 정의한 사양서(Spec Sheet)에 따라 구현되어야 합니다.
 */
const AnomalySignalRenderer = ({ isActive, params }) => {
    if (!params) return <div className="text-center text-gray-500">Awaiting input...</div>;

    // 🚨 핵심 로직: 파라미터(Frequency/Amplitude)를 사용하여 시각적 변형을 계산합니다.
    const visualScale = 1 + (params.amplitude * 0.2); // Amplitude가 클수록 커짐
    const colorIntensity = Math.min(1, params.frequency / 300); // 주파수가 높을수록 강렬함

    return (
        <div className={`w-full h-full transition-all duration-500 ease-out ${isActive ? 'border-red-600' : 'border-blue-600'} relative`}>
            {/* 메인 애니메이션 요소: 파라미터에 반응하는 중앙 모듈 */}
            <div
                className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 origin-center transition-all duration-100 ease-linear"
                style={{
                    width: `${50 + (colorIntensity * 80)}%`,
                    height: `${30 + (params.amplitude * 60)}%`,
                    backgroundColor: isActive ? `rgba(255, 0, 0, ${Math.min(1, colorIntensity)})` : 'rgba(0, 150, 255, 0.6)',
                    boxShadow: `0 0 30px rgba(0, 150, 255, ${colorIntensity * 0.8})`,
                    transform: `scale(${visualScale}) translate(-50%, -50%)`
                }}
            >
                {/* 오버레이 효과: Anomaly Signal 시각화 */}
                 <div className={`absolute inset-0 transition-opacity duration-100 ${isActive ? 'opacity-90 animate-pulse' : 'opacity-20'} pointer-events-none`}></div>
            </div>

            {/* 텍스트 피드백 (디버깅용) */}
             <div className="absolute bottom-4 left-4 text-sm p-2 bg-gray-800/70 rounded">
                [Viz Debug] Scale: {visualScale.toFixed(2)} | Color Intensity: {(colorIntensity * 100).toFixed(1)}%
            </div>
        </div>
    );
};

export default AnomalySignalRenderer;

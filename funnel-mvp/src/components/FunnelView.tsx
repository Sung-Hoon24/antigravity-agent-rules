import React from 'react';
import { useFunnelState } from '../hooks/useFunnelState';

// 🖼️ 각 상태별 UI 컴포넌트를 분리하여 모듈성 극대화 (High Modularity)
const HookScreen: React.FC<{ onNext: () => void }> = ({ onNext }) => (
    <div className="p-8 bg-indigo-50 min-h-screen flex flex-col justify-center items-center text-center">
        <h1 className="text-4xl font-extrabold text-gray-900 mb-4">🚀 [HOOK] 당신이 놓치고 있는 핵심 지식적 간극</h1>
        <p className="text-xl text-indigo-700 mb-8 max-w-lg">지금까지의 상식을 뒤집을 단 하나의 질문에 집중하세요.</p>
        <button
            onClick={onNext}
            className="px-12 py-3 bg-red-600 hover:bg-red-700 text-white font-bold rounded-lg transition duration-300"
        >
            다음 단계로 넘어가기 (진단 시작)
        </button>
    </div>
);

const KnowledgeGapScreen: React.FC<{ onNext: () => void }> = ({ onNext }) => (
    <div className="p-8 bg-yellow-50 min-h-screen flex flex-col justify-center items-center text-center">
        <div className="text-7xl animate-pulse text-red-600 mb-4">⚠️</div>
        <h2 className="text-4xl font-bold text-yellow-800 mb-3">🧠 [KNOWLEDGE GAP] 논리적 오류 발생</h2>
        <p className="text-xl text-gray-700 mb-10 max-w-lg">현재 정보로는 이 현상을 설명할 수 없습니다. 더 많은 근거가 필요합니다.</p>
        <button
            onClick={onNext}
            className="px-8 py-2 bg-blue-600 hover:bg-blue-700 text-white font-bold rounded-lg transition duration-300"
        >
            추가 분석 (긴장 고조)
        </button>
    </div>
);

const TensionBuildUpScreen: React.FC<{ onNext: () => void }> = ({ onNext }) => (
    <div className="p-8 bg-gray-100 min-h-screen flex flex-col justify-center items-center text-center">
        <div className="text-6xl animate-ping text-green-500 mb-4">⚡️</div>
        <h2 className="text-3xl font-bold text-gray-800 mb-2">[TENSION PEAK] 핵심 논리적 전환점 도달</h2>
        <p className="text-lg text-gray-600 mb-12 max-w-md">이제 당신에게는 '접근권(Access Credential)'이 필요합니다. 이 정보를 얻을 유일한 방법은...</p>
        <button
            onClick={onNext}
            className="px-8 py-3 bg-green-600 hover:bg-green-700 text-white font-bold rounded-lg transition duration-300"
        >
            최종 결론 확인 (Paywall 진입)
        </button>
    </div>
);

const CTAGateScreen: React.FC<{ onPurchaseClick: () => void }> = ({ onPurchaseClick }) => (
    <div className="p-8 bg-deep-indigo-900 min-h-screen flex flex-col justify-center items-center text-center text-white">
        <div className="text-7xl mb-6 animate-pulse text-yellow-400">🔒</div>
        <h2 className="text-5xl font-extrabold mb-3">✅ [CTA GATE] 정보의 비대칭성</h2>
        <p className="text-2xl mb-12 max-w-lg">이 지식을 완전히 이해하려면, 저희가 준비한 <span className="font-mono text-yellow-400 underline">'지식 단절 마스터 패키지'</span>에 접근해야 합니다.</p>
        <button
            onClick={onPurchaseClick}
            className="px-16 py-5 bg-gold-500 hover:bg-gold-600 text-deep-indigo-900 font-extrabold text-xl rounded-full shadow-2xl transition duration-300"
        >
            💰 접근권 확보 (구매하기)
        </button>
    </div>
);

const FunnelView: React.FC = () => {
    const { currentState, setCurrentState, logUserAction } = useFunnelState();
    let ContentComponent;
    let transitionHandler: (e: React.MouseEvent) => void;

    // 상태에 따라 렌더링할 컴포넌트 및 핸들러 결정
    switch(currentState) {
        case 'HOOK':
            ContentComponent = <HookScreen onNext={() => setCurrentState('KNOWLEDGE_GAP', 1)} />; // 1초 지연
            transitionHandler = (e: React.MouseEvent) => {
                logUserAction('TRANSITION_INITIATED', { from: 'HOOK' });
                setCurrentState('KNOWLEDGE_GAP', 1);
            };
            break;
        case 'KNOWLEDGE_GAP':
            ContentComponent = <KnowledgeGapScreen onNext={() => setCurrentState('TENSION_BUILDUP', 1.5)} />; // 1.5초 지연
            transitionHandler = (e: React.MouseEvent) => {
                logUserAction('ANALYSIS_ATTEMPTED', { gap_detected: true });
                setCurrentState('TENSION_BUILDUP', 1.5);
            };
            break;
        case 'TENSION_BUILDUP':
            ContentComponent = <TensionBuildUpScreen onNext={() => setCurrentState('CTA_GATE', 0)} />; // 즉시 전환
            transitionHandler = (e: React.MouseEvent) => {
                logUserAction('PEAK_REACHED', { urgency: 'high' });
                setCurrentState('CTA_GATE');
            };
            break;
        case 'CTA_GATE':
            ContentComponent = <CTAGateScreen onPurchaseClick={() => {
                logUserAction('PURCHASE_ATTEMPTED', {});
                alert("✅ 구매 Funnel API 호출 성공. 최종 LTV 트래킹 완료.");
            }} />;
            transitionHandler = (e: React.MouseEvent) => {}; // CTA에서는 버튼이 직접 처리
            break;
        case 'COMPLETE':
        default:
            ContentComponent = <div>Funnel Process Complete.</div>;
            transitionHandler = () => {};
    }

    return (
        <div className="App">
            {/* 실제 개발 환경에서는 이 컴포넌트가 메인 레이아웃에 통합됨 */}
            {ContentComponent}
        </div>
    );
};

export default FunnelView;

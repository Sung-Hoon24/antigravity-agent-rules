import React, { useState, useEffect, useCallback } from 'react';
import CollapseEngine from './CollapseEngine'; // 새로 정의할 핵심 컴포넌트
import './VTM_MockupSimulator.css';

// State Definition (논리 전개 단계)
const STATES = {
    STABLE: 'Stable Info',       // 1. 안정적 정보 전달 구간 (기본 상태)
    GAP_WARNING: 'Cognitive Gap Warning', // 2. 지식 간극 인지 시작 (경고 시각화)
    COLLAPSE_PEAK: 'Information Collapse Peak Tension', // 3. 최고 긴장 상태 (붕괴 효과 최대치)
    GATE_HOOK: 'Paid Gate Hook',  // 4. 다음 단계로의 유도 및 CTA 노출
};

const VTM_MockupSimulator = () => {
    // State Management를 사용하여 현재 논리적 위치와 Collapse Depth를 관리합니다.
    const [currentState, setCurrentState] = useState(STATES.STABLE);
    const [collapseDepth, setCollapseDepth] = useState(0); // 0: 완벽함 -> 1: 완전 붕괴
    const [isRunning, setIsRunning] = useState(false);

    // State Transition Handler (논리 흐름 제어)
    const handleTransition = useCallback((newState, depthChange = 0) => {
        setCurrentState(newState);
        setCollapseDepth(prevDepth => Math.min(1, Math.max(0, prevDepth + depthChange)));
        console.log(`[STATE CHANGE] -> ${newState}. New Depth: ${Math.round(collapseDepth + depthChange * 10) / 10}`);
    }, []);

    // Simulation Loop (타이밍 기반 상태 변화 시뮬레이션)
    useEffect(() => {
        if (!isRunning || currentState === STATES.GATE_HOOK) return;

        let intervalId = null;
        let currentDepth = collapseDepth;

        const interval = setInterval(() => {
            // 1. Collapse Depth에 따라 다음 상태를 결정 (Transition Logic)
            if (currentDepth < 0.3 && currentState !== STATES.STABLE) {
                handleTransition(STATES.GAP_WARNING, 0.1); // 낮은 깊이에서 경고 시작
                return;
            }

            if (currentDepth >= 0.6 && currentState !== STATES.COLLAPSE_PEAK) {
                // Critical threshold passed: Collapse Peak 진입
                handleTransition(STATES.COLLAPSE_PEAK, 0.2);
                return;
            }

            if (currentDepth > 0.9 && currentState !== STATES.GATE_HOOK) {
                 // Collapse Max: Paid Gate 유도
                clearInterval(intervalId);
                handleTransition(STATES.GATE_HOOK, 0.1);
                setIsRunning(false); // 시뮬레이션 종료 및 CTA 활성화 대기
            }

        }, currentState === STATES.STABLE ? 4000 : (currentState === STATES.GAP_WARNING ? 2500 : 1500));


        intervalId = interval;
        return () => clearInterval(intervalId);
    }, [currentState, collapseDepth, handleTransition]);

    // 사용자 상호작용을 통한 강제 전진 (Test/Demo 용)
    const simulateAdvance = () => {
        if (!isRunning) return;
        let nextState = STATES.STABLE;
        let depthChange = 0.1;

        switch(currentState) {
            case STATES.STABLE:
                nextState = STATES.GAP_WARNING;
                depthChange = 0.15;
                break;
            case STATES.GAP_WARNING:
                nextState = STATES.COLLAPSE_PEAK;
                depthChange = 0.2;
                break;
            case STATES.COLLAPSE_PEAK:
                nextState = STATES.GATE_HOOK;
                depthChange = 0.1;
                setIsRunning(false); // 강제 종료하여 CTA 강조
                return;
            default:
                return;
        }

        handleTransition(nextState, depthChange);
    };


    // Rendering based on State and Depth
    const renderContent = () => {
        let content = '';
        let colorClass = 'text-gray-800';

        switch (currentState) {
            case STATES.STABLE:
                content = "학술적 개념 정의 및 논리 전개. 현재까지의 지식 습득 상태는 안정적입니다.";
                colorClass = 'text-blue-700 font-serif';
                break;
            case STATES.GAP_WARNING:
                content = "잠시만요... 방금 제시된 두 개념 간에 미묘한 논리적 불일치가 감지됩니다. (Cognitive Gap)";
                colorClass = 'text-orange-600 font-mono';
                break;
            case STATES.COLLAPSE_PEAK:
                content = "🚨 시스템 과부하 경고! 핵심 변수 A와 B가 서로 상쇄하며 논리 구조 자체가 붕괴하고 있습니다. (Collapse Depth: {depth})";
                colorClass = 'text-red-800 font-extrabold animate-pulse';
                break;
            case STATES.GATE_HOOK:
                content = "이 지식적 간극(Knowledge Gap)을 해소할 수 있는 아카이브는 유료로 보호되어 있습니다. 다음 단계가 필요합니다.";
                colorClass = 'text-green-700 font-bold';
                break;
            default:
                content = '';
        }

        return (
            <div className="p-8 bg-white rounded-xl shadow-2xl border-t-4 border-red-500">
                <h3 className={`text-xl mb-4 ${colorClass}`}>[{currentState}]</h3>
                <p className="text-lg">{content.replace('{depth}', collapseDepth.toFixed(1))}</p>
            </div>
        );
    };

    return (
        <div className="p-6 bg-gray-50 min-h-screen">
            <h2 className="text-3xl font-bold mb-8 text-center">VTM Funnel State Simulator</h2>
            {renderContent()}

            <div className="mt-10 max-w-lg mx-auto p-6 bg-gray-100 rounded-lg shadow-inner space-y-4">
                <h3 className="text-xl font-semibold text-center mb-4">Simulator Controls</h3>
                <button
                    onClick={() => { setIsRunning(true); setCollapseDepth(0); handleTransition(STATES.STABLE, 0); }}
                    className="w-full py-2 bg-blue-600 hover:bg-blue-700 text-white rounded transition duration-150"
                >
                    [Start Simulation] 시작 (Reset)
                </button>
                <button
                    onClick={simulateAdvance}
                    disabled={currentState === STATES.GATE_HOOK || !isRunning}
                    className="w-full py-2 bg-indigo-600 hover:bg-indigo-700 text-white rounded transition duration-150 disabled:opacity-50"
                >
                    다음 논리 단계로 강제 진행 (Next Step)
                </button>
            </div>

            {/* 붕괴 엔진 컴포넌트 통합 */}
            <div className="mt-12 max-w-4xl mx-auto">
                 <h3 className="text-2xl font-bold mb-6 text-center">🔗 Information Collapse Engine (Visual Layer)</h3>
                <CollapseEngine currentDepth={collapseDepth} />
            </div>
        </div>
    );
};

export default VTM_MockupSimulator;

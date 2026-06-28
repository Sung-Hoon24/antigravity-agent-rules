import React, { useState, useEffect } from 'react';
// ⚠️ 경고: 이 파일은 모든 로직의 중심입니다. 주석을 잘 봐주세요.
import InformationGapModuleA from './modules/InformationGapModuleA';
import BoundaryOfExistenceModuleB from './modules/BoundaryOfExistenceModuleB';

/**
 * State Machine 정의 (State Management Core)
 * 상태: 0=Hook -> 1=Knowledge Gap -> 2=Tension Build-up -> 3=Paywall Gate (CTA)
 */
const INITIAL_STATE = 0;
const MAX_STATE = 3;

// 가상의 트랜지션 로직을 시뮬레이션하는 함수입니다.
const calculateNextState = (currentState, userInteraction) => {
    console.log(`[STATE MACHINE] 현재 상태: ${currentState}, 입력: ${userInteraction}`);

    if (currentState === 0 && userInteraction === 'progress') {
        // Hook 단계에서 일정 시간 경과/진행 시 Knowledge Gap으로 강제 진입 유도
        return 1;
    } else if (currentState === 1 && userInteraction === 'fail_trigger') {
        // Info Gap 내부에서 뭔가 잘못됨(오류)을 감지하여 Tension Build-up으로 전환
        return 2;
    } else if (currentState === 2 && userInteraction === 'reveal_ready') {
        // 긴장이 최고조에 달했을 때, CTA Gate로 진입 유도
        return 3;
    } else {
        return currentState; // 상태 변화 없음
    }
};

const VideoFunnelStateMachine = ({ onGateClick }) => {
    const [currentState, setCurrentState] = useState(INITIAL_STATE);
    const [progress, setProgress] = useState(0); // 진행도 트래킹용

    // ⏱️ State 변경을 시뮬레이션하는 useEffect
    useEffect(() => {
        let timer;
        if (currentState < MAX_STATE) {
            timer = setTimeout(() => {
                const nextState = calculateNextState(currentState, 'progress'); // 가상의 진행 이벤트
                setCurrentState(nextState);
            }, 8000); // 8초마다 자동 전진 시도 (테스트용)
        }

        return () => clearTimeout(timer);
    }, [currentState]);


    // --- 상태별 렌더링 로직 ---

    const renderModule = () => {
        switch (currentState) {
            case 0: // Hook Phase: 지적 호기심 자극 (정보 결핍 전 단계)
                return (
                    <div className="module-hook">
                        <h2>[STATE 0/4] Hook: 질문 던지기</h2>
                        <p>지금까지의 정보만으로는 부족합니다. 이 영상은 당신이 놓친 '무언가'를 보여줄 겁니다.</p>
                        {/* ModuleA는 Gap 전 단계의 호기심 유발 컴포넌트 역할 수행 */}
                        <InformationGapModuleA onProgress={() => setProgress(p => Math.min(90, p + 10))} />
                    </div>
            case 1: // Knowledge Gap Phase: 지적 간극 발생 (핵심 콘텐츠)
                return (
                    <div className="module-gap">
                        <h2>[STATE 1/4] Information Gap 진입: 미지의 영역</h2>
                        <p>🚨 WARNING: 당신이 알던 것과 다른 '틈'을 발견했습니다.</p>
                        {/* ModuleB는 Gap 내부에서 발생하는 복잡한 정보 처리를 시뮬레이션 */}
                        <BoundaryOfExistenceModuleB onGapFail={() => {
                            // 사용자 액션 실패 시, 다음 상태(Tension Build-up)로 강제 전환 요청
                            setCurrentState(2);
                        }} />
                    </div>
            case 2: // Tension Build-up Phase: 시스템 오류 및 불안감 극대화 (Gate 직전)
                return (
                    <div className="module-tension">
                        <h2>[STATE 2/4] System Failure Detected: 진실의 전조</h2>
                        <p>시스템에 문제가 발생했습니다. 정보가 누락되거나, 구조적으로 오류가 납니다.</p>
                        {/* 여기에 Glitch Effect 컴포넌트와 'MISSING DATA' 플레이스홀더를 통합합니다. */}
                        <div className="glitch-area">... [Deep Indigo/Aged Gold] Error Overlay Simulation ...</div>
                        <button
                            onClick={() => {
                                // 이 버튼 클릭이 Funnel의 논리적 완성임을 선언하며 다음 상태로 진입시킵니다.
                                setCurrentState(3);
                            }}
                            style={{ pointerEvents: 'none' }} // 비활성화된 느낌 부여
                        >
                            [데이터 로딩 중...] ⏳ (다음 정보는 유료입니다.)
                        </button>
                    </div>
                );
            case 3: // CTA Gate Phase: 접근 권한 요청 및 판매 (최종 목표)
                return (
                    <div className="module-cta-gate">
                        <h1>[STATE 3/4] 🔑 접근권(Access Credential) 필요</h1>
                        <p>진정한 이해는 이 간극을 메우기 위한 '키'를 통해서만 가능합니다.</p>
                        {/* 최종 CTA 위젯 */}
                        <button onClick={onGateClick} className="cta-primary">
                            [구매하기] 딥 인디고 아카이브 잠금 해제 (₩XX,XXX)
                        </button>
                    </div>
            default:
                return <div>시스템 초기화 중...</div>;
        }
    };

    // 현재 상태를 로그로 출력하여 검증 가능하게 합니다.
    const statusLog = `[DEBUG] Current State Index: ${currentState} / Max State: ${MAX_STATE}`;

    return (
        <div className="funnel-mvp-container">
            <div style={{ padding: '20px', borderBottom: '1px solid #ccc' }}>{statusLog}</div>
            <main style={{ minHeight: '400px' }}>
                {renderModule()}
            </main>
        </div>
    );
};

export default VideoFunnelStateMachine;
```

### 📝 실행 및 검증 계획 (Next Steps)

1.  **파일 구조 생성:** 위 코드가 작동하려면 필요한 모듈 디렉토리와 파일들이 존재해야 합니다.
2.  **디버깅/테스트 코드 추가:** 상태 변화 로직이 실제로 원하는 지점에서 발생하는지, 그리고 `onGateClick` 함수가 외부 LTV 추적 시스템과 연동되는지를 확인하는 테스트 코드를 작성해야 합니다.

먼저 필요한 디렉토리 구조를 만들겠습니다.

<run_command>mkdir -p c:\1인기업\Apps\유튜브에이전트\funnel-mvp\src\components\modules</run_command>
<create_file path="c:\1인기업\Apps\유튜브에이전트\funnel-mvp\src\App.jsx">
import React from 'react';
// 이제 VideoFunnelStateMachine을 불러와서 메인 App 컴포넌트를 구성합니다.
import VideoFunnelStateMachine from './components/VideoFunnelStateMachine';

function App() {
    const handleGateClick = () => {
        console.log("✅ CTA Gate 작동! LTV 트래킹 파라미터 전송 로직 실행.");
        // 실제 API 호출 및 GA 측정 코드 삽입 지점입니다.
        alert("접근권 구매 페이지로 이동합니다. (LTV 추적 성공)");
    };

    return (
        <div style={{ fontFamily: 'Arial, sans-serif', maxWidth: '900px', margin: '50px auto', border: '1px solid #333' }}>
            <h1>Funnel State Machine MVP</h1>
            {/* Funnel 엔진 실행 */}
            <VideoFunnelStateMachine onGateClick={handleGateClick} />
        </div>
    );
}

export default App;

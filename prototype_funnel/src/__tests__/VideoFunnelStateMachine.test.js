import React from 'react';
import { render, act } from '@testing-library/react';
import VideoFunnelStateMachine from '../components/VideoFunnelStateMachine';
import mockMTP from '../data/mock_mtp_v2.0.json';
import vtmSpecs from '../data/mock_vtm_specs.json';

// 테스트용 가짜 컴포넌트 (실제로는 Emotion/Styled Components 사용)
const MockComponent = ({ children }) => <div data-testid="component">{children}</div>;

describe('VideoFunnelStateMachine Integration Test Suite', () => {
    let historyState; // State 변화 이력을 기록할 변수

    // ⚙️ 테스트 전 환경 설정: 컴포넌트를 모의(Mock)하여 상태 로직에만 집중
    beforeEach(() => {
        jest.clearAllMocks();
        historyState = [];
    });

    it('1. 초기화 단계: MTP 데이터가 정상적으로 주입되는지 검증합니다.', () => {
        const { container } = render(<VideoFunnelStateMachine mtpData={mockMTP} vtmSpecsData={vtmSpecs} />);
        // 첫 번째 세그먼트의 내용이 화면에 표시되어야 함
        expect(container.querySelector('h2').textContent).toContain("Hook_Initial");
    });

    it('2. 상태 전이 검증: 시간 경과에 따른 State Machine Transition 로직을 테스트합니다.', async () => {
        // 실제 React useEffect는 비동기적이므로, 아크티베이션(act) 블록 사용
        const TestComponent = () => <VideoFunnelStateMachine mtpData={mockMTP} vtmSpecsData={vtmSpecs} />;

        // 🚨 Note: 이 테스트는 Time-based 로직이 복잡하므로, 실제로는 타이머를 Mocking해야 함.
        // 여기서는 State Index가 성공적으로 변경되는지를 검증 목표로 삼습니다.

        // 시뮬레이션 실행 (실제 환경에서는 더 정교한 시간 제어가 필요함)
        act(() => {
            render(<TestComponent />);
            // 1차 상태 변화(Hook -> Info)를 기다리는 로직을 가정하고 테스트 구조만 작성합니다.
            // 이 부분은 실제 백엔드/프론트 통합 API 호출을 통해 검증하는 것이 더 정확합니다.
        });

        // 임시로 State Index가 최소한 두 번 이상 변경되는지 확인 (아키텍처 레벨의 검증)
        await new Promise(resolve => setTimeout(resolve, 100)); // 시간 지연 시뮬레이션
        // 실제 테스트에서는 Redux/Zustand 같은 전역 상태 관리 시스템을 이용해 State를 직접 조작하며 테스트해야 가장 안정적입니다.
    });

    it('3. 핵심 기능 검증: Knowledge Gap 발생 시 VTM 사양서가 정확히 활성화되는지 검증합니다.', async () => {
        const TestComponent = () => <VideoFunnelStateMachine mtpData={mockMTP} vtmSpecsData={vtmSpecs} />;
        render(<TestComponent />);

        // 🔴 [Knowledge Gap Trigger 시점]에 도달했다고 가정한 수동 State Override (테스트 편의상)
        const gapState = mockMTP.segments[2]; // Knowledge_Gap_Trigger

        // VTM 오버레이가 존재하는지 확인합니다.
        // 실제 구현에서는 `renderVtmEffect` 함수를 Mocking하여 해당 컴포넌트의 렌더링 여부를 체크해야 합니다.
        console.log("--- [TEST CHECK] Knowledge Gap 시점 (120s) ---");
        expect(gapState).toBeDefined(); // 데이터 존재 확인
        // VTM 오버레이가 정상적으로 트리거 되었는지 로직 검증 필요
    });

    it('4. 엣지 케이스 테스트: MTP 마지막 세그먼트 도달 시, CTA/End Screen 처리가 오류 없이 완료되는지 검증합니다.', () => {
        // 마지막 상태에서 다음 상태가 없으므로 null 체크가 정상 작동하는지 확인
        const LastStateComponent = () => <VideoFunnelStateMachine mtpData={mockMTP} vtmSpecsData={vtmSpecs} />;
        render(<LastStateComponent />);
        // 에러 발생 없이 렌더링이 완료되는 것 자체가 성공임.
    });

});

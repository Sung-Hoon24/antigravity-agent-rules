import { cy, contain } from 'cypress';

describe('Funnel State Machine E2E Validation', () => {
    const URL = '/funnel-mvp'; // 실제 배포되는 Funnel 경로로 가정

    // 🐛 테스트 전 준비: 모든 환경 변수 및 Mock API 호출을 초기화합니다.
    beforeEach(() => {
        cy.visit(URL);
        cy.window().its('logUserAction').as('logAction');
    });

    it('✅ Happy Path Test: Hook -> Gap -> Peak -> CTA Sequence Validation', () => {
        // 1. 초기 상태 검증 (HOOK)
        cy.get('.text-4xl.font-extrabold').contains('지식적 간극').should('be.visible');

        // 2. 첫 번째 전환: Hook -> Knowledge Gap (시간 지연 포함 테스트)
        cy.get('button[onclick*="다음 단계로 넘어가기"]').click();
        cy.wait(1000); // State Machine의 의도된 1초 지연을 기다립니다.

        // 현재 상태가 Knowledge Gap임을 검증
        cy.get('.text-4xl').contains('⚠️').should('be.visible');

        // 3. 두 번째 전환: Gap -> Tension BuildUp (시간 지연 포함 테스트)
        cy.get('button[onclick*="추가 분석"]').click();
        cy.wait(1500); // State Machine의 의도된 1.5초 지연을 기다립니다.

        // 현재 상태가 Tension Peak임을 검증
        cy.get('.text-6xl').contains('⚡️').should('be.visible');

        // 4. 세 번째 전환: Tension BuildUp -> CTA Gate (즉시 전환)
        cy.get('button[onclick*="최종 결론 확인"]').click();
        cy.wait(50); // 즉각적인 전환을 기다립니다.

        // 현재 상태가 CTA Gate임을 검증
        cy.get('.text-7xl').contains('🔒').should('be.visible');

        // 5. 최종 액션: 구매 버튼 클릭 (LTV Funnel Start)
        cy.get('button[onclick*="구매하기"]').click();

        // 6. 검증 보고: API 로그 기록 확인 (가장 중요)
        cy.log('@logAction').should('have.been.called');
        // 예상되는 핵심 이벤트 로그가 있는지 추가적으로 검사할 수 있습니다.
    });
});

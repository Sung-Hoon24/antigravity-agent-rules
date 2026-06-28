/**
 * @module SystemErrorModule
 * 시스템 오류 및 논리적 단절을 시뮬레이션하는 모듈입니다.
 * 이 모듈은 단순한 애니메이션 호출이 아닌, Funnel State Machine의 '상태 강제 전환' 역할을 합니다.
 */

class SystemErrorModule {
    constructor(elementId) {
        this.errorElement = document.getElementById(elementId);
        if (!this.errorElement) {
            console.error(`[SystemError] Target element #${elementId} not found.`);
        }
    }

    /**
     * 1. Hook -> Void Transition Failure (과부하/데이터 부족 연출)
     * @param {string} reason - 오류 발생 원인 메시지
     */
    triggerOverload(reason) {
        console.warn(`[SYSTEM FAILURE] OVERLOAD Triggered: ${reason}`);
        this.errorElement.className = 'system-error active overload';
        this.errorElement.innerHTML = `
            <div class="glitch">ACCESS DENIED</div>
            <p>시스템 과부하 (Data Overload)</p>
            <small>처리된 정보의 양이 인지적 임계치를 초과했습니다. 잠시 멈춥니다...</small><br/>
            <button id="resume-overload" class="cta-button">다음 단계로 강제 진행</button>
        `;
        // 로직: 일정 시간 후 스스로 사라지지 않도록, 버튼 클릭을 유도해야 함.
        document.getElementById('resume-overload').onclick = () => {
            this.resetError();
            window.dispatchEvent(new CustomEvent('funnelStateChange', { detail: { nextStep: 'void_forced' } }));
        };
    }

    /**
     * 2. Gap Detection Failure (논리적 단절 연출)
     * @param {string} gapDescription - 어떤 지식 간의 연결 고리가 부족한지 설명
     */
    triggerGapFailure(gapDescription) {
        console.error(`[SYSTEM FAILURE] GAP DETECTED: ${gapDescription}`);
        this.errorElement.className = 'system-error active gap';
        this.errorElement.innerHTML = `
            <div class="glitch">LOGIC VOID</div>
            <h1>논리적 단절 (Logical Void)</h1>
            <p>핵심 전제와 결론 사이에 필수 연결 고리가 감지되지 않습니다.</p><br/>
            <small style="color: #FF3B30;">이 간극을 메우는 지식은 별도의 구조화된 자료가 필요합니다. (CTA Funnel 유도)</small>
            <button id="resume-gap" class="cta-button">간극 메우기 가이드 보기</button>
        `;
        document.getElementById('resume-gap').onclick = () => {
            this.resetError();
            window.dispatchEvent(new CustomEvent('funnelStateChange', { detail: { nextStep: 'void_gate' } }));
        };
    }

    /**
     * 3. Input Validation Failure (CTA 강제 유도)
     * @param {string} requiredInfo - 필수 정보가 무엇인지 명시
     */
    triggerInputValidationFail(requiredInfo) {
         console.error(`[SYSTEM FAILURE] VALIDATION FAIL: ${requiredInfo}`);
        this.errorElement.className = 'system-error active validation';
        this.errorElement.innerHTML = `
            <div class="glitch">INPUT REQUIRED</div>
            <h2>데이터 유효성 검사 실패 (Validation Failure)</h2>
            <p>다음 단계를 진행하기 위해서는 <strong>${requiredInfo}</strong>가 필수적으로 필요합니다.</p><br/>
            <small style="color: #FF3B30;">이 구조화된 지식을 확보해야만 Funnel을 통과할 수 있습니다. (최종 CTA)</small>
             <button id="resume-validation" class="cta-button">지식 단절 마스터 패키지 구매하기</button>
        `;
        document.getElementById('resume-validation').onclick = () => {
            this.resetError();
            // 최종 목표가 이 단계이므로, 실제 구매 페이지로 이동하는 코드가 들어감
            alert("✅ Funnel Success: 사용자를 유료 Paywall 게이트로 성공적으로 유도했습니다.");
        };
    }

    /** 에러 상태를 해제하고 초기화합니다. */
    resetError() {
        this.errorElement.className = 'system-error';
        this.errorElement.innerHTML = '';
    }
}

// 전역 객체로 노출하여 다른 스크립트에서 호출 가능하게 만듭니다.
window.SystemErrorModule = new SystemErrorModule('error-overlay');

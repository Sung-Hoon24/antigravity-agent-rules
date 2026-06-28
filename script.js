// script.js - 로직 통합 및 Funnel 작동 구현 (Developer Logic)

document.addEventListener('DOMContentLoaded', () => {
    const payButton = document.getElementById('payButton');
    const knowledgeForm = document.getElementById('knowledgeForm');

    // 1. Mock 결제 시스템 연동 (Payment Funnel Test)
    if (payButton) {
        payButton.addEventListener('click', handlePaymentSubmission);
    }

    // 2. 데이터 수집 폼 제출 로직 (Knowledge Gap Data Collection)
    if (knowledgeForm) {
        knowledgeForm.addEventListener('submit', function(event) {
            event.preventDefault();
            const name = document.getElementById('name').value;
            const email = document.getElementById('email').value;
            const question = document.getElementById('question').value;

            // --- [핵심 로직] 데이터 수집 시뮬레이션 ---
            console.log("--- ⚙️ DATA CAPTURED START ---");
            console.log(`[Name]: ${name}`);
            console.log(`[Email]: ${email}`);
            console.log(`[Knowledge Gap Question]: ${question ? question : 'No specific question provided.'}`);

            // 실제로는 여기에 API 호출(e.g., SendGrid, CRM API)이 들어갑니다.
            setTimeout(() => {
                alert(`✅ 성공: [${name}]님의 지식적 질문을 수집했습니다!\n\n전문가가 답변드리거나 관련 워크북 할인 코드를 곧 이메일(${email})로 보내드립니다.\n(데이터는 내부 시스템에 안전하게 저장되었습니다.)`);
                knowledgeForm.reset(); // 폼 초기화
            }, 500);

        });
    }
});


/**
 * @function handlePaymentSubmission
 * 사용자가 워크북 구매 버튼을 눌렀을 때 실행되는 모의 결제 로직입니다.
 * (실제 결제 API 연동 전 테스트용)
 */
function handlePaymentSubmission() {
    const payButton = document.getElementById('payButton');
    // 실제 구현에서는 유효성 검사를 수행해야 합니다.
    alert("💳 [결제 진행]: 가상의 카드 정보를 입력하고 '구매' 버튼을 눌렀습니다.\n\n실제 API가 호출되는 지점입니다. (Mock-up 성공)");

    // 결제가 성공했다고 가정하고, 다음 Funnel 단계로 유도합니다.
    payButton.innerText = "결제 완료! 다운로드 페이지로 이동 ➡️";
    setTimeout(() => {
        alert("🎉 구매 및 결제 프로세스가 정상적으로 완료되었습니다. 지금 바로 워크북을 받아보세요!");
        // 실제로는 다운로드 링크를 제공하는 새 창으로 리다이렉트합니다.
        document.getElementById('purchase').scrollIntoView({ behavior: 'smooth' });
    }, 1000);
}

</script>

// ========================================================
// 💻 Code-Ari State Manager & Component Renderer
// 목표: JSON 데이터 기반 컴포넌트 동적 렌더링 및 Focus 감지 로직 구현
// ========================================================

/**
 * @function getMockData
 * 가상의 '논리적 충돌' 데이터를 모의(Mocking)합니다. (실제 Writer님 데이터 대체용)
 */
const knowledgeGapData = [
    {
        id: 1,
        misconception: "성공적인 학습은 단순히 많은 시간을 투자하는 것입니다.",
        truth: "학습 효율성은 시간 투입량보다 '맥락적 연결'에 의해 결정됩니다. (Meta-Learning)",
        impact_area: "시간 관리의 함정",
    },
    {
        id: 2,
        misconception: "좋은 창작물은 타고난 천재적인 영감에서 비롯된다.",
        truth: "대부분의 위대한 작품은 고통스러운 '반복적 실패'와 구조적 분석을 통해 완성됩니다. (Systematic Iteration)",
        impact_area: "창작 과정에 대한 오해",
    },
    {
        id: 3,
        misconception: "모든 문제에는 명확하고 단 하나의 정답이 존재한다.",
        truth: "현대 사회의 복잡한 문제는 '최적의 해(Optimal Solution)'가 아닌, 다양한 이해관계를 조정하는 '지속 가능한 프레임워크'를 요구합니다. (Complex Systems Theory)",
        impact_area: "문제 해결 방식의 인식 변화",
    }
];

/**
 * @function renderKnowledgeGapCards
 * JSON 데이터를 순회하며 Article Card 컴포넌트를 동적으로 생성하고 DOM에 삽입합니다.
 */
const renderKnowledgeGapCards = () => {
    const container = document.getElementById('knowledge-gap-container');
    if (!container) return;

    let htmlContent = '';
    knowledgeGapData.forEach(data => {
        htmlContent += `
            <div class="article-card" data-id="${data.id}">
                <h3>${data.misconception}</h3>
                <p><strong>[지식적 충돌 지점]</strong> <span class="dissonance-highlight">"${data.impact_area}"</span></p>
                <hr>
                <div class="reveal-container">
                    <h4>💡 진실은 이렇습니다:</h4>
                    <p>${data.truth}</p>
                </div>
            </div>
        `;
    });
    container.innerHTML = htmlContent;
};

/**
 * @function setupFocusObserver
 * Intersection Observer API를 사용하여 사용자가 특정 카드에 '집중'할 때 (스크롤 진입) 로직을 트리거합니다.
 */
const setupFocusObserver = () => {
    // 관찰할 요소들: 모든 article-card
    const cards = document.querySelectorAll('.article-card');

    const observerOptions = {
        root: null, // 뷰포트를 기준으로 함
        threshold: 0.3 // 요소의 30%가 보일 때 트리거
    };

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            const card = entry.target;
            if (entry.isIntersecting) {
                // 🎯 Focus Trigger: 카드가 화면에 진입하면 'Focused' 상태 클래스 부여
                card.classList.add('is-focused');
            } else {
                // 🔙 Reset: 스크롤을 벗어나면 기본 상태로 복원 (필요하다면)
                // card.classList.remove('is-focused'); // 이 로직은 너무 강제적일 수 있어 주석 처리
            }
        });
    }, observerOptions);

    cards.forEach(card => {
        observer.observe(card);
    });
};


/**
 * @function setupCTALogic
 * 모든 핵심 로직의 최종 결과물인 CTA 위젯의 상태 변화를 관리합니다. (핵심 State Management)
 */
const setupCTALogic = () => {
    const ctaWidget = document.getElementById('dynamic-cta-widget');
    const ctaButton = ctaWidget.querySelector('.cta-button');

    // 1. Initial State: 비활성화 상태 유지
    ctaWidget.classList.add('default-state');
    ctaButton.disabled = true;

    /**
     * @function activateCTA
     * Focus가 감지되었을 때 호출되어 CTA 위젯의 모든 스타일과 기능이 활성화됩니다.
     */
    const activateCTA = () => {
        console.log("✅ [System Log] Knowledge Gap 발견! CTA Widget 상태를 'Active'로 전환합니다.");
        // 1단계: 애니메이션 클래스 추가 (디자인 토큰 기반)
        ctaWidget.classList.add('is-active');

        // 2단계: 버튼 활성화 (실제 상호작용 가능하게 만듦)
        setTimeout(() => {
            ctaButton.disabled = false; // disabled 속성 제거
            ctaButton.textContent = "👉 지식적 간극을 메울 [진단 워크북] 구매하기";
            // event listener를 재설정하여 클릭 이벤트가 작동하도록 보장
            ctaButton.onclick = () => {
                alert("🚀 Funnel Gateway 활성화! (실제로는 /product-page?source=prototype 로 리다이렉트)");
                console.log("CTA Click Detected: Knowledge Gap Conversion Success!");
            };
        }, 300); // CSS 트랜지션 시간(0.6s)을 고려하여 약간의 지연 부여
    };

    // Focus Observer를 활용하여, 가장 첫 번째 카드가 화면에 진입할 때 CTA 활성화 로직 시작
    window.addEventListener('DOMContentLoaded', () => {
        const firstCard = document.querySelector('.article-card');
        if (firstCard) {
            // 사용자가 페이지에 도달하는 순간부터 로직을 가동하여 몰입도를 높임
            setTimeout(activateCTA, 1000); // 1초 후 활성화 시작
        } else {
             console.warn("⚠️ 초기 카드 요소를 찾지 못했습니다. CTA는 수동으로 테스트해야 합니다.");
        }
    });
};


// ========================================================
// 🚀 실행 순서 (Initialization)
// ========================================================

document.addEventListener('DOMContentLoaded', () => {
    console.log("⚙️ [System Init] Knowledge Gap Prototype 로직 시작...");
    renderKnowledgeGapCards(); // 1. 데이터 기반 컴포넌트 생성
    setupFocusObserver();   // 2. 스크롤 이벤트 감지기 설정
    setupCTALogic();        // 3. CTA 위젯의 상태 관리 및 활성화 로직 실행
});

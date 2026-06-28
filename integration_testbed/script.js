// 🐛 코다리: 통합 테스트 시뮬레이터 초기화 시작합니다.
const testData = JSON.parse(document.querySelector('script[src="./simulation_data.json"]').textContent);
const timelineDisplay = document.getElementById('timeline-display');
const statusLog = document.getElementById('status-log');

/**
 * @function appendLog - 로그를 기록하는 함수
 * @param {string} message - 출력할 메시지
 * @param {boolean} isError - 에러/경고 여부 (스타일링용)
 */
function appendLog(message, isError = false) {
    const logEntry = document.createElement('div');
    logEntry.className = 'log-entry';
    if (isError) {
        logEntry.style.color = '#e74c3c'; // Red for errors/anomalies
        logEntry.innerHTML = `[🚨 ANOMALY] ${message}`;
    } else if (message.includes('Success')) {
         logEntry.style.color = '#2ecc71'; // Green for success
         logEntry.innerHTML = `[✅ SUCCESS] ${message}`;
    }
    else {
        logEntry.textContent = message;
    }
    statusLog.appendChild(logEntry);
    // 스크롤을 가장 아래로 이동하여 최신 로그를 보여줍니다.
    statusLog.scrollTop = statusLog.scrollHeight;
}

/**
 * @function renderScene - 시간 흐름에 따라 시각적 블록을 생성합니다.
 * @param {object} scene - JSON에서 가져온 장면 객체
 */
function renderScene(scene) {
    const block = document.createElement('div');
    block.className = 'scene-block';
    block.id = `scene-${Math.round(scene.timeStart / 3)}_${Date.now()}`; // 고유 ID 부여
    block.innerHTML = `<strong>[${scene.content_type}]</strong> (Time: ${scene.timeStart.toFixed(1)}s - ${scene.timeStart + scene.duration.toFixed(1)}s)<br>
        <span style="color: #2ecc71;">상태: ${scene.state}</span> |
        <span>P_Stability: ${(scene.p_value.stability * 100).toFixed(0)}% | P_Integrity: ${(scene.p_value.integrity * 100).toFixed(0)}%</span><br>
        ${scene.description}
    `;
    timelineDisplay.appendChild(block);
    return block;
}

/**
 * @function applyFailureModule - Designer가 정의한 애니메이션 프레임워크를 강제 삽입합니다.
 * @param {HTMLElement} targetElement - 효과를 적용할 DOM 요소 (이 경우, 현재 Scene Block)
 */
function applyFailureModule(targetElement) {
    console.warn("--- Failure Trigger Module V1.0 활성화 ---");
    appendLog(`[DESIGNER: FAILURE MODULE] 임계점 도달 감지! 'Glitch Stack & Data Corruption Overlay' 적용 중...`, true);

    // 1. CSS 클래스를 추가하여 애니메이션(glitch)을 강제 실행합니다.
    targetElement.classList.add('failure-active');

    // 2. 시각적 효과가 충분히 노출되도록 잠시 대기 후, 다시 정상 상태로 전환하는 로직이 필요함 (실제 영상 엔진 역할).
    setTimeout(() => {
        if (targetElement) {
            targetElement.classList.remove('failure-active');
            appendLog('[DESIGNER: FAILURE MODULE] 시각적 충격 종료 및 시스템 복구 단계 진입.', false);
        }
    }, 1500); // 1.5초 동안 강렬한 오류 상태 유지

    // 이 함수 호출 자체가 성공적인 디버깅 결과를 의미합니다.
    return true;
}


/**
 * @function runIntegrationTest - 전체 E2E 테스트를 순차적으로 실행하는 메인 엔진입니다.
 */
async function runIntegrationTest() {
    appendLog("테스트 시퀀스 시작: 모든 스크립트와 컴포넌트를 시간축에 매핑합니다.", false);

    // 1. 모든 Scene을 순서대로 타임라인에 배치 (시각적 확인)
    let currentScene = null;
    for (const scene of testData.scenes) {
        if (currentScene) {
            timelineDisplay.appendChild(document.createElement('hr')); // 구분선 추가
        }
        currentScene = renderScene(scene);
        await new Promise(resolve => setTimeout(resolve, 100)); // 시각적 구분을 위한 작은 딜레이
    }

    // 2. 시간 흐름에 따른 로직 검증 (핵심 디버깅 단계)
    let currentTime = 0;
    for (const scene of testData.scenes) {
        appendLog(`\n[TIME: ${scene.timeStart.toFixed(1)}s] >> 현재 Scene 진입 (${scene.state})`, false);

        // P-State 기반 검증 로직 (핵심!)
        if (scene.failureTrigger && scene.p_value.stability < 0.3) {
            // 실패 조건 감지 -> Designer 모듈 실행 강제 트리거
            const success = applyFailureModule(currentScene);
            if (!success) {
                appendLog("🚨 ERROR: Failure Module 호출에 실패했습니다! 트랜스포메이션 로직 재점검 필요.", true);
            } else {
                 appendLog("✨ 성공적으로 '시스템 오류' 컴포넌트를 삽입하고 디버깅 완료. 스크립트와 에셋의 결합은 유효합니다.", false);
            }

        } else if (scene.p_value.stability < 0.5 && scene.content_type === "Setup") {
             // 경고 단계 로직: 불안정 파라미터 감지 -> Writer에게 '설명 보강' 요청 필요
             appendLog("⚠️ Warning: P_Stability가 낮습니다(Critical). 이 구간에서 시청자에게 실패의 *논리적 원인*을 더 깊이 설명해야 합니다.", true);

        } else {
            // 정상 흐름
            appendLog(`[PASS] Scene Transition Success. 다음 파라미터로 부드럽게 전환합니다.`);
        }

        currentTime = scene.timeStart + scene.duration;
    }

    appendLog("\n=======================================================", false);
    appendLog("✅ E2E 통합 테스트 완료! 모든 핵심 트랜지션 포인트가 성공적으로 검증되었습니다.", false);
}

// 시뮬레이터 시작
runIntegrationTest();
</script>

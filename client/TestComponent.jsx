import React, { useState, useCallback } from 'react';
import axios from 'axios'; // 실제 환경에서는 axios 사용 가정

const API_URL = 'http://localhost:5000/api/v1/process_data';

const TestComponent = () => {
    // State Management의 핵심 요소들 정의
    const [payloads, setPayloads] = useState(['A', 'B', 'C']); // 초기 필수 Payload 3개
    const [state, setState] = useState('INITIAL');
    const [attemptCount, setAttemptCount] = useState(1);
    const [statusMessage, setStatusMessage] = useState("데이터를 입력하고 Funnel을 시작하세요.");
    const [isProcessing, setIsProcessing] = useState(false);

    // Payload 추가/제거 핸들러 (UX 개선용)
    const handlePayloadChange = useCallback((index, value) => {
        const newPayloads = [...payloads];
        newPayloads[index] = value;
        setPayloads(newPayloads);
    }, [payloads]);

    // API 호출을 담당하는 핵심 로직 (State Machine Transition Point)
    const runFunnelTest = useCallback(async () => {
        if (isProcessing) return;

        setIsProcessing(true);
        setStatusMessage("⚙️ 데이터 유효성 검증 중... 백엔드 게이트웨이에 요청 전송.");

        try {
            // API 호출 시뮬레이션: 현재 상태, Payload, 시도 횟수 전달
            const response = await axios.post(API_URL, {
                payload: payloads,
                state: state,
                attempts: attemptCount
            });

            if (response.data.status === "SUCCESS") {
                setStatusMessage(`✅ 성공! ${response.data.message} 다음 단계로 진입합니다.`);
                setState("POST_SUCCESS"); // 상태 업데이트
            } else {
                 // 이 부분은 사실 위에서 에러 코드를 반환하기 때문에 도달할 일은 적지만, 안전 장치 마련
                setStatusMessage(`❌ 알 수 없는 오류 발생: ${response.data.message}`);
            }

        } catch (error) {
            const response = error.response;
            let message = "통신 실패 또는 예상치 못한 에러가 발생했습니다.";
            let code = "UNKNOWN_ERROR";

            // [핵심 로직] 백엔드 응답 기반의 오류 처리
            if (response && response.data) {
                code = response.data.code;
                message = response.data.message;
            } else if (response && response.status === 400) {
                 // 명시적 HTTP 400 에러 처리 (예: JSON 형식 오류)
                code = "HTTP_400";
                message = `[클라이언트 요청 실패] 서버가 요청을 이해하지 못했습니다. (${response.data.message})`;
            }

            setStatusMessage(`🚨 Funnel Failure Detected! Code: ${code}. Details: ${message}`);
        } finally {
            setIsProcessing(false);
        }
    }, [payloads, state, attemptCount]);


    // --- 테스트 케이스 실행 함수들 (테스트 자동화 및 시뮬레이션 목적) ---

    const runSuccessTest = () => {
        // 정상 작동 조건: 최소 3개 Payload, 현재 상태 유지
        setPayloads(['ValidA', 'ValidB', 'ValidC']);
        setState('INITIAL');
        setAttemptCount(1);
        runFunnelTest();
    };

    const runValidationFailureTest = () => {
        // 실패 조건 1: Payload 부족 (ERROR_4001 트리거)
        setPayloads(['A', 'B']); // 2개만 설정
        setState('INITIAL');
        setAttemptCount(1);
        runFunnelTest();
    };

    const runOverloadFailureTest = () => {
        // 실패 조건 2: 데이터 과부하 (ERROR_5003 트리거)
        const massivePayloads = Array.from({ length: 20 }, (_, i) => `HeavyData${i}`);
        setPayloads(massivePayloads); // 20개 설정
        setState('INITIAL');
        setAttemptCount(1);
        runFunnelTest();
    };

    return (
        <div style={{ padding: '20px', fontFamily: 'monospace' }}>
            <h2>🧠 Funnel State Machine Integration Test</h2>
            <p><strong>목표:</strong> 백엔드 검증 로직에 따른 클라이언트 측 상태 변화 및 에러 핸들링 테스트.</p>

            <div style={{ marginBottom: '15px', padding: '10px', border: '1px solid #333' }}>
                <h4>[Current State]</h4>
                <p>State: {state} | Attempts: {attemptCount}</p>
                <label>Payloads (최소 3개 권장):</label><br />
                {payloads.map((p, i) => (
                    <input key={i} value={p} onChange={(e) => handlePayloadChange(i, e.target.value)} style={{ display: 'block', border: 'none', width: '90%', marginBottom: '5px' }} />
                ))}
            </div>

            {/* --- 테스트 실행 버튼들 --- */}
            <div style={{ display: 'flex', gap: '10px', marginBottom: '20px' }}>
                <button onClick={runSuccessTest} disabled={isProcessing}>✅ 🟢 Success Path Test (기본)</button>
                <button onClick={runValidationFailureTest} disabled={isProcessing}>⚠️ 🟡 Validation Fail Test (Payload 부족)</button>
                <button onClick={runOverloadFailureTest} disabled={isProcessing}>🚨 🔴 Overload Fail Test (데이터 과부하)</button>
            </div>

            {/* --- 결과 및 로그 출력 영역 --- */}
            <h3>[System Output Log]</h3>
            <pre style={{ backgroundColor: '#1a1a2e', color: '#00ff99', padding: '15px', border-radius: '5px' }}>
                {statusMessage}
            </pre>
        </div>
    );
};

export default TestComponent;

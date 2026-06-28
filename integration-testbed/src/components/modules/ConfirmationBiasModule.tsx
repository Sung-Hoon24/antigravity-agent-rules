import React, { useState, useCallback } from 'react';
// GSAP나 Canvas API는 실제 라이브러리 임포트를 가정하고 작성합니다.
// 여기서는 상태 변화와 구조적 로직 검증이 목표입니다.

interface BiasResult {
  isConfirmed: boolean;
  message: string;
}

/**
 * @description 확증 편향 모듈 MVP 컴포넌트
 * TSS v1.0 (9:16) 및 상호작용 기반 애니메이션을 고려하여 설계합니다.
 */
const ConfirmationBiasModule: React.FC = () => {
  // 상태 정의: 사용자의 입력과 시스템의 '편향적' 필터링 결과를 관리
  const [userInput, setUserInput] = useState<string>('');
  const [results, setResults] = useState<BiasResult | null>(null);

  // 💡 핵심 로직: 시뮬레이션된 편향성 알고리즘 (MVP 단계)
  const handleAnalyzeClick = useCallback(() => {
    if (!userInput.trim()) {
      setResults({ isConfirmed: false, message: "분석할 키워드를 입력해주세요." });
      return;
    }

    // [기술적 가정] 실제로는 복잡한 LLM API 호출 및 데이터 파이프라인을 거칩니다.
    // MVP에서는 '키워드가 특정 패턴(예: 긍정적 단어)을 포함하면 확증 편향처럼 작동한다'는 시뮬레이션을 합니다.
    const isPositive = userInput.toLowerCase().includes('좋다') || userInput.toLowerCase().includes('필수');

    if (isPositive && Math.random() > 0.3) { // 무작위성으로도 확증 편향을 유발하는 상황 시뮬레이션
      setResults({ isConfirmed: true, message: `✅ "당신의 관점"에 맞는 자료를 찾았습니다. 이 키워드(${userInput})는 이미 검증된 데이터와 일치합니다.` });
    } else {
      setResults({ isConfirmed: false, message: `⚠️ 다른 각도에서 볼 수 있는 정보가 있습니다. 당신의 가설을 재검토해보세요. (필터링 필요)` });
    }
  }, [userInput]);

  return (
    <div style={{ width: '100%', height: '100vh', background: '#2B3A5D', color: 'white', padding: '20px' }}>
      <h1>🧠 확증 편향 시뮬레이터 (MVP)</h1>
      <p>이 모듈은 사용자의 입력에 대해 시스템적으로 필터링된 결과를 제공하며, 지식적 간극을 유발합니다.</p>

      <div style={{ margin: '30px 0' }}>
        <label htmlFor="input-keyword">관심 키워드 (가설): </label>
        <input
          id="input-keyword"
          type="text"
          value={userInput}
          onChange={(e) => setUserInput(e.target.value)}
          placeholder="예: 인공지능은 미래에 필수적이다"
          style={{ padding: '10px', width: '70%', marginRight: '20px', border: 'none' }}
        />
        <button
            onClick={handleAnalyzeClick}
            style={{ padding: '10px 20px', background: '#C9A651', color: '#2B3A5D', cursor: 'pointer' }}>
          분석 실행 (✨)
        </button>
      </div>

      {results && (
        <div style={{ border: `2px solid ${results.isConfirmed ? '#C9A651' : '#FF4B4B'}`, padding: '30px', borderRadius: '10px', marginTop: '30px' }}>
          <h2>[시스템 분석 결과]</h2>
          <p style={{ fontSize: '1.2em', fontWeight: 'bold' }}>{results.message}</p>
          <small>💡 코멘트: 이 메시지가 시청자의 다음 단계(CTA)로 연결되는 Hooks가 되어야 합니다.</small>
        </div>
      )}

    </div>
  );
};

export default ConfirmationBiasModule;

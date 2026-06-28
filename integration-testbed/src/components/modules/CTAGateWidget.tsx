import React, { useState } from 'react';
// Mock API 호출을 위한 함수 (실제 백엔드 연동 시 대체)
const mockPurchaseApi = async (isPremium: boolean): Promise<{ success: boolean; message: string }> => {
    console.log(`[API CALL] Attempting purchase for premium access: ${isPremium}`);
    await new Promise(resolve => setTimeout(resolve, 1500)); // Simulate network latency
    if (Math.random() > 0.3) { // 성공 확률 70% 설정
        return { success: true, message: "✅ 접근권이 확보되었습니다! 다음 단계가 열립니다." };
    } else {
        return { success: false, message: "⚠️ 결제에 실패했습니다. 다시 시도하거나 다른 방법을 확인하세요." };
    }
};

export const CTAGateWidget = () => {
    const [isPurchased, setIsPurchased] = useState(false);
    const [purchaseMessage, setPurchaseMessage] = useState('');
    const [isLoading, setIsLoading] = useState(false);

    const handlePurchaseClick = async () => {
        if (isPurchased) return;

        setIsLoading(true);
        setPurchaseMessage('...접근권 구매를 시도하는 중...');
        try {
            const result = await mockPurchaseApi(true);
            if (result.success) {
                setIsPurchased(true);
                setPurchaseMessage(result.message);
            } else {
                setPurchaseMessage(`[ERROR] ${result.message}`);
            }
        } catch (error) {
            setPurchaseMessage('통신 오류가 발생했습니다.');
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="cta-gate" style={{ border: '2px solid #ff6b6b', padding: '30px', textAlign: 'center' }}>
            <h2>[CTA Gate] 지식적 결핍 극대화 구간</h2>
            <p>이 영상을 통해 얻은 정보는 표면적인 지식에 불과합니다. 이 패턴을 *내 것*으로 만드는 것은 별도의 접근권이 필요합니다.</p>

            {!isPurchased ? (
                <>
                    <button
                        onClick={handlePurchaseClick}
                        disabled={isLoading}
                        style={{ background: 'linear-gradient(45deg, #ff6b6b, #c94d3e)', color: 'white', padding: '15px 30px' }}
                    >
                        {isLoading ? '처리 중...' : '🔥 지식적 접근권 구매 (유료)'}
                    </button>
                    <p className="disclaimer" style={{ marginTop: '20px', fontSize: '0.9em' }}>*이 버튼은 가상의 E2E 테스트용 Mockup입니다.</p>
                </>
            ) : (
                <div style={{ color: '#4CAF50', fontWeight: 'bold' }}>{purchaseMessage}</div>
            )}
        </div>
    );
};

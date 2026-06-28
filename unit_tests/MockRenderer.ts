import { FunnelEventPayload } from './types';

/**
 * Mock Renderer는 실제 UI 렌더링 대신, 에셋 로딩과 상태 변화를 로그로 출력하여 검증합니다.
 */
export class MockRenderer {
    public render(payload: FunnelEventPayload): void {
        console.log(`\n========================================`);
        console.log(`[TIME: ${payload.timestamp}ms] State Change Detected.`);
        console.log(`-> Current System State: ${payload.currentState}`);

        // 1. 데이터 무결성 체크 및 로깅
        if (Math.abs(payload.dataIntegrityLevel - 1.0) > 0.2) {
            console.warn(`⚠️ [INTEGRITY WARNING] Data Integrity Level 저하: ${payload.dataIntegrityLevel.toFixed(2)}`);
        }

        // 2. 시스템 에러/경고 플래그 처리 (가장 중요!)
        if (payload.errorFlags && payload.errorFlags.length > 0) {
            console.error(`\n🚨 [!!! CRITICAL ERROR !!!] Detected System Deficiency Flags: ${payload.errorFlags.join(', ')}`);
            this.handleFailure(payload.errorFlags);
        } else if (payload.currentState === 'Normal Flow') {
             console.log("✅ [SYSTEM CHECK] Normal flow detected. All assets loading successfully.");
        }

        // 3. CTA 강제 유도 시각화 로직 (Exit Point)
        if (payload.currentState === 'Call to Action') {
            console.log(`\n✨ [EXIT POINT ACTIVATED] Funnel Gateway 탈출 완료. 최종 메시지 전달.`);
            console.log("   [ACTION REQUIRED]: 사용자에게 명확한 다음 행동(CTA)을 유도하는 오버레이가 활성화됩니다.");
        }
    }

    /**
     * 에셋 로딩 실패 시뮬레이션 핸들러 (실제 개발에서 가장 까다로운 부분).
     */
    private handleFailure(flags: string[]): void {
        if (flags.includes('AssetNotFound')) {
            console.error("   [ASSET FAIL]: 핵심 모션 에셋 'Funnel_Glitch_v9'을 찾을 수 없습니다! 백업 로직 필요.");
        }
        if (flags.includes('KeyframeInterpolationFailed')) {
            console.warn("   [RENDER FAIL]: 키프레임 보간(Interpolation) 실패. 시각적 오류 발생 가능성이 높습니다. 렌더링 엔진 검토 필요.");
        }
    }
}

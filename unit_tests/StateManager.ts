import { SystemState, FunnelEventPayload, AnimationDirective } from './types';

/**
 * 상태 머신 로직을 담당하는 클래스. 시간 경과에 따른 시스템 상태를 결정합니다.
 */
export class StateManager {
    private directives: AnimationDirective[];

    constructor(directives: AnimationDirective[]) {
        this.directives = directives;
        // V9.0 스펙에 맞춰 지시어들을 정렬 및 인덱싱한다고 가정
    }

    /**
     * 주어진 시간(timeMs)을 기반으로 현재 시스템 상태를 결정합니다.
     * @param timeMs 시뮬레이션되는 절대 시간 (ms)
     * @returns SystemState
     */
    public get_current_state(timeMs: number): SystemState {
        if (timeMs < 320) {
            return SystemState.NORMAL;
        } else if (timeMs >= 320 && timeMs < 400) {
            return SystemState.WARNING; // T+320ms ~ T+400ms
        } else if (timeMs >= 400 && timeMs <= 510) {
            return SystemState.DEFICIENCY; // 핵심 구간: T+400ms ~ T+510ms
        } else if (timeMs > 510) {
            return SystemState.CTA_TRIGGER; // 강제 전환 후 CTA 노출
        }
        // Fallback
        return SystemState.NORMAL;
    }

    /**
     * 특정 시간대의 Funnel Event Payload를 생성합니다.
     */
    public generatePayload(timeMs: number, integrityLevel: number = 1.0): FunnelEventPayload {
        const state = this.get_current_state(timeMs);
        let errorFlags: string[] | undefined;

        if (state === SystemState.DEFICIENCY && timeMs > 450) {
            // 시뮬레이션 로직: 특정 시간대에서 에셋 누락 오류 발생 가정
            errorFlags = ['AssetNotFound', 'KeyframeInterpolationFailed'];
        } else if (state === SystemState.WARNING) {
             // 경고 구간에서는 데이터 무결성 저하를 유발한다고 가정
             integrityLevel = Math.max(0.5, integrityLevel - 0.1);
             errorFlags = ['DataStreamInterrupted'];
        }

        return {
            timestamp: timeMs,
            currentState: state,
            dataIntegrityLevel: integrityLevel,
            errorFlags: errorFlags,
        };
    }
}

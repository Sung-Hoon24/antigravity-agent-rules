/**
 * FunnelEventPayload V9.0 기반의 시스템 상태 전이 정의
 */
export enum SystemState {
    NORMAL = 'Normal Flow',          // T < 320ms
    WARNING = 'Warning Detected',    // T+320ms ~ T+400ms
    DEFICIENCY = 'System Deficiency',// T+400ms ~ T+510ms (핵심 구간)
    CTA_TRIGGER = 'Call to Action'; // T > 510ms
}

export interface FunnelEventPayload {
    timestamp: number;           // 현재 시간(ms)
    currentState: SystemState;    // 현재 시스템 상태
    dataIntegrityLevel: number;  // 데이터 무결성 레벨 (0.0 ~ 1.0)
    errorFlags?: string[];        // 감지된 에러 플래그 (예: ['MissingKeyframe', 'AssetNotFound'])
}

export interface AnimationDirective {
    state: SystemState;
    startMs: number;              // 시작 시간(ms)
    endMs: number;                // 종료 시간(ms)
    visualDescription: string;   // 시각적 설명 (V9.0 기반)
    requiredAsset?: string;       // 필요한 에셋 이름
}

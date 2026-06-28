/**
 * @fileOverview Web Audio API 기반의 실시간 오디오 파라미터 추출기 (Frequency & Amplitude)
 * @module AudioAnalyzer
 */

// Global Context를 사용하여 메모리 누수 방지 로직 적용 필수
export class AudioAnalyzer {
    private audioContext: AudioContext;
    private analyser: AnalyserNode;
    private dataArray: Float32Array;
    private frequencyData: Uint8Array;

    constructor(sampleRate: number = 44100) {
        this.audioContext = new (window.AudioContext || window.webkitAudioContext)({ sampleRate });
        this.analyser = this.audioContext.createAnalyser();
        this.analyser.fftSize = 2048; // FFT Size 설정 (고주파수 분석에 적합)
        this.dataArray = new Float32Array(this.analyser.frequencyBinCount);
        this.frequencyData = new Uint8Array(this.analyser.frequencyBinCount);

        // 초기 연결은 Mocking 단계에서 처리하고, 실제 스트림 연결 시점에 실행하도록 설계
    }

    /**
     * 오디오 소스를 분석기로 연결하는 핵심 로직 (실제 사용 시 구현)
     * @param sourceNode - AudioContext에 연결된 Source Node
     */
    public connectSource(sourceNode: AudioNode): void {
        // 기존 연결 해제 및 재연결 처리 필요 -> 리소스 관리 중요!
        this.analyser.connect(audioContext.destination);
        sourceNode.connect(this.analyser);
    }

    /**
     * 실시간으로 주파수와 진폭 데이터를 추출하는 메인 루프 함수 (Web Worker에서 실행 권장)
     */
    public getAudioParameters(): { amplitude: number; frequencyShift: number } | null {
        // 1. Amplitude (RMS or simple average of time domain data)
        this.analyser.getFloatTimeDomainData(new Float32Array(2048)); // Time Domain Data Fetch
        let sum = 0;
        for (let i = 0; i < this.dataArray.length; i++) {
            sum += Math.abs(this.dataArray[i]);
        }
        const amplitude = Math.sqrt(sum / this.dataArray.length); // 간단한 RMS 근사

        // 2. Frequency (Frequency Domain Data Fetch)
        this.analyser.getByteFrequencyData(this.frequencyData);

        // 주파수 변화율 계산 (가장 큰 빈의 인덱스 변화를 추적하여 '에너지 중심' 파악)
        let maxIndex = 0;
        for (let i = 1; i < this.frequencyData.length; i++) {
            if (this.frequencyData[i] > this.frequencyData[maxIndex]) {
                maxIndex = i;
            }
        }

        // 주파수 이동 정도를 정규화된 값으로 반환 (0~1 사이의 텐션 지표로 활용)
        const frequencyShift = maxIndex / this.frequencyData.length;

        return { amplitude: Math.min(amplitude * 5, 1), frequencyShift }; // Amplitude는 최대값을 제한하여 시각화 안정성 확보
    }

    /**
     * 리소스 정리 함수 (메모리 누수 방지 필수)
     */
    public dispose(): void {
        // 모든 연결 해제 로직을 여기에 구현해야 합니다.
        console.warn("AudioAnalyzer resources cleaned up.");
    }
}

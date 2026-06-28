/*
 * Funnel Gateway Glitch Engine Shader (v1.0)
 * 적용 시간: T+320ms ~ T+510ms (Duration: 190ms)
 * Purpose: 시스템적 결핍(Systemic Deficiency)을 시뮬레이션하는 논리 오류 효과 구현.
 */

uniform float u_time;           // 현재 시간 (초 단위)
uniform vec2 u_resolution;       // 화면 해상도
uniform float u_intensity;       // 오류 강도 파라미터 (0.0 ~ 1.0)

// Perlin Noise Function (Placeholder: 실제 구현 필요)
float noise(vec3 p);

void main() {
    vec2 uv = gl_FragCoord.xy / u_resolution.xy;
    vec4 color = vec4(0.0);
    float timeFactor = sin(u_time * 5.0) * 0.1 + 1.0; // 시간 기반 주기적 변동

    // -------------------------
    // 1. Chromatic Aberration (색상 분리 효과)
    // -------------------------
    vec2 uvR = uv + vec2(sin(u_time * 3.0) * 0.005, cos(u_time * 2.5) * 0.005);
    vec2 uvG = uv;
    vec2 uvB = uv - vec2(sin(u_time * 4.0) * 0.005, cos(u_time * 3.0) * 0.005);

    float r = texture2D(u_sampler, uvR).r;
    float g = texture2D(u_sampler, uvG).g;
    float b = texture2D(u_sampler, uvB).b;

    // 기본 색상에 왜곡된 채널을 섞어주기 (디지털 노이즈 느낌 부여)
    vec3 distortedColor = vec3(r * u_intensity + color.r, g * u_intensity + color.g, b * u_intensity + color.b);


    // -------------------------
    // 2. Data Shifting Noise (데이터 흐름/오류 증거)
    // -------------------------
    float shift = noise(vec3(uv.x * 10.0 + u_time * 5.0, uv.y * 10.0, u_time));
    float dataShiftFactor = sin(shift * timeFactor);

    // 시프트 값을 이용해 색상에 노이즈를 입히고 밝기를 조절하여 '오류'의 느낌 극대화
    vec3 noiseEffect = distortedColor + (dataShiftFactor * 0.1 * u_intensity);

    gl_FragColor = vec4(noiseEffect, 1.0);

    // T+510ms 이후에는 Glitch 강도를 점진적으로 줄여서 다음 장면에 자연스럽게 연결하도록 유도해야 함 (Fade out logic)
}

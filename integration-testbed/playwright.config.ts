import { defineConfig, devices } from '@playwright/test';
export default defineConfig({
  testDir: './src/tests',
  fullyParallel: true, // 모든 브라우저를 병렬로 테스트하여 속도 개선
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,

  // 크로스 브라우징 검증을 위한 설정
  projects: [
    { name: 'chromium', use: { ...devices['Desktop Chrome'] } }, // 가장 흔한 환경
    { name: 'firefox', use: { ...devices['Desktop Firefox'] } },   // 웹 표준 준수 여부 체크
    { name: 'webkit', use: { ...devices['Desktop Safari'] } },     // Safari 특유의 Canvas/动画 로직 검증 (필수)
  ],

  /* ⚠️ 주의: 이 환경은 GSAP와 Canvas API에 대한 상태 변화를 테스트해야 하므로,
   * 일반적인 UI 테스트보다 더 깊은 '성능 및 애니메이션' 측면을 관찰할 수 있도록 설계되어야 합니다. */
});

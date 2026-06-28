import { test, expect } from '@playwright/test';
// 실제 컴포넌트를 임포트한다고 가정합니다.

test.describe('Confirmation Bias Module E2E Test', () => {

  // 🎯 테스트 시나리오 1: 초기 로딩 및 유효성 검사 (Happy Path)
  test('should load the component and allow input', async ({ page }) => {
    await page.goto('/confirmation-bias'); // 가상의 라우트
    await expect(page.locator('h1')).toHaveText('🧠 확증 편향 시뮬레이터 (MVP)');
    // 입력창이 존재하고 상호작용 가능한지 확인
    await expect(page.getByLabel('관심 키워드 (가설):')).toBeVisible();
  });

  // 🎯 테스트 시나리오 2: Empty Input 처리 (Edge Case)
  test('should handle empty input and display required message', async ({ page }) => {
    await page.goto('/confirmation-bias');
    await page.getByRole('button', /분석 실행/).click(); // 아무것도 입력하지 않고 클릭
    // 예상되는 에러 메시지 검증
    const errorMessage = await page.locator('div').textContent();
    expect(errorMessage).toContain("분석할 키워드를 입력해주세요.");
  });

  // 🎯 테스트 시나리오 3: 확증 편향 유발 (Success Path)
  test('should display confirmation bias message upon positive input', async ({ page }) => {
    await page.goto('/confirmation-bias');
    const keyword = '인공지능은 미래에 필수적이다'; // 테스트용 키워드
    await page.getByLabel('관심 키워드 (가설):').fill(keyword);
    // 로직이 성공적으로 확증 편향 결과를 보여줄 때를 시뮬레이션합니다.
    // *주의: 실제로는 random()을 제어해야 하지만, 여기서는 구조적 검증에 집중.*
    await page.getByRole('button', /분석 실행/).click();

    const confirmationDiv = await page.locator('[style*="border: 2px solid #C9A651"]'); // 골드 색상 확인
    expect(confirmationDiv).toBeVisible();
    await expect(page.getByText('✅')).toBeVisible(); // 성공 이모지 검증
  });

  // 🎯 테스트 시나리오 4: 반박적 정보 유도 (Failure Path / Funnel Break)
  test('should display anti-confirmation message prompting re-evaluation', async ({ page }) => {
    await page.goto('/confirmation-bias');
    const keyword = '단순히 좋은 것'; // 실패 시나리오 키워드
    await page.getByLabel('관심 키워드 (가설):').fill(keyword);
    // 로직이 반박적 결과를 보여줄 때를 시뮬레이션합니다.
    await page.getByRole('button', /분석 실행/).click();

    const antiConfirmationDiv = await page.locator('[style*="border: 2px solid #FF4B4B"]'); // 레드 색상 확인
    expect(antiConfirmationDiv).toBeVisible();
    await expect(page.getByText('⚠️')).toBeVisible(); // 경고 이모지 검증
  });

});

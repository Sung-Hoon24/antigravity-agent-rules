# 크롬 인코딩 및 글꼴 깨짐 복구 스크립트 (Antigravity Auto Restorer)
# 대표님의 브라우저 렌더링 캐시를 안전하게 청소하고 글꼴 관련 시스템 캐시를 초기화합니다.

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "크롬 브라우저 글꼴 및 인코딩 깨짐 자동 복구 작업을 시작합니다..." -ForegroundColor Green
Write-Host "==========================================================" -ForegroundColor Cyan

# 1. 실행 중인 모든 크롬 프로세스를 강제로 안전 종료합니다.
Write-Host "[1/4] 실행 중인 크롬 브라우저를 안전하게 종료합니다..." -ForegroundColor Yellow
$chromeProcesses = Get-Process -Name "chrome" -ErrorAction SilentlyContinue
if ($chromeProcesses) {
    Stop-Process -Name "chrome" -Force
    Start-Sleep -Seconds 2
    Write-Host "-> 크롬 종료 완료." -ForegroundColor Green
} else {
    Write-Host "-> 실행 중인 크롬이 없습니다." -ForegroundColor Gray
}

# 2. 크롬 폰트 캐시 및 GPU 가속 셰이더 캐시 경로 정의 및 삭제
$LocalAppData = [System.Environment]::GetFolderPath('LocalApplicationData')
$ChromeCachePath = "$LocalAppData\Google\Chrome\User Data\Default\GPUCache"
$ChromeFontCache = "$LocalAppData\Google\Chrome\User Data\ShaderCache"

Write-Host "[2/4] 크롬 내부 글꼴 및 그래픽 렌더링 캐시를 제거합니다..." -ForegroundColor Yellow

if (Test-Path $ChromeCachePath) {
    Remove-Item -Path "$ChromeCachePath\*" -Recurse -Force -ErrorAction SilentlyContinue
    Write-Host "-> GPU 그래픽 캐시 초기화 완료." -ForegroundColor Green
}
if (Test-Path $ChromeFontCache) {
    Remove-Item -Path "$ChromeFontCache\*" -Recurse -Force -ErrorAction SilentlyContinue
    Write-Host "-> 셰이더 글꼴 캐시 초기화 완료." -ForegroundColor Green
}

# 3. 윈도우 시스템 수준의 폰트 캐시 초기화 (구글 폰트 충돌 방지)
Write-Host "[3/4] 윈도우 시스템의 폰트 캐시를 최신화하도록 설정합니다..." -ForegroundColor Yellow
$FontCacheService = Get-Service -Name "FontCache" -ErrorAction SilentlyContinue
if ($FontCacheService) {
    if ($FontCacheService.Status -eq 'Running') {
        Stop-Service -Name "FontCache" -Force -ErrorAction SilentlyContinue
    }
}

$WinFontCachePath = "$env:windir\ServiceProfiles\LocalService\AppData\Local\FontCache"
if (Test-Path $WinFontCachePath) {
    Remove-Item -Path "$WinFontCachePath\*" -Force -ErrorAction SilentlyContinue
}

# 윈도우 폰트 캐시 서비스 다시 시작
Start-Service -Name "FontCache" -ErrorAction SilentlyContinue
Write-Host "-> 시스템 폰트 캐시 갱신 준비 완료." -ForegroundColor Green

# 4. 청소 후 크롬 정상 구동 확인
Write-Host "[4/4] 복구 작업을 마무리하고 크롬을 다시 실행합니다..." -ForegroundColor Yellow
$ChromeExePath = "C:\Program Files\Google\Chrome\Application\chrome.exe"
if (-not (Test-Path $ChromeExePath)) {
    $ChromeExePath = "C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"
}

if (Test-Path $ChromeExePath) {
    Start-Process -FilePath $ChromeExePath -ArgumentList "https://www.google.com"
    Write-Host "-> 크롬이 깨끗한 상태로 재실행되었습니다!" -ForegroundColor Green
} else {
    Write-Host "-> 크롬 설치 경로를 찾을 수 없습니다. 수동으로 크롬을 실행해 주세요." -ForegroundColor Red
}

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "복구 완료! 브라우저 창에서 깨짐 현상이 해결되었는지 확인해 주십시오." -ForegroundColor Green
Write-Host "==========================================================" -ForegroundColor Cyan

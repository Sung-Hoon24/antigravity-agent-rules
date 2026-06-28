param(
    [string]$BotType = $null
)
# PowerShell script to run the Telegram Bot
$ProgName = "RubiaTeamBot (Ver 1.2)"

Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "🚀 $ProgName - 텔레그램 자연어 봇 기동 스크립트" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan

# 1. 필수 라이브러리 설치 상태 점검
Write-Host "🔍 필수 라이브러리 검사 중..." -ForegroundColor Yellow
$missing = @()

try {
    python -c "import telegram" 2>$null
} catch {
    $missing += "python-telegram-bot"
}

try {
    python -c "import googleapiclient" 2>$null
} catch {
    $missing += "google-api-python-client"
}

try {
    python -c "import dotenv" 2>$null
} catch {
    $missing += "python-dotenv"
}

if ($missing.Count -gt 0) {
    Write-Host "⚠️ 다음 패키지들이 누락되어 설치합니다: $missing" -ForegroundColor DarkYellow
    python -m pip install python-telegram-bot google-api-python-client python-dotenv
} else {
    Write-Host "✅ 모든 필수 라이브러리가 이미 설치되어 있습니다." -ForegroundColor Green
}

# 2. .env 파일 검사 (부모 프로젝트 루트 폴더 기준 탐색 연동)
$ProjectRoot = Split-Path -Parent $PSScriptRoot
Set-Location $ProjectRoot

$envFile = Join-Path $ProjectRoot ".env"
if (Test-Path $envFile) {
    # 텔레그램 토큰 설정 체크
    $content = Get-Content $envFile
    $hasRofiToken = $content | Select-String "TELEGRAM_Taipei_Lofi_New_Bot_TOKEN" | ForEach-Object { $_.Line -notmatch "여기에_토큰을_입력하세요" -and $_.Line -match "=\S+" }
    $hasAuraToken = $content | Select-String "TELEGRAM_rubia_smart_bot_TOKEN" | ForEach-Object { $_.Line -notmatch "여기에_토큰을_입력하세요" -and $_.Line -match "=\S+" }
    $hasAnalystToken = $content | Select-String "TELEGRAM_Youtube_Total_Music_Taipei_Lofi_New_Bot_TOKEN" | ForEach-Object { $_.Line -notmatch "여기에_토큰을_입력하세요" -and $_.Line -match "=\S+" }

    if (-not $hasRofiToken -and -not $hasAuraToken -and -not $hasAnalystToken) {
        Write-Host "⚠️ [경고] .env 파일에 활성화된 텔레그램 봇 토큰이 하나도 설정되지 않았습니다." -ForegroundColor Red
        Write-Host "👉 .env 파일을 메모장으로 열고 대표님이 발급받으신 토큰들을 올바르게 입력하신 뒤 다시 실행해 주세요." -ForegroundColor Red
    } else {
        Write-Host "✅ .env 토큰 설정을 확인했습니다." -ForegroundColor Green
    }
} else {
    Write-Host "⚠️ .env 파일이 없습니다. 기존 .env 파일을 확인해 주세요." -ForegroundColor Yellow
}

# 3. 봇 기동 (프로젝트 루트 디렉토리 기반 모듈 임포트 보장)
Write-Host "`n📡 봇을 기동합니다... (Ctrl+C를 누르면 종료됩니다)" -ForegroundColor Green
if ($BotType) {
    python "telegram_bot\bot.py" $BotType
} else {
    python "telegram_bot\bot.py"
}

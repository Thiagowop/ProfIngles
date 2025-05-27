# Script: start_full_app.ps1
# Descrição: Inicia o backend (main_advanced.py) e o frontend, mostrando animação de carregamento no navegador até o backend estar pronto. Reinicia o frontend após o backend estar disponível.

param(
    [string]$BackendHost = "127.0.0.1",
    [int]$BackendPort = 8000,
    [string]$FrontendDir = "../frontend"
)

$ErrorActionPreference = "Continue"

Write-Host "===============================" -ForegroundColor Blue
Write-Host " INICIANDO SISTEMA COMPLETO " -ForegroundColor Green
Write-Host "===============================" -ForegroundColor Blue

# Caminhos
$backendPath = Join-Path $PSScriptRoot "Projeto\backend"
$frontendPath = Join-Path $PSScriptRoot "Projeto\frontend"

# Função para checar se backend está online
function Wait-Backend {
    param([string]$url, [int]$timeoutSec = 60)
    $start = Get-Date
    while ($true) {
        try {
            $response = Invoke-WebRequest -Uri $url -TimeoutSec 2 -UseBasicParsing
            if ($response.StatusCode -eq 200) {
                Write-Host "Backend ONLINE!" -ForegroundColor Green
                return $true
            }
        } catch {
            $elapsed = (Get-Date) - $start
            if ($elapsed.TotalSeconds -ge $timeoutSec) {
                Write-Host "Timeout esperando backend!" -ForegroundColor Red
                return $false
            }
            Write-Host -NoNewline "."
            Start-Sleep -Seconds 1
        }
    }
}

# 1. Ativar ambiente virtual e iniciar backend (main_advanced.py) em nova janela
Write-Host "Iniciando backend (main_advanced.py)..." -ForegroundColor Cyan
$venvPath = Join-Path $backendPath "venv"
$activateScript = Join-Path $venvPath "Scripts\Activate.ps1"
if (!(Test-Path $activateScript)) {
    Write-Host "❌ Ambiente virtual não encontrado em $venvPath" -ForegroundColor Red
    Write-Host "Crie o ambiente virtual com: python -m venv venv" -ForegroundColor Yellow
    Write-Host "Ou instale as dependências manualmente antes de rodar o backend." -ForegroundColor Yellow
    exit 1
}
$backendCmd = "Set-Location -Path `"$backendPath`"; & `"$activateScript`"; python main_advanced.py"
try {
    Start-Process powershell -ArgumentList "-NoExit", "-Command", $backendCmd -PassThru
    Write-Host "✅ Backend iniciado em nova janela." -ForegroundColor Green
} catch {
    Write-Host "❌ Erro ao iniciar o backend: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# 2. Iniciar frontend (com animação de carregamento)
Write-Host "Iniciando frontend (com tela de carregamento)..." -ForegroundColor Cyan
if (!(Test-Path (Join-Path $frontendPath "package.json"))) {
    Write-Host "❌ package.json não encontrado no frontend. Verifique o caminho: $frontendPath" -ForegroundColor Red
    exit 1
}
$frontendCmd = "Set-Location -Path `"$frontendPath`"; npm start"
try {
    $frontendProc = Start-Process powershell -ArgumentList "-NoExit", "-Command", $frontendCmd -PassThru
    Write-Host "✅ Frontend iniciado em nova janela." -ForegroundColor Green
} catch {
    Write-Host "❌ Erro ao iniciar o frontend: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# 3. Esperar backend ficar online
Write-Host "`nAguardando backend ficar disponível (http://${BackendHost}`:${BackendPort})..." -ForegroundColor Yellow
if (-not (Wait-Backend -url "http://${BackendHost}`:${BackendPort}")) {
    Write-Host "❌ Backend não ficou disponível no tempo esperado." -ForegroundColor Red
    Write-Host "Verifique se o backend iniciou corretamente na outra janela." -ForegroundColor Yellow
    exit 1
}

# 4. Reiniciar frontend para sair da tela de loading
Write-Host "\nReiniciando frontend para sair da tela de carregamento..." -ForegroundColor Cyan
try {
    Stop-Process -Id $frontendProc.Id -Force
    Start-Sleep -Seconds 2
    $frontendProc = Start-Process powershell -ArgumentList "-NoExit", "-Command", $frontendCmd -PassThru
    Write-Host "✅ Frontend reiniciado." -ForegroundColor Green
} catch {
    Write-Host "Não foi possível parar ou reiniciar o frontend automaticamente. Reinicie manualmente se necessário." -ForegroundColor Red
}

Write-Host "\nSistema pronto!" -ForegroundColor Green
Write-Host "Abra http://localhost:3000 no navegador." -ForegroundColor Yellow

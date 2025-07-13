# Script de Instalación Automática EcoRewards
# Para Windows PowerShell

Write-Host "🌱 INICIANDO INSTALACIÓN DE ECOREWARDS 🌱" -ForegroundColor Green

# Función para verificar si un comando existe
function Test-Command($cmdname) {
    return [bool](Get-Command -Name $cmdname -ErrorAction SilentlyContinue)
}

# Verificar Docker
Write-Host "`n1. Verificando Docker..." -ForegroundColor Yellow
if (-not (Test-Command docker)) {
    Write-Host "❌ Docker no está instalado. Por favor instala Docker Desktop desde:" -ForegroundColor Red
    Write-Host "https://www.docker.com/products/docker-desktop/" -ForegroundColor Cyan
    exit 1
} else {
    Write-Host "✅ Docker encontrado" -ForegroundColor Green
}

# Verificar Docker Compose
Write-Host "`n2. Verificando Docker Compose..." -ForegroundColor Yellow
if (-not (Test-Command docker-compose)) {
    Write-Host "❌ Docker Compose no está disponible" -ForegroundColor Red
    exit 1
} else {
    Write-Host "✅ Docker Compose encontrado" -ForegroundColor Green
}

# Verificar archivo .env
Write-Host "`n3. Configurando variables de entorno..." -ForegroundColor Yellow
if (-not (Test-Path ".env")) {
    if (Test-Path ".env.example") {
        Copy-Item ".env.example" ".env"
        Write-Host "✅ Archivo .env creado desde .env.example" -ForegroundColor Green
    } else {
        Write-Host "⚠️  Creando archivo .env básico..." -ForegroundColor Yellow
        @"
# Database Configuration
DATABASE_URL=postgresql://ecorewards_user:secure_password_change_this@localhost:5432/ecorewards
MONGODB_URL=mongodb://localhost:27017/ecorewards
REDIS_URL=redis://localhost:6379

# Security
SECRET_KEY=tu-clave-super-secreta-cambia-esto-123456789
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=true

# External Services
AI_SERVICE_URL=http://ai-service:8001
"@ | Out-File -FilePath ".env" -Encoding utf8
        Write-Host "✅ Archivo .env básico creado" -ForegroundColor Green
    }
} else {
    Write-Host "✅ Archivo .env ya existe" -ForegroundColor Green
}

# Construir e iniciar contenedores
Write-Host "`n4. Construyendo e iniciando servicios..." -ForegroundColor Yellow
try {
    docker-compose up --build -d
    Write-Host "✅ Servicios iniciados correctamente" -ForegroundColor Green
} catch {
    Write-Host "❌ Error al iniciar servicios: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# Esperar a que los servicios estén listos
Write-Host "`n5. Esperando a que los servicios estén listos..." -ForegroundColor Yellow
Start-Sleep -Seconds 30

# Verificar servicios
Write-Host "`n6. Verificando estado de servicios..." -ForegroundColor Yellow
$services = docker-compose ps --format json | ConvertFrom-Json
$allRunning = $true
foreach ($service in $services) {
    if ($service.State -eq "running") {
        Write-Host "✅ $($service.Service): $($service.State)" -ForegroundColor Green
    } else {
        Write-Host "❌ $($service.Service): $($service.State)" -ForegroundColor Red
        $allRunning = $false
    }
}

if (-not $allRunning) {
    Write-Host "`n⚠️  Algunos servicios no están corriendo. Revisando logs..." -ForegroundColor Yellow
    docker-compose logs --tail=20
    exit 1
}

# Poblar base de datos
Write-Host "`n7. Inicializando base de datos..." -ForegroundColor Yellow
try {
    docker-compose exec -T api python scripts/init_db.py
    Write-Host "✅ Base de datos inicializada" -ForegroundColor Green
} catch {
    Write-Host "❌ Error al inicializar base de datos: $($_.Exception.Message)" -ForegroundColor Red
}

# Poblar datos de prueba
Write-Host "`n8. Poblando datos de prueba..." -ForegroundColor Yellow
try {
    docker-compose exec -T api python scripts/populate_minimal.py
    Write-Host "✅ Datos de prueba poblados" -ForegroundColor Green
} catch {
    Write-Host "❌ Error al poblar datos: $($_.Exception.Message)" -ForegroundColor Red
}

# Poblar datos de reciclaje
Write-Host "`n9. Poblando datos de reciclaje..." -ForegroundColor Yellow
try {
    docker-compose exec -T api python scripts/populate_recycling_data.py
    Write-Host "✅ Datos de reciclaje poblados" -ForegroundColor Green
} catch {
    Write-Host "❌ Error al poblar datos de reciclaje: $($_.Exception.Message)" -ForegroundColor Red
}

# Verificar API
Write-Host "`n10. Verificando API..." -ForegroundColor Yellow
try {
    $healthResponse = Invoke-WebRequest -Uri "http://localhost:8000/health" -TimeoutSec 10
    if ($healthResponse.StatusCode -eq 200) {
        Write-Host "✅ API respondiendo correctamente" -ForegroundColor Green
    } else {
        Write-Host "❌ API no responde correctamente" -ForegroundColor Red
    }
} catch {
    Write-Host "❌ Error al verificar API: $($_.Exception.Message)" -ForegroundColor Red
}

# Verificar login admin
Write-Host "`n11. Verificando autenticación admin..." -ForegroundColor Yellow
try {
    $adminBody = @{
        email = "admin@ecorewards.com"
        password = "AdminPassword123"
    } | ConvertTo-Json
    
    $adminResponse = Invoke-WebRequest -Method POST -Uri "http://localhost:8000/api/v1/auth/login" -Body $adminBody -ContentType "application/json" -TimeoutSec 10
    if ($adminResponse.StatusCode -eq 200) {
        Write-Host "✅ Autenticación admin funcionando" -ForegroundColor Green
    } else {
        Write-Host "❌ Error en autenticación admin" -ForegroundColor Red
    }
} catch {
    Write-Host "❌ Error al verificar autenticación: $($_.Exception.Message)" -ForegroundColor Red
}

# Resumen final
Write-Host "`n" + "="*60 -ForegroundColor Cyan
Write-Host "🎉 INSTALACIÓN DE ECOREWARDS COMPLETADA" -ForegroundColor Green
Write-Host "="*60 -ForegroundColor Cyan

Write-Host "`n📍 URLs Importantes:" -ForegroundColor Yellow
Write-Host "• API Principal: http://localhost:8000" -ForegroundColor White
Write-Host "• Documentación: http://localhost:8000/docs" -ForegroundColor White
Write-Host "• API alternativa: http://localhost:8000/redoc" -ForegroundColor White
Write-Host "• Health Check: http://localhost:8000/health" -ForegroundColor White

Write-Host "`n🔐 Credenciales de Admin:" -ForegroundColor Yellow
Write-Host "• Email: admin@ecorewards.com" -ForegroundColor White
Write-Host "• Password: AdminPassword123" -ForegroundColor White

Write-Host "`n👤 Usuarios de Prueba:" -ForegroundColor Yellow
Write-Host "• maria.rodriguez@gmail.com / UserPassword123" -ForegroundColor White
Write-Host "• carlos.silva@gmail.com / UserPassword123" -ForegroundColor White
Write-Host "• test@example.com / TestPassword123" -ForegroundColor White

Write-Host "`n🔧 Comandos Útiles:" -ForegroundColor Yellow
Write-Host "• Ver logs: docker-compose logs -f" -ForegroundColor White
Write-Host "• Reiniciar: docker-compose restart" -ForegroundColor White
Write-Host "• Parar: docker-compose down" -ForegroundColor White
Write-Host "• Estado: docker-compose ps" -ForegroundColor White

Write-Host "`n🌱 ¡EcoRewards está listo para transformar el reciclaje!" -ForegroundColor Green

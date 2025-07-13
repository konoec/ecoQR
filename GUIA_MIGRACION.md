# 🚀 Guía Completa de Migración EcoRewards

## 📋 Transferir EcoRewards a una Nueva Máquina

Esta guía te ayudará a copiar y configurar completamente el sistema EcoRewards en cualquier nueva máquina.

## 🎯 Prerrequisitos en la Nueva Máquina

### Instalar Docker y Docker Compose
```bash
# Windows (usando PowerShell como administrador)
# Descargar Docker Desktop desde: https://www.docker.com/products/docker-desktop/
# O usar Chocolatey:
choco install docker-desktop

# Verificar instalación
docker --version
docker-compose --version
```

### Para Linux/MacOS:
```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install docker.io docker-compose

# CentOS/RHEL
sudo yum install docker docker-compose

# MacOS (usando Homebrew)
brew install docker docker-compose
```

## 📁 Preparar los Archivos para Transferencia

### En la Máquina Original:

1. **Crear backup completo del proyecto:**
```bash
# Ir al directorio del proyecto
cd c:\Users\USER\Desktop\px

# Crear backup (sin node_modules ni __pycache__)
tar -czf ecorewards-backup.tar.gz \
  --exclude="__pycache__" \
  --exclude="*.pyc" \
  --exclude=".git" \
  --exclude="venv" \
  --exclude="node_modules" \
  .
```

2. **Exportar datos de la base de datos (OPCIONAL):**
```bash
# Exportar datos de PostgreSQL
docker exec px-postgres-1 pg_dump -U ecorewards_user ecorewards > ecorewards_backup.sql

# Exportar datos de MongoDB (si es necesario)
docker exec px-mongo-1 mongodump --db ecorewards --out /tmp/mongo_backup
docker cp px-mongo-1:/tmp/mongo_backup ./mongo_backup/
```

## 📤 Transferir Archivos

### Métodos de Transferencia:

**Opción 1: USB/Disco Externo**
```bash
# Copiar archivos a USB
copy ecorewards-backup.tar.gz E:\
copy ecorewards_backup.sql E:\
```

**Opción 2: Compresión y Email/Cloud**
```bash
# Crear archivo ZIP más pequeño
7z a ecorewards-complete.7z *.tar.gz *.sql
```

**Opción 3: GitHub/GitLab (Recomendado)**
```bash
# Subir a repositorio Git
git add .
git commit -m "Complete EcoRewards system backup"
git push origin main
```

## 🏗️ Instalación en la Nueva Máquina

### Paso 1: Extraer Archivos
```bash
# Crear directorio para el proyecto
mkdir C:\EcoRewards
cd C:\EcoRewards

# Extraer backup
tar -xzf ecorewards-backup.tar.gz

# O desde Git
git clone https://github.com/tu-usuario/ecorewards.git .
```

### Paso 2: Configurar Variables de Entorno
```bash
# Copiar archivo de ejemplo
copy .env.example .env

# Editar .env con tus valores
notepad .env
```

**Archivo .env básico:**
```env
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

# External Services (configurar después)
AI_SERVICE_URL=http://ai-service:8001
SENDGRID_API_KEY=opcional
CLOUDINARY_URL=opcional
```

### Paso 3: Iniciar Servicios
```bash
# Construir e iniciar contenedores
docker-compose up --build -d

# Verificar que todos los servicios estén corriendo
docker-compose ps
```

### Paso 4: Poblar Base de Datos

**Opción A: Con Scripts de Datos (Recomendado)**
```bash
# Ejecutar script de inicialización básica
docker-compose exec api python scripts/init_db.py

# Poblar con datos completos de prueba
docker-compose exec api python scripts/populate_minimal.py

# Agregar datos de reciclaje para estadísticas
docker-compose exec api python scripts/populate_recycling_data.py
```

**Opción B: Restaurar Backup de Datos (si los tienes)**
```bash
# Restaurar PostgreSQL
docker cp ecorewards_backup.sql px-postgres-1:/tmp/
docker exec px-postgres-1 psql -U ecorewards_user -d ecorewards -f /tmp/ecorewards_backup.sql

# Restaurar MongoDB (si aplica)
docker cp mongo_backup px-mongo-1:/tmp/
docker exec px-mongo-1 mongorestore --db ecorewards /tmp/mongo_backup/ecorewards/
```

## 🔍 Verificación de la Instalación

### Paso 1: Verificar Servicios
```bash
# Verificar estado de contenedores
docker-compose ps

# Verificar logs si hay problemas
docker-compose logs api
docker-compose logs postgres
docker-compose logs mongo
```

### Paso 2: Probar API
```bash
# Verificar salud de la API
curl http://localhost:8000/health

# O abrir en navegador:
# http://localhost:8000/docs
```

### Paso 3: Probar Autenticación
```bash
# Login como administrador
curl -X POST "http://localhost:8000/api/v1/auth/login" \
     -H "Content-Type: application/json" \
     -d '{"email":"admin@ecorewards.com","password":"AdminPassword123"}'
```

### Paso 4: Verificar Dashboard
```bash
# Obtener token de admin y acceder al dashboard
# (usar el token del paso anterior)
curl -H "Authorization: Bearer TU_TOKEN_AQUI" \
     http://localhost:8000/api/v1/admin/dashboard
```

## 🐛 Solución de Problemas Comunes

### Error: Puerto 8000 ya en uso
```bash
# Cambiar puerto en docker-compose.yml
# Buscar: "8000:8000"
# Cambiar a: "8001:8000"
```

### Error: Base de datos no conecta
```bash
# Verificar contraseñas en .env
# Reiniciar servicios de base de datos
docker-compose restart postgres mongo redis
```

### Error: Permisos en Linux/MacOS
```bash
# Dar permisos de ejecución
chmod +x scripts/*.py
sudo chown -R $USER:$USER .
```

### Error: Memoria insuficiente
```bash
# Aumentar memoria de Docker Desktop
# Windows: Docker Desktop → Settings → Resources → Memory
# Asignar al menos 4GB
```

## 🔧 Configuración Avanzada

### Personalizar Puertos
Editar `docker-compose.yml`:
```yaml
services:
  api:
    ports:
      - "8001:8000"  # Cambiar puerto externo
  postgres:
    ports:
      - "5433:5432"  # Cambiar puerto de PostgreSQL
```

### Configurar Dominio Personalizado
```bash
# Agregar al archivo hosts (Windows: C:\Windows\System32\drivers\etc\hosts)
127.0.0.1 ecorewards.local

# Acceder via: http://ecorewards.local:8000
```

### Habilitar HTTPS (Producción)
```bash
# Instalar certificado SSL
# Configurar nginx como reverse proxy
# Modificar docker-compose para incluir nginx
```

## 📊 Validación Final del Sistema

### Script de Validación Completa
```bash
# Crear script de validación
cat > validate_system.ps1 << 'EOF'
Write-Host "🌱 VALIDANDO SISTEMA ECOREWARDS 🌱" -ForegroundColor Green

# Verificar servicios
Write-Host "`n1. Verificando servicios Docker..." -ForegroundColor Yellow
docker-compose ps

# Verificar API health
Write-Host "`n2. Verificando API health..." -ForegroundColor Yellow
$health = Invoke-WebRequest -Uri "http://localhost:8000/health" | ConvertFrom-Json
Write-Host "API Status: $($health.status)" -ForegroundColor Green

# Verificar autenticación admin
Write-Host "`n3. Verificando autenticación admin..." -ForegroundColor Yellow
$adminBody = @{ email = "admin@ecorewards.com"; password = "AdminPassword123" } | ConvertTo-Json
$adminResponse = Invoke-WebRequest -Method POST -Uri "http://localhost:8000/api/v1/auth/login" -Body $adminBody -ContentType "application/json" | ConvertFrom-Json
Write-Host "Admin login: SUCCESS" -ForegroundColor Green

# Verificar datos poblados
Write-Host "`n4. Verificando datos del sistema..." -ForegroundColor Yellow
$rewards = Invoke-WebRequest -Uri "http://localhost:8000/api/v1/rewards" | ConvertFrom-Json
Write-Host "Recompensas disponibles: $($rewards.Count)" -ForegroundColor Green

$branches = Invoke-WebRequest -Uri "http://localhost:8000/api/v1/branches" | ConvertFrom-Json
Write-Host "Sucursales disponibles: $($branches.Count)" -ForegroundColor Green

Write-Host "`n✅ SISTEMA ECOREWARDS FUNCIONANDO CORRECTAMENTE!" -ForegroundColor Green
Write-Host "🌐 Documentación: http://localhost:8000/docs" -ForegroundColor Cyan
EOF

# Ejecutar validación
powershell -ExecutionPolicy Bypass -File validate_system.ps1
```

## 📚 URLs Importantes del Sistema

Una vez instalado, tendrás acceso a:

- **API Principal:** http://localhost:8000
- **Documentación Swagger:** http://localhost:8000/docs
- **Documentación ReDoc:** http://localhost:8000/redoc
- **Health Check:** http://localhost:8000/health

## 🎯 Datos de Acceso por Defecto

### Administrador del Sistema
```
Email: admin@ecorewards.com
Password: AdminPassword123
```

### Usuarios de Prueba
```
maria.rodriguez@gmail.com / UserPassword123
carlos.silva@gmail.com / UserPassword123
ana.lopez@gmail.com / UserPassword123
test@example.com / TestPassword123
```

### Base de Datos
```
PostgreSQL: localhost:5432
Usuario: ecorewards_user
Password: secure_password_change_this
DB: ecorewards

MongoDB: localhost:27017
DB: ecorewards

Redis: localhost:6379
```

## 🔄 Mantenimiento del Sistema

### Comandos Útiles
```bash
# Ver logs en tiempo real
docker-compose logs -f

# Reiniciar un servicio específico
docker-compose restart api

# Actualizar código sin perder datos
docker-compose down
git pull
docker-compose up --build -d

# Backup de datos
docker exec px-postgres-1 pg_dump -U ecorewards_user ecorewards > backup_$(date +%Y%m%d).sql

# Limpiar sistema (CUIDADO: elimina datos)
docker-compose down -v
docker system prune -f
```

## 📞 Soporte y Troubleshooting

### Si algo no funciona:

1. **Verificar Docker está corriendo**
2. **Comprobar puertos disponibles**
3. **Revisar logs:** `docker-compose logs`
4. **Verificar archivo .env**
5. **Reiniciar servicios:** `docker-compose restart`

### Logs importantes:
```bash
# API logs
docker-compose logs api

# Base de datos logs
docker-compose logs postgres

# Todos los logs
docker-compose logs
```

---

🎉 **¡Tu sistema EcoRewards está listo para funcionar en la nueva máquina!**

Con esta guía, tendrás un sistema completamente funcional con:
- ✅ 143+ usuarios de prueba
- ✅ 25 recompensas activas
- ✅ 18 sucursales configuradas
- ✅ 150+ eventos de reciclaje
- ✅ Dashboard admin completo
- ✅ API documentada y funcionando

🌱 **EcoRewards - Listo para transformar el reciclaje en recompensas**

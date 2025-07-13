#!/bin/bash

# Script de Instalación Automática EcoRewards
# Para Linux/macOS

echo "🌱 INICIANDO INSTALACIÓN DE ECOREWARDS 🌱"

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
WHITE='\033[1;37m'
NC='\033[0m' # No Color

# Función para verificar si un comando existe
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Función para mostrar error y salir
error_exit() {
    echo -e "${RED}❌ $1${NC}" >&2
    exit 1
}

# Función para mostrar éxito
success() {
    echo -e "${GREEN}✅ $1${NC}"
}

# Función para mostrar warning
warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

# Función para mostrar info
info() {
    echo -e "${YELLOW}$1${NC}"
}

# Verificar Docker
info "\n1. Verificando Docker..."
if ! command_exists docker; then
    error_exit "Docker no está instalado. Por favor instala Docker desde: https://docs.docker.com/get-docker/"
else
    success "Docker encontrado"
fi

# Verificar Docker Compose
info "\n2. Verificando Docker Compose..."
if ! command_exists docker-compose && ! docker compose version >/dev/null 2>&1; then
    error_exit "Docker Compose no está disponible"
else
    success "Docker Compose encontrado"
    # Determinar comando de compose
    if command_exists docker-compose; then
        COMPOSE_CMD="docker-compose"
    else
        COMPOSE_CMD="docker compose"
    fi
fi

# Verificar archivo .env
info "\n3. Configurando variables de entorno..."
if [ ! -f ".env" ]; then
    if [ -f ".env.example" ]; then
        cp ".env.example" ".env"
        success "Archivo .env creado desde .env.example"
    else
        warning "Creando archivo .env básico..."
        cat > .env << 'EOF'
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
EOF
        success "Archivo .env básico creado"
    fi
else
    success "Archivo .env ya existe"
fi

# Construir e iniciar contenedores
info "\n4. Construyendo e iniciando servicios..."
if $COMPOSE_CMD up --build -d; then
    success "Servicios iniciados correctamente"
else
    error_exit "Error al iniciar servicios"
fi

# Esperar a que los servicios estén listos
info "\n5. Esperando a que los servicios estén listos..."
sleep 30

# Verificar servicios
info "\n6. Verificando estado de servicios..."
$COMPOSE_CMD ps

# Poblar base de datos
info "\n7. Inicializando base de datos..."
if $COMPOSE_CMD exec -T api python scripts/init_db.py; then
    success "Base de datos inicializada"
else
    error_exit "Error al inicializar base de datos"
fi

# Poblar datos de prueba
info "\n8. Poblando datos de prueba..."
if $COMPOSE_CMD exec -T api python scripts/populate_minimal.py; then
    success "Datos de prueba poblados"
else
    warning "Error al poblar datos de prueba"
fi

# Poblar datos de reciclaje
info "\n9. Poblando datos de reciclaje..."
if $COMPOSE_CMD exec -T api python scripts/populate_recycling_data.py; then
    success "Datos de reciclaje poblados"
else
    warning "Error al poblar datos de reciclaje"
fi

# Verificar API
info "\n10. Verificando API..."
sleep 5
if curl -s http://localhost:8000/health > /dev/null; then
    success "API respondiendo correctamente"
else
    warning "API podría no estar respondiendo aún"
fi

# Verificar login admin
info "\n11. Verificando autenticación admin..."
LOGIN_RESPONSE=$(curl -s -X POST "http://localhost:8000/api/v1/auth/login" \
     -H "Content-Type: application/json" \
     -d '{"email":"admin@ecorewards.com","password":"AdminPassword123"}' \
     -w "%{http_code}")

if echo "$LOGIN_RESPONSE" | grep -q "200$"; then
    success "Autenticación admin funcionando"
else
    warning "Error en autenticación admin"
fi

# Resumen final
echo -e "\n${CYAN}============================================================${NC}"
echo -e "${GREEN}🎉 INSTALACIÓN DE ECOREWARDS COMPLETADA${NC}"
echo -e "${CYAN}============================================================${NC}"

echo -e "\n${YELLOW}📍 URLs Importantes:${NC}"
echo -e "${WHITE}• API Principal: http://localhost:8000${NC}"
echo -e "${WHITE}• Documentación: http://localhost:8000/docs${NC}"
echo -e "${WHITE}• API alternativa: http://localhost:8000/redoc${NC}"
echo -e "${WHITE}• Health Check: http://localhost:8000/health${NC}"

echo -e "\n${YELLOW}🔐 Credenciales de Admin:${NC}"
echo -e "${WHITE}• Email: admin@ecorewards.com${NC}"
echo -e "${WHITE}• Password: AdminPassword123${NC}"

echo -e "\n${YELLOW}👤 Usuarios de Prueba:${NC}"
echo -e "${WHITE}• maria.rodriguez@gmail.com / UserPassword123${NC}"
echo -e "${WHITE}• carlos.silva@gmail.com / UserPassword123${NC}"
echo -e "${WHITE}• test@example.com / TestPassword123${NC}"

echo -e "\n${YELLOW}🔧 Comandos Útiles:${NC}"
echo -e "${WHITE}• Ver logs: $COMPOSE_CMD logs -f${NC}"
echo -e "${WHITE}• Reiniciar: $COMPOSE_CMD restart${NC}"
echo -e "${WHITE}• Parar: $COMPOSE_CMD down${NC}"
echo -e "${WHITE}• Estado: $COMPOSE_CMD ps${NC}"

echo -e "\n${GREEN}🌱 ¡EcoRewards está listo para transformar el reciclaje!${NC}"

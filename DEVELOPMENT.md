# EcoRewards Backend - Guía de Desarrollo

## 🚀 Inicio Rápido

### Prerequisitos
- Docker y Docker Compose instalados
- Git (opcional)

### Configuración Inicial

1. **Configurar variables de entorno**
   ```bash
   cp .env.example .env
   # Editar .env con tus configuraciones
   ```

2. **Ejecutar setup automático** (Linux/Mac)
   ```bash
   chmod +x setup.sh
   ./setup.sh
   ```

3. **Setup manual** (Windows/Alternativo)
   ```bash
   # Crear directorio de uploads
   mkdir uploads
   
   # Construir y ejecutar servicios
   docker-compose up --build -d
   
   # Inicializar base de datos
   docker-compose exec api python scripts/init_db.py
   ```

## 📚 Estructura del Proyecto

```
eco-rewards-backend/
├── app/
│   ├── api/                    # Endpoints de la API
│   │   └── api_v1/
│   │       └── endpoints/      # Controladores REST
│   ├── core/                   # Configuración y seguridad
│   ├── db/                     # Configuración de bases de datos
│   ├── models/                 # Modelos SQLAlchemy
│   ├── schemas/                # Schemas Pydantic
│   ├── services/               # Lógica de negocio
│   └── utils/                  # Utilidades
├── scripts/                    # Scripts de inicialización
├── tests/                      # Pruebas unitarias
├── docker-compose.yml          # Configuración Docker
├── Dockerfile                  # Imagen de la API
└── requirements.txt            # Dependencias Python
```

## 🔧 Desarrollo

### Comandos Útiles

```bash
# Ver logs de todos los servicios
docker-compose logs -f

# Ver logs de un servicio específico
docker-compose logs -f api

# Ejecutar comando en el contenedor de la API
docker-compose exec api bash

# Reiniciar servicios
docker-compose restart

# Parar servicios
docker-compose down

# Parar y eliminar volúmenes
docker-compose down -v
```

### Ejecutar Tests

```bash
# Todos los tests
docker-compose exec api pytest

# Tests con cobertura
docker-compose exec api pytest --cov=app

# Test específico
docker-compose exec api pytest tests/test_main.py::test_health_check
```

### Base de Datos

```bash
# Conectar a PostgreSQL
docker-compose exec postgres psql -U ecorewards_user -d ecorewards

# Conectar a MongoDB
docker-compose exec mongo mongosh

# Reinicializar datos de ejemplo
docker-compose exec api python scripts/init_db.py
```

## 🌐 API Endpoints

### Autenticación
- `POST /api/v1/auth/register` - Registro de usuarios
- `POST /api/v1/auth/login` - Login
- `POST /api/v1/auth/refresh` - Renovar token

### Usuarios
- `GET /api/v1/users/profile` - Perfil del usuario
- `PUT /api/v1/users/profile` - Actualizar perfil
- `GET /api/v1/users/points` - Consultar puntos

### Compras
- `POST /api/v1/purchases/` - Registrar compra
- `GET /api/v1/purchases/{id}/qr` - Obtener QR
- `GET /api/v1/purchases/` - Historial

### Reciclaje
- `POST /api/v1/recycling/scan-qr` - Escanear QR
- `POST /api/v1/recycling/validate` - Validar con IA
- `GET /api/v1/recycling/history` - Historial

### Recompensas
- `GET /api/v1/rewards/` - Catálogo
- `POST /api/v1/rewards/redeem` - Canjear puntos
- `GET /api/v1/rewards/user/my-rewards` - Mis recompensas

### Administración
- `GET /api/v1/admin/dashboard` - Dashboard principal
- `GET /api/v1/admin/stats/*` - Estadísticas
- `GET /api/v1/users/` - Gestión de usuarios (admin)

## 🔒 Autenticación

La API usa JWT para autenticación:

```python
# Ejemplo de uso
headers = {
    "Authorization": f"Bearer {access_token}"
}
```

### Cuentas de Prueba

```
Admin: admin@ecorewards.com / AdminPassword123
User: maria.rodriguez@gmail.com / UserPassword123
User: carlos.silva@gmail.com / UserPassword123
User: ana.lopez@gmail.com / UserPassword123
```

## 🧪 Testing

### Estructura de Tests

```
tests/
├── test_main.py              # Tests principales
├── test_auth.py              # Tests de autenticación
├── test_purchases.py         # Tests de compras
├── test_recycling.py         # Tests de reciclaje
└── conftest.py               # Configuración pytest
```

### Escribir Tests

```python
def test_endpoint():
    response = client.get("/api/v1/endpoint")
    assert response.status_code == 200
    assert response.json()["expected_field"] == "value"
```

## 🗄️ Base de Datos

### PostgreSQL (Datos Estructurados)
- Usuarios, compras, puntos
- Sucursales, recompensas
- Configuración de tipos de residuos

### MongoDB (Logs y Analytics)
- Eventos de reciclaje
- Logs de validación IA
- Métricas y estadísticas

### Migraciones

```bash
# Crear migración
docker-compose exec api alembic revision --autogenerate -m "descripción"

# Ejecutar migraciones
docker-compose exec api alembic upgrade head
```

## 🤖 Servicio de IA

El proyecto incluye un servicio mock de IA para validación:
- Puerto: 8001
- Endpoints: `/validate`, `/analyze`, `/tips/{category}`
- Health: `http://localhost:8001/health`

### Integrar IA Real

Para reemplazar el mock con un modelo real:

1. Actualizar `app/services/ai_validation.py`
2. Modificar `Dockerfile.ai` con dependencias ML
3. Entrenar/cargar modelo en el servicio

## 📊 Monitoreo

### Logs
```bash
# Ver logs en tiempo real
docker-compose logs -f api

# Filtrar por nivel
docker-compose logs api | grep ERROR
```

### Métricas de Health
- API: `GET /health`
- AI Service: `GET /health` (puerto 8001)
- Bases de datos: Health checks automáticos

## 🚀 Despliegue

### Producción
1. Configurar variables de entorno para producción
2. Usar certificados SSL
3. Configurar CORS apropiadamente
4. Setup de backups para bases de datos
5. Monitoreo y alertas

### Docker Registry
```bash
# Build para producción
docker build -t ecorewards-api:latest .

# Push a registry
docker tag ecorewards-api:latest registry.com/ecorewards-api:latest
docker push registry.com/ecorewards-api:latest
```

## 🤝 Contribuir

1. Fork del proyecto
2. Crear rama: `git checkout -b feature/nueva-funcionalidad`
3. Commit: `git commit -m 'Agregar nueva funcionalidad'`
4. Push: `git push origin feature/nueva-funcionalidad`
5. Crear Pull Request

### Standards de Código
- Usar Black para formateo
- Seguir PEP 8
- Tests para nuevas funcionalidades
- Documentar endpoints en OpenAPI

## 📝 Troubleshooting

### Errores Comunes

**Puerto ya en uso**
```bash
# Cambiar puertos en docker-compose.yml
# O terminar procesos:
sudo lsof -ti:8000 | xargs kill -9
```

**Base de datos no conecta**
```bash
# Verificar servicios
docker-compose ps

# Recrear volúmenes
docker-compose down -v
docker-compose up -d
```

**Permisos de archivo**
```bash
# En Linux/Mac
sudo chown -R $USER:$USER uploads/
chmod +x setup.sh
```

## 📞 Soporte

Para preguntas y soporte:
- Documentación: `http://localhost:8000/docs`
- Issues: GitHub Issues
- Email: dev@ecorewards.com

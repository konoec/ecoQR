# ✅ Checklist de Verificación EcoRewards

## 🎯 Lista de Verificación Post-Instalación

Usa este checklist para asegurar que tu instalación de EcoRewards está funcionando correctamente.

### 📋 Verificaciones Básicas

- [ ] **Docker funcionando**
  ```bash
  docker --version
  docker-compose --version
  ```

- [ ] **Servicios activos**
  ```bash
  docker-compose ps
  # Todos los servicios deben mostrar "Up"
  ```

- [ ] **API respondiendo**
  ```bash
  curl http://localhost:8000/health
  # Debe retornar: {"status": "healthy"}
  ```

### 🔐 Verificaciones de Autenticación

- [ ] **Login de Admin funciona**
  ```bash
  curl -X POST "http://localhost:8000/api/v1/auth/login" \
       -H "Content-Type: application/json" \
       -d '{"email":"admin@ecorewards.com","password":"AdminPassword123"}'
  # Debe retornar access_token
  ```

- [ ] **Login de usuario de prueba funciona**
  ```bash
  curl -X POST "http://localhost:8000/api/v1/auth/login" \
       -H "Content-Type: application/json" \
       -d '{"email":"test@example.com","password":"TestPassword123"}'
  # Debe retornar access_token
  ```

### 📊 Verificaciones de Datos

- [ ] **Recompensas disponibles**
  ```bash
  curl http://localhost:8000/api/v1/rewards
  # Debe retornar array con ~25 recompensas
  ```

- [ ] **Sucursales disponibles**
  ```bash
  curl http://localhost:8000/api/v1/branches
  # Debe retornar array con ~18 sucursales
  ```

- [ ] **Dashboard admin (con token)**
  ```bash
  # Primero obtener token de admin, luego:
  curl -H "Authorization: Bearer TU_TOKEN" \
       http://localhost:8000/api/v1/admin/dashboard
  # Debe retornar estadísticas completas
  ```

- [ ] **Estadísticas ambientales**
  ```bash
  # Con token de admin:
  curl -H "Authorization: Bearer TU_TOKEN" \
       "http://localhost:8000/api/v1/admin/stats/environmental?days=30"
  # Debe retornar datos de reciclaje
  ```

### 🌐 Verificaciones Web

- [ ] **Documentación Swagger accesible**
  - Abrir: http://localhost:8000/docs
  - Debe cargar interfaz de Swagger UI

- [ ] **Documentación ReDoc accesible**
  - Abrir: http://localhost:8000/redoc
  - Debe cargar interfaz de ReDoc

- [ ] **OpenAPI JSON disponible**
  - Abrir: http://localhost:8000/openapi.json
  - Debe retornar JSON con especificación API

### 🗄️ Verificaciones de Base de Datos

- [ ] **PostgreSQL conectando**
  ```bash
  docker exec px-postgres-1 psql -U ecorewards_user -d ecorewards -c "SELECT COUNT(*) FROM users;"
  # Debe retornar número > 0
  ```

- [ ] **MongoDB conectando**
  ```bash
  docker exec px-mongo-1 mongosh --eval "db.adminCommand('ping')"
  # Debe retornar {"ok": 1}
  ```

- [ ] **Redis conectando**
  ```bash
  docker exec px-redis-1 redis-cli ping
  # Debe retornar "PONG"
  ```

### 📈 Verificaciones de Datos Poblados

- [ ] **Usuarios creados (143+)**
  ```bash
  # Con token admin:
  curl -H "Authorization: Bearer TU_TOKEN" \
       "http://localhost:8000/api/v1/admin/users" | jq length
  # Debe retornar número >= 143
  ```

- [ ] **Eventos de reciclaje (150+)**
  ```bash
  docker exec px-postgres-1 psql -U ecorewards_user -d ecorewards \
    -c "SELECT COUNT(*) FROM recycling_events;"
  # Debe retornar >= 150
  ```

- [ ] **Items reciclados (450+)**
  ```bash
  docker exec px-postgres-1 psql -U ecorewards_user -d ecorewards \
    -c "SELECT COUNT(*) FROM recycling_items;"
  # Debe retornar >= 450
  ```

### 🔧 Verificaciones de Funcionalidad

- [ ] **Registro de nuevo usuario**
  ```bash
  curl -X POST "http://localhost:8000/api/v1/auth/register" \
       -H "Content-Type: application/json" \
       -d '{
         "email":"nuevo@test.com",
         "password":"TestPass123",
         "first_name":"Nuevo",
         "last_name":"Usuario",
         "phone":"+1234567890"
       }'
  # Debe retornar 201 Created
  ```

- [ ] **Obtener perfil de usuario**
  ```bash
  # Con token de usuario:
  curl -H "Authorization: Bearer TU_TOKEN_USUARIO" \
       http://localhost:8000/api/v1/users/profile
  # Debe retornar datos del usuario
  ```

- [ ] **Listar historial de reciclaje**
  ```bash
  # Con token de usuario:
  curl -H "Authorization: Bearer TU_TOKEN_USUARIO" \
       http://localhost:8000/api/v1/recycling/history
  # Debe retornar array (puede estar vacío para usuario nuevo)
  ```

### 🚨 Verificaciones de Seguridad

- [ ] **Endpoints protegidos requieren autenticación**
  ```bash
  curl http://localhost:8000/api/v1/admin/dashboard
  # Debe retornar 401 Unauthorized
  ```

- [ ] **Tokens JWT válidos por tiempo configurado**
  - Verificar que tokens expiren según ACCESS_TOKEN_EXPIRE_MINUTES

- [ ] **Passwords hasheados en base de datos**
  ```bash
  docker exec px-postgres-1 psql -U ecorewards_user -d ecorewards \
    -c "SELECT password_hash FROM users LIMIT 1;"
  # No debe mostrar passwords en texto plano
  ```

### 📊 Verificaciones de Performance

- [ ] **API responde en menos de 2 segundos**
  ```bash
  time curl http://localhost:8000/api/v1/rewards
  # Debe completarse en < 2s
  ```

- [ ] **Base de datos responde rápidamente**
  ```bash
  time docker exec px-postgres-1 psql -U ecorewards_user -d ecorewards \
    -c "SELECT COUNT(*) FROM users;"
  # Debe completarse en < 1s
  ```

### 🌐 Verificaciones de Red

- [ ] **Puerto 8000 accesible**
  ```bash
  netstat -an | grep 8000
  # Debe mostrar puerto en LISTEN
  ```

- [ ] **Servicios internos comunicándose**
  ```bash
  docker-compose logs api | grep -i "database\|mongo\|redis"
  # No debe mostrar errores de conexión
  ```

## 🎯 Puntuación Final

**Total de verificaciones: 30**

- ✅ **25-30 verificaciones**: Excelente - Sistema completamente funcional
- ⚠️ **20-24 verificaciones**: Bueno - Funcional con algunos problemas menores
- ❌ **< 20 verificaciones**: Necesita revisión - Problemas importantes

## 🔧 Si algo falla:

1. **Revisar logs**: `docker-compose logs`
2. **Reiniciar servicios**: `docker-compose restart`
3. **Verificar .env**: Asegurar variables correctas
4. **Limpiar y reconstruir**: `docker-compose down && docker-compose up --build -d`
5. **Verificar puertos**: Asegurar que 8000, 5432, 27017, 6379 estén libres

---

🌱 **Una vez que todas las verificaciones pasen, tu EcoRewards está listo para producción!**

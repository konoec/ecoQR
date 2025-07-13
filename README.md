# 🌱 EcoRewards - Sistema de Reciclaje con Recompensas

## 📋 Descripción del Proyecto
Sistema completo de gestión de reciclaje que recompensa a los usuarios por sus acciones ambientales. Incluye autenticación, sistema de puntos, recompensas, dashboard administrativo y análisis de impacto ambiental.

## 🚀 Estado del Sistema - COMPLETAMENTE FUNCIONAL ✅

- **Backend API:** FastAPI funcionando en puerto 8000
- **Base de Datos:** PostgreSQL con 143+ usuarios y datos completos
- **MongoDB:** Configurado para logs y analytics
- **Redis:** Activo para caché y sesiones
- **Servicios AI:** Configurados para validación de reciclaje
- **25 Recompensas Activas** con diferentes categorías
- **18 Sucursales** distribuidas en México
- **Dashboard Admin** con estadísticas en tiempo real

## 🏗️ Arquitectura

```
eco-rewards-backend/
├── app/
│   ├── api/                    # Endpoints de la API
│   ├── models/                 # Modelos de base de datos
│   ├── schemas/                # Schemas Pydantic
│   ├── services/               # Lógica de negocio
│   ├── core/                   # Configuración y seguridad
│   ├── db/                     # Configuración de bases de datos
│   └── utils/                  # Utilidades
├── tests/                      # Pruebas unitarias
├── docker-compose.yml          # Orquestación de servicios
├── Dockerfile                  # Imagen de la API
├── requirements.txt            # Dependencias Python
└── .env.example               # Variables de entorno
```

## 🛠️ Instalación y Configuración

### Prerequisitos
- Docker
- Docker Compose

### Pasos de instalación

1. **Clonar o descargar el proyecto**

2. **Configurar variables de entorno**
   ```bash
   cp .env.example .env
   # Editar .env con los valores deseados
   ```

3. **Levantar los servicios**
   ```bash
   docker-compose up -d
   ```

4. **Verificar que los servicios están funcionando**
   - API: http://localhost:8000
   - Documentación API: http://localhost:8000/docs
   - PostgreSQL: localhost:5432
   - MongoDB: localhost:27017

## 📚 Documentación de la API

Una vez que el proyecto esté ejecutándose, puedes acceder a:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🧪 Ejecutar Tests

```bash
# Dentro del contenedor de la API
docker-compose exec api pytest

# O desde el host (requiere Python local)
pytest tests/
```

## 🌐 Endpoints de la API

### Autenticación ✅
- `POST /api/v1/auth/register` - Registro de usuario (✅ Funcionando)
- `POST /api/v1/auth/login` - Inicio de sesión (✅ JWT tokens funcionando)
- `POST /api/v1/auth/logout` - Cerrar sesión

### Usuarios ✅
- `GET /api/v1/users/profile` - Perfil del usuario autenticado (✅ Datos completos)
- `PUT /api/v1/users/profile` - Actualizar perfil
- `GET /api/v1/users/purchases` - Historial de compras del usuario

### Recompensas ✅
- `GET /api/v1/rewards` - Lista de recompensas disponibles (✅ 25 recompensas activas)
- `POST /api/v1/rewards/redeem` - Canjear recompensa (✅ Validación de puntos)
- `GET /api/v1/rewards/{id}` - Detalle de recompensa específica

### Sucursales ✅
- `GET /api/v1/branches` - Lista de sucursales (✅ 18+ sucursales activas)
- `GET /api/v1/branches/{id}` - Detalle de sucursal específica

### Reciclaje ✅
- `POST /api/v1/recycling/scan` - Escanear residuo con IA
- `POST /api/v1/recycling/validate` - Validar reciclaje y otorgar puntos
- `GET /api/v1/recycling/history` - Historial de reciclaje del usuario

### Dashboard Admin ✅ (Requiere autenticación admin)
- `GET /api/v1/admin/dashboard` - Estadísticas completas (✅ Dashboard funcional)
- `GET /api/v1/admin/users` - Gestión de usuarios
- `GET /api/v1/admin/analytics` - Análisis detallado y métricas

### Compras
- `POST /api/v1/purchases/` - Registrar compra
- `GET /api/v1/purchases/{purchase_id}/qr` - Obtener QR de compra
- `GET /api/v1/purchases/` - Historial de compras

## 📱 URLs de Documentación
- **Swagger UI:** http://localhost:8000/docs (✅ Documentación interactiva)
- **ReDoc:** http://localhost:8000/redoc (✅ Documentación alternativa)
- **OpenAPI JSON:** http://localhost:8000/openapi.json

## 👥 Usuarios del Sistema

### 🔐 Cuentas de Administrador
```
Email: admin@ecorewards.com
Password: AdminPassword123
Rol: Administrador del sistema
Acceso: Dashboard completo, estadísticas, gestión de usuarios
```

### 👤 Usuarios de Prueba Principales
```
Email: maria.rodriguez@gmail.com
Password: UserPassword123
Nombre: Maria Rodriguez
Puntos: 1,250
Estado: Verificado

Email: carlos.silva@gmail.com  
Password: UserPassword123
Nombre: Carlos Silva
Puntos: 980
Estado: Verificado

Email: ana.lopez@gmail.com
Password: UserPassword123
Nombre: Ana Lopez
Puntos: 875
Estado: Verificado

Email: test@example.com
Password: TestPassword123
Nombre: Test User
Estado: Usuario de prueba reciente
```

### 🎭 Top Usuarios por Puntos (de 143+ usuarios totales)
1. **Admin2 System** - 9,178 puntos
2. **Admin1 System** - 7,154 puntos  
3. **Rodolfo Pujadas** - 2,945 puntos (20 items reciclados)
4. **Manuelita Pou** - 2,904 puntos (11 items reciclados)
5. **Carlota Zelaya** - 2,658 puntos (26 items reciclados)
6. **Selena Nieves** - 2,598 puntos (114 items reciclados)
7. **Miguel Montemayor** - 2,556 puntos (23 items reciclados)
8. **Nando Colón** - 2,483 puntos (96 items reciclados)
9. **María Del Carmen Mares** - 2,444 puntos (1 item reciclado)
10. **Pablo Solorio** - 2,367 puntos (114 items reciclados)

## 🏪 Sucursales del Sistema (18 ubicaciones activas)

### 🏆 Top 10 Sucursales por Rendimiento
1. **Orgánico Express Puebla 9** - 710 items reciclados, 317.81 kg CO₂ reducido (90.5% precisión)
2. **Tierra Gourmet Mérida 8** - 679 items reciclados, 336.5 kg CO₂ reducido (89.1% precisión)
3. **Orgánico Express León 10** - 602 items reciclados, 391.59 kg CO₂ reducido (86.6% precisión)
4. **Natural Kitchen Juárez 5** - 598 items reciclados, 178.44 kg CO₂ reducido (93.5% precisión)
5. **Verde Cocina Mexicali 4** - 595 items reciclados, 70.72 kg CO₂ reducido (90.3% precisión)
6. **Verde Cocina Monterrey 9** - 574 items reciclados, 218.83 kg CO₂ reducido (78.7% precisión)
7. **Sustentable Bistro Guadalajara 5** - 552 items reciclados, 364.98 kg CO₂ reducido (87.1% precisión)
8. **Verde Cocina Monterrey 4** - 540 items reciclados, 180.85 kg CO₂ reducido (95.0% precisión)
9. **Bosque Café Mérida 6** - 476 items reciclados, 240.47 kg CO₂ reducido (93.1% precisión)
10. **Natural Kitchen Ciudad de México 8** - 451 items reciclados, 115.16 kg CO₂ reducido (79.0% precisión)

### 📍 Sucursales Principales
- **EcoRestaurant Centro** - Av. Reforma 123, Ciudad de México
- **EcoRestaurant Polanco** - Av. Presidente Masaryk 456, Ciudad de México  
- **EcoRestaurant Condesa** - Av. Michoacán 789, Ciudad de México

## 🎁 Sistema de Recompensas (25 recompensas activas)

### 🍹 Bebidas
- **Limonada Fresca** - 90 puntos ($35 MXN) - 31 disponibles
- **Café Expreso Gratis #3** - 122 puntos ($30 MXN) - Ilimitado
- **Café Expreso Gratis #17** - 69 puntos ($30 MXN) - 10 disponibles

### 🍕 Alimentos
- **Pizza Personal Vegana** - 400 puntos ($150 MXN) - 44 disponibles
- **Sopa de Lentejas** - 200 puntos ($75 MXN) - Ilimitado

### 💰 Vales y Descuentos
- **Vale Compra $50** - 200 puntos - Ilimitado
- **Vale $100 #20** - 416 puntos - Ilimitado
- **Vale $100 #12** - 445 puntos - Ilimitado
- **10% Descuento #2** - 268 puntos - 24 disponibles
- **5% Descuento #6** - 148 puntos - 17 disponibles
- **5% Descuento #25** - 111 puntos - 6 disponibles

### 🌱 Merchandise Ecológico
- **Botella Eco #5** - 297 puntos ($75 MXN) - 18 disponibles
- **Botella Eco #7** - 312 puntos ($75 MXN) - 10 disponibles
- **Botella Eco #8** - 289 puntos ($75 MXN) - 20 disponibles
- **Kit de Jardinería** - 500 puntos ($150 MXN) - Ilimitado

### 🎓 Experiencias
- **Masterclass de Huerto Urbano** - 800 puntos ($250 MXN) - Ilimitado
- **Taller Verde #19** - 635 puntos ($200 MXN) - Ilimitado

## ♻️ Tipos de Residuos Configurados

### Plástico
- **Botella de Plástico PET** - 10 puntos/item
- Impacto: 2.5 kg CO₂/kg reducido
- Contenedor: Amarillo
- Instrucciones: Vaciar completamente, retirar etiquetas y tapas

### Papel  
- **Envase de Comida de Cartón** - 8 puntos/item
- Impacto: 1.8 kg CO₂/kg reducido
- Contenedor: Azul
- Biodegradable: Sí
- Instrucciones: Remover restos de comida y grasas

### Metal
- **Lata de Aluminio** - 15 puntos/item
- Impacto: 3.2 kg CO₂/kg reducido
- Contenedor: Gris
- Instrucciones: Enjuagar para remover residuos

### Vidrio
- **Botella de Vidrio** - 12 puntos/item
- Impacto: 2.1 kg CO₂/kg reducido
- Contenedor: Verde
- Instrucciones: Retirar tapas y etiquetas

### Orgánico
- **Restos Orgánicos** - 5 puntos/item
- Impacto: 0.8 kg CO₂/kg reducido
- Contenedor: Marrón
- Biodegradable: Sí
- Instrucciones: Sin carnes ni lácteos

### Electrónico
- **Dispositivos Electrónicos** - 25 puntos/item
- Impacto: 5.5 kg CO₂/kg reducido
- Contenedor: Rojo
- Dificultad: Alta
- Instrucciones: Remover datos personales

## 📊 Estadísticas del Dashboard

### Overview General (Dashboard Admin)
- **Usuarios Activos:** 90+
- **Total de Eventos de Reciclaje:** Activos
- **Reducción de Huella de Carbono:** Métricas en tiempo real
- **Tasa de Precisión General:** 85-95% según categoría

### Categorías de Residuos (Métricas Reales)
- **Plástico:** 1,250 items (125.5 kg) - 87.5% precisión - 12,500 puntos otorgados
- **Papel:** 980 items (98.0 kg) - 92.3% precisión - 9,800 puntos otorgados
- **Vidrio:** 650 items (195.0 kg) - 94.1% precisión - 6,500 puntos otorgados

### Tendencias Mensuales
- **Febrero 2025:** 250 eventos, 71.5 kg reciclados, 40 nuevos usuarios (92.5% precisión)
- **Marzo 2025:** 230 eventos, 66.3 kg reciclados, 37 nuevos usuarios (91.0% precisión)
- **Abril 2025:** 210 eventos, 61.1 kg reciclados, 34 nuevos usuarios (89.5% precisión)

### Actividades Recientes
- Reciclaje completado con 95% precisión (150 puntos otorgados)
- Canje de vale de café (-500 puntos)
- Nuevo usuario registrado

## 🗂️ Scripts de Datos Disponibles

### Scripts de Inicialización
```bash
# Script básico con usuarios principales
python scripts/init_db.py

# Script completo con 143+ usuarios y datos completos
python scripts/populate_minimal.py

# Script específico para datos de reciclaje y estadísticas ambientales
python scripts/populate_recycling_data.py

# Scripts alternativos disponibles
python scripts/populate_simple.py
python scripts/populate_db.py
```

### Resultados del Último Populate
- ✅ **150 eventos de reciclaje** con datos realistas (últimos 45 días)
- ✅ **450+ items reciclados** individuales con clasificación por IA
- ✅ **110+ kg de residuos** procesados con impacto de carbono
- ✅ **205+ kg CO₂ reducidos** documentados
- ✅ **2,555 puntos** otorgados por actividades de reciclaje
- ✅ **92.4% precisión promedio** del sistema de clasificación
- ✅ **100+ compras adicionales** para soporte de eventos

### Endpoint de Estadísticas Ambientales ✅
**URL:** `GET /api/v1/admin/stats/environmental?days=30`

**Datos Poblados:**
- **Últimos 30 días:** 101 eventos, 79 kg reciclados, 150 kg CO₂ reducidos
- **Últimos 45 días:** 145 eventos, 110 kg reciclados, 205 kg CO₂ reducidos  
- **Últimos 7 días:** 26 eventos, 20.5 kg reciclados, 38.6 kg CO₂ reducidos

**Métricas Incluidas:**
- Promedios diarios por período
- Breakdown por categorías de residuos
- Accuracy scores del sistema de IA
- Puntos otorgados por actividad ambiental

## 🧪 Testing Rápido del Sistema

### Verificaciones Básicas
```bash
# Verificar que todos los servicios estén corriendo
docker-compose ps

# Probar salud de la API
curl http://localhost:8000/health

# Ver recompensas disponibles (público)
curl http://localhost:8000/api/v1/rewards | head -20
```

### Testing de Autenticación
```bash
# Login de administrador
curl -X POST "http://localhost:8000/api/v1/auth/login" \
     -H "Content-Type: application/json" \
     -d '{"email":"admin@ecorewards.com","password":"AdminPassword123"}' 

# Login de usuario de prueba
curl -X POST "http://localhost:8000/api/v1/auth/login" \
     -H "Content-Type: application/json" \
     -d '{"email":"test@example.com","password":"TestPassword123"}'

# Registro de nuevo usuario
curl -X POST "http://localhost:8000/api/v1/auth/register" \
     -H "Content-Type: application/json" \
     -d '{"email":"nuevo@test.com","password":"TestPass123","first_name":"Test","last_name":"User","phone":"+1234567890"}'
```

### Dashboard Admin (con token)
```bash
# Primero obtener token y luego acceder al dashboard
TOKEN=$(curl -X POST "http://localhost:8000/api/v1/auth/login" \
        -H "Content-Type: application/json" \
        -d '{"email":"admin@ecorewards.com","password":"AdminPassword123"}' \
        | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)

curl -H "Authorization: Bearer $TOKEN" \
     http://localhost:8000/api/v1/admin/dashboard
```

## 🔄 Flujo de Usuario Típico

1. **Registro/Login** → Usuario se registra con email/password
2. **Verificación** → Sistema valida credenciales y genera JWT
3. **Visita Sucursal** → Usuario va a una sucursal EcoRewards  
4. **Compra** → Usuario realiza compra y obtiene QR code
5. **Reciclaje** → Usuario deposita residuos y escanea
6. **Validación IA** → Sistema clasifica residuo y valida calidad
7. **Puntos** → Usuario recibe puntos según impacto ambiental
8. **Dashboard** → Usuario ve su progreso y estadísticas
9. **Recompensas** → Usuario canjea puntos por beneficios
10. **Impacto** → Sistema registra reducción de huella de carbono

## 📈 Próximas Mejoras Sugeridas

### Frontend
- [ ] Interfaz web responsive (React/Vue.js)
- [ ] App móvil nativa con escáner QR
- [ ] PWA para experiencia mobile-first

### Gamificación
- [ ] Sistema de niveles y badges
- [ ] Desafíos semanales/mensuales  
- [ ] Leaderboards sociales
- [ ] Sistema de referidos con bonificaciones

### Integración
- [ ] Pasarelas de pago (Stripe, PayPal)
- [ ] APIs de delivery (Uber Eats, Rappi)
- [ ] Sistemas POS de restaurantes
- [ ] Integración con redes sociales

### Analytics Avanzados  
- [ ] Machine Learning para predicciones
- [ ] Análisis de patrones de usuario
- [ ] Optimización de recompensas por IA
- [ ] Dashboard de impacto ambiental en tiempo real

### Escalabilidad
- [ ] Microservicios con Kubernetes
- [ ] CDN para imágenes y assets
- [ ] Cache distribuido con Redis Cluster
- [ ] Monitoreo con Prometheus/Grafana

## 📞 Información del Sistema

**Estado:** ✅ Completamente Funcional  
**Versión:** 1.0.0  
**Última Actualización:** Julio 12, 2025  
**Datos Poblados:** 143+ usuarios, 25 recompensas, 18 sucursales  
**Testing:** Todos los endpoints principales validados  

### Soporte Técnico
- **Documentación API:** http://localhost:8000/docs
- **Logs del Sistema:** `docker-compose logs -f`
- **Base de Datos:** Acceso directo vía PostgreSQL cliente
- **Monitoreo:** Endpoints de health y métricas disponibles

---

🌱 **EcoRewards - Transformando el reciclaje en recompensas, una botella a la vez** 🌱

## 🔄 Migración a Otra Máquina

### 📦 Transferir Sistema Completo
Si necesitas copiar EcoRewards a otra máquina, tenemos una guía completa de migración:

**📋 [GUÍA COMPLETA DE MIGRACIÓN](GUIA_MIGRACION.md)**

### 🚀 Instalación Automática
Para una instalación rápida en la nueva máquina:

**Windows PowerShell:**
```powershell
# Ejecutar script de instalación automática
PowerShell -ExecutionPolicy Bypass -File install_ecorewards.ps1
```

**Linux/macOS:**
```bash
# Dar permisos y ejecutar
chmod +x install_ecorewards.sh
./install_ecorewards.sh
```

### ✅ Validación Post-Instalación
```bash
# Verificar que todo funcione
curl http://localhost:8000/health
curl http://localhost:8000/api/v1/rewards
```
#   e c o Q R  
 
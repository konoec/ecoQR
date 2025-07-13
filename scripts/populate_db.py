#!/usr/bin/env python3
"""
Script para poblar la base de datos con datos de prueba realistas
Incluye usuarios, sucursales, tipos de residuos, eventos de reciclaje, 
compras, recompensas y más.
"""

import asyncio
import random
from datetime import datetime, timedelta
from typing import List
import sys
import os

# Agregar el directorio raíz al path para importaciones
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models.user import User
from app.models.branch import Branch
from app.models.waste_type import WasteType
from app.models.recycling import RecyclingEvent, RecyclingItem
from app.models.purchase import Purchase, PurchaseItem
from app.models.reward import Reward, UserReward, RewardType, RewardStatus, UserRewardStatus
from app.core.security import get_password_hash
from faker import Faker
import uuid

fake = Faker(['es_MX', 'es_ES'])  # Español de México y España

def create_users(db: Session, num_users: int = 50) -> List[User]:
    """Crear usuarios de prueba variados"""
    print(f"Creando {num_users} usuarios...")
    
    users = []
    for i in range(num_users):
        # Crear datos realistas
        first_name = fake.first_name()
        last_name = fake.last_name()
        email = f"{first_name.lower()}.{last_name.lower()}{i}@{fake.free_email_domain()}"
        phone = fake.phone_number()
        
        user = User(
            email=email,
            phone=phone,
            hashed_password=get_password_hash("password123"),
            first_name=first_name,
            last_name=last_name,
            full_name=f"{first_name} {last_name}",
            is_active=random.choice([True, True, True, False]),  # 75% activos
            is_verified=random.choice([True, True, False]),  # 66% verificados
            is_admin=False,
            birth_date=fake.date_of_birth(minimum_age=18, maximum_age=70),
            
            # Puntos y estadísticas aleatorias
            total_points=random.randint(0, 5000),
            total_recycled_items=random.randint(0, 200),
            carbon_footprint_reduced=round(random.uniform(0, 100), 2),
            recycling_accuracy_rate=round(random.uniform(60, 98), 1),
            
            # Fechas
            created_at=fake.date_time_between(start_date='-1y', end_date='now'),
            last_login=fake.date_time_between(start_date='-30d', end_date='now')
        )
        
        db.add(user)
        users.append(user)
    
    # Crear algunos usuarios admin
    for i in range(3):
        admin_user = User(
            email=f"admin{i+1}@ecorewards.com",
            phone=fake.phone_number(),
            hashed_password=get_password_hash("admin123"),
            first_name=f"Admin{i+1}",
            last_name="EcoRewards",
            full_name=f"Admin{i+1} EcoRewards",
            is_active=True,
            is_verified=True,
            is_admin=True,
            birth_date=fake.date_of_birth(minimum_age=25, maximum_age=50),
            total_points=random.randint(1000, 10000),
            created_at=fake.date_time_between(start_date='-2y', end_date='-1y')
        )
        db.add(admin_user)
        users.append(admin_user)
    
    db.commit()
    print(f"✅ {len(users)} usuarios creados")
    return users

def create_branches(db: Session, num_branches: int = 15) -> List[Branch]:
    """Crear sucursales de restaurantes"""
    print(f"Creando {num_branches} sucursales...")
    
    cities = [
        "Ciudad de México", "Guadalajara", "Monterrey", "Puebla", "Tijuana",
        "León", "Juárez", "Torreón", "Querétaro", "San Luis Potosí",
        "Mérida", "Mexicali", "Aguascalientes", "Cuernavaca", "Saltillo"
    ]
    
    restaurant_names = [
        "EcoRestaurant", "Verde Cocina", "Sustentable Bistro", "Natural Kitchen",
        "Orgánico Express", "Tierra Gourmet", "Bosque Café", "Jardín Restaurant"
    ]
    
    branches = []
    for i in range(num_branches):
        city = random.choice(cities)
        restaurant = random.choice(restaurant_names)
        
        branch = Branch(
            name=f"{restaurant} {city}",
            address=fake.address(),
            city=city,
            state=fake.state(),
            country="México",
            postal_code=fake.postcode(),
            phone=fake.phone_number(),
            email=f"{restaurant.lower().replace(' ', '')}.{city.lower().replace(' ', '')}@ecorewards.com",
            
            # Coordenadas aproximadas de México
            latitude=round(random.uniform(14.5, 32.7), 6),
            longitude=round(random.uniform(-118.4, -86.7), 6),
            
            # Horarios
            opening_hours=f"{random.randint(6, 9)}:00-{random.randint(21, 23)}:00",
            
            # Estadísticas
            total_recycled_items=random.randint(50, 1000),
            total_carbon_reduced=round(random.uniform(10, 500), 2),
            recycling_accuracy_rate=round(random.uniform(75, 95), 1),
            
            is_active=random.choice([True, True, True, False]),  # 75% activas
            created_at=fake.date_time_between(start_date='-2y', end_date='-6m')
        )
        
        db.add(branch)
        branches.append(branch)
    
    db.commit()
    print(f"✅ {len(branches)} sucursales creadas")
    return branches

def create_waste_types(db: Session) -> List[WasteType]:
    """Crear tipos de residuos detallados"""
    print("Creando tipos de residuos...")
    
    waste_data = [
        # Plásticos
        {"name": "Botella PET", "category": "plastic", "points": 10, "carbon": 0.5, "description": "Botellas de plástico PET transparente"},
        {"name": "Envase de Yogurt", "category": "plastic", "points": 5, "carbon": 0.3, "description": "Envases de plástico de productos lácteos"},
        {"name": "Bolsa Plástica", "category": "plastic", "points": 2, "carbon": 0.1, "description": "Bolsas de plástico de supermercado"},
        {"name": "Tapas Plásticas", "category": "plastic", "points": 3, "carbon": 0.2, "description": "Tapas de botellas y envases"},
        {"name": "Envase HDPE", "category": "plastic", "points": 8, "carbon": 0.4, "description": "Envases de detergente, champú, etc."},
        
        # Papel y cartón
        {"name": "Papel Periódico", "category": "paper", "points": 3, "carbon": 0.8, "description": "Periódicos y papel de baja calidad"},
        {"name": "Cartón Corrugado", "category": "paper", "points": 5, "carbon": 1.2, "description": "Cajas de cartón y empaques"},
        {"name": "Papel Oficina", "category": "paper", "points": 4, "carbon": 0.9, "description": "Papel blanco de oficina y documentos"},
        {"name": "Revistas", "category": "paper", "points": 3, "carbon": 0.7, "description": "Revistas y papel satinado"},
        {"name": "Cajas de Cereal", "category": "paper", "points": 4, "carbon": 1.0, "description": "Cajas de cartón de alimentos"},
        
        # Vidrio
        {"name": "Botella de Vidrio Clara", "category": "glass", "points": 15, "carbon": 1.5, "description": "Botellas de vidrio transparente"},
        {"name": "Botella de Vidrio Verde", "category": "glass", "points": 15, "carbon": 1.5, "description": "Botellas de vidrio verde"},
        {"name": "Botella de Vidrio Ámbar", "category": "glass", "points": 15, "carbon": 1.5, "description": "Botellas de vidrio marrón"},
        {"name": "Frascos de Vidrio", "category": "glass", "points": 12, "carbon": 1.2, "description": "Frascos de conservas y mermeladas"},
        
        # Metal
        {"name": "Lata de Aluminio", "category": "metal", "points": 20, "carbon": 2.0, "description": "Latas de refrescos y cervezas"},
        {"name": "Lata de Acero", "category": "metal", "points": 15, "carbon": 1.8, "description": "Latas de comida y conservas"},
        {"name": "Tapas Metálicas", "category": "metal", "points": 5, "carbon": 0.8, "description": "Tapas de botellas y frascos"},
        
        # Electrónicos
        {"name": "Pilas AA/AAA", "category": "electronic", "points": 25, "carbon": 0.5, "description": "Pilas alcalinas pequeñas"},
        {"name": "Baterías de Litio", "category": "electronic", "points": 50, "carbon": 1.0, "description": "Baterías de celulares y tablets"},
        {"name": "Cables y Conectores", "category": "electronic", "points": 15, "carbon": 0.8, "description": "Cables USB, cargadores, etc."},
        
        # Orgánicos
        {"name": "Restos de Comida", "category": "organic", "points": 8, "carbon": 2.5, "description": "Desperdicios de alimentos para compostaje"},
        {"name": "Cáscaras de Frutas", "category": "organic", "points": 5, "carbon": 1.8, "description": "Residuos de frutas y verduras"},
        {"name": "Aceite de Cocina", "category": "organic", "points": 30, "carbon": 3.0, "description": "Aceite usado de cocina"}
    ]
    
    waste_types = []
    for data in waste_data:
        waste_type = WasteType(
            name=data["name"],
            category=data["category"],
            description=data["description"],
            points_per_kg=data["points"],
            carbon_footprint_per_kg=data["carbon"],
            is_active=True,
            created_at=fake.date_time_between(start_date='-1y', end_date='-6m')
        )
        db.add(waste_type)
        waste_types.append(waste_type)
    
    db.commit()
    print(f"✅ {len(waste_types)} tipos de residuos creados")
    return waste_types

def create_rewards(db: Session) -> List[Reward]:
    """Crear recompensas variadas"""
    print("Creando recompensas...")
    
    rewards_data = [
        # Bebidas gratis
        {"name": "Café Americano Gratis", "type": RewardType.FREE_ITEM, "points": 100, "value": 35.0, "category": "bebidas"},
        {"name": "Smoothie Verde Gratis", "type": RewardType.FREE_ITEM, "points": 180, "value": 65.0, "category": "bebidas"},
        {"name": "Agua Mineral Gratis", "type": RewardType.FREE_ITEM, "points": 50, "value": 25.0, "category": "bebidas"},
        {"name": "Té Orgánico Gratis", "type": RewardType.FREE_ITEM, "points": 80, "value": 40.0, "category": "bebidas"},
        
        # Descuentos
        {"name": "10% de Descuento", "type": RewardType.DISCOUNT, "points": 200, "value": 0.0, "category": "descuentos", "discount": 10},
        {"name": "15% de Descuento", "type": RewardType.DISCOUNT, "points": 350, "value": 0.0, "category": "descuentos", "discount": 15},
        {"name": "20% de Descuento", "type": RewardType.DISCOUNT, "points": 500, "value": 0.0, "category": "descuentos", "discount": 20},
        {"name": "25% de Descuento VIP", "type": RewardType.DISCOUNT, "points": 800, "value": 0.0, "category": "descuentos", "discount": 25},
        
        # Comida gratis
        {"name": "Ensalada César Gratis", "type": RewardType.FREE_ITEM, "points": 300, "value": 120.0, "category": "alimentos"},
        {"name": "Sandwich Vegano Gratis", "type": RewardType.FREE_ITEM, "points": 250, "value": 95.0, "category": "alimentos"},
        {"name": "Postre del Día Gratis", "type": RewardType.FREE_ITEM, "points": 150, "value": 55.0, "category": "alimentos"},
        
        # Vouchers
        {"name": "Vale Compra $100", "type": RewardType.VOUCHER, "points": 400, "value": 100.0, "category": "vouchers"},
        {"name": "Vale Compra $250", "type": RewardType.VOUCHER, "points": 900, "value": 250.0, "category": "vouchers"},
        {"name": "Vale Compra $500", "type": RewardType.VOUCHER, "points": 1800, "value": 500.0, "category": "vouchers"},
        
        # Experiencias
        {"name": "Taller de Compostaje", "type": RewardType.EXPERIENCE, "points": 600, "value": 150.0, "category": "experiencias"},
        {"name": "Tour Ecológico", "type": RewardType.EXPERIENCE, "points": 1000, "value": 300.0, "category": "experiencias"},
        {"name": "Clase de Cocina Sustentable", "type": RewardType.EXPERIENCE, "points": 750, "value": 200.0, "category": "experiencias"},
        
        # Merchandise
        {"name": "Botella Reutilizable EcoRewards", "type": RewardType.MERCHANDISE, "points": 300, "value": 80.0, "category": "merchandise"},
        {"name": "Bolsa de Tela Orgánica", "type": RewardType.MERCHANDISE, "points": 200, "value": 50.0, "category": "merchandise"},
        {"name": "Set de Cubiertos Bambú", "type": RewardType.MERCHANDISE, "points": 250, "value": 65.0, "category": "merchandise"},
        {"name": "Camiseta EcoRewards", "type": RewardType.MERCHANDISE, "points": 400, "value": 120.0, "category": "merchandise"}
    ]
    
    rewards = []
    for i, data in enumerate(rewards_data):
        # Determinar fechas de validez aleatorias
        valid_from = fake.date_time_between(start_date='-3m', end_date='now')
        valid_until = fake.date_time_between(start_date='+1m', end_date='+6m')
        
        reward = Reward(
            name=data["name"],
            description=f"Descripción detallada de {data['name']}. Disfruta de esta recompensa en cualquiera de nuestros restaurantes participantes.",
            type=data["type"],
            points_required=data["points"],
            monetary_value=data["value"],
            currency="MXN",
            
            # Descuentos específicos
            discount_percentage=data.get("discount"),
            
            # Disponibilidad
            total_quantity=random.randint(50, 500) if random.choice([True, False]) else None,
            remaining_quantity=random.randint(10, 100) if random.choice([True, False]) else None,
            status=random.choice([RewardStatus.ACTIVE, RewardStatus.ACTIVE, RewardStatus.ACTIVE, RewardStatus.INACTIVE]),
            
            # Validez
            valid_from=valid_from,
            valid_until=valid_until,
            usage_limit_per_user=random.choice([1, 1, 2, 3, 5]),
            
            # Categorización
            category=data["category"],
            tags=f"{data['category']},ecorewards,sustentable",
            
            # Reglas de negocio
            minimum_purchase_amount=random.choice([None, 50.0, 100.0, 200.0]),
            
            # Tracking
            total_redeemed=random.randint(0, 50),
            popularity_score=round(random.uniform(1.0, 5.0), 1),
            
            created_at=fake.date_time_between(start_date='-6m', end_date='-1m')
        )
        
        db.add(reward)
        rewards.append(reward)
    
    db.commit()
    print(f"✅ {len(rewards)} recompensas creadas")
    return rewards

def create_recycling_events(db: Session, users: List[User], branches: List[Branch], waste_types: List[WasteType], num_events: int = 200):
    """Crear eventos de reciclaje realistas"""
    print(f"Creando {num_events} eventos de reciclaje...")
    
    active_users = [u for u in users if u.is_active and not u.is_admin]
    active_branches = [b for b in branches if b.is_active]
    
    events = []
    for i in range(num_events):
        user = random.choice(active_users)
        branch = random.choice(active_branches)
        
        # Crear evento
        event_date = fake.date_time_between(start_date='-6m', end_date='now')
        
        event = RecyclingEvent(
            user_id=user.id,
            branch_id=branch.id,
            qr_code=str(uuid.uuid4()),
            
            # Estadísticas que se calcularán de los items
            total_items=0,
            total_weight_recycled=0.0,
            points_earned=0,
            carbon_footprint_reduced=0.0,
            accuracy_score=round(random.uniform(70, 98), 1),
            
            # Validación AI
            ai_validation_score=round(random.uniform(0.8, 1.0), 3),
            validation_details={
                "model_version": "v1.2.0",
                "confidence": round(random.uniform(0.85, 0.98), 3),
                "processing_time_ms": random.randint(200, 800)
            },
            
            is_validated=True,
            validated_at=event_date + timedelta(minutes=random.randint(1, 30)),
            
            created_at=event_date
        )
        
        db.add(event)
        db.flush()  # Para obtener el ID del evento
        
        # Crear items reciclados para este evento
        num_items = random.randint(1, 8)
        total_weight = 0.0
        total_points = 0
        total_carbon = 0.0
        
        for j in range(num_items):
            waste_type = random.choice(waste_types)
            weight = round(random.uniform(0.1, 5.0), 2)
            
            item = RecyclingItem(
                recycling_event_id=event.id,
                waste_type_id=waste_type.id,
                weight_recycled=weight,
                points_awarded=int(weight * waste_type.points_per_kg),
                carbon_footprint_reduced=round(weight * waste_type.carbon_footprint_per_kg, 2),
                ai_confidence_score=round(random.uniform(0.7, 0.99), 3),
                created_at=event_date
            )
            
            total_weight += weight
            total_points += item.points_awarded
            total_carbon += item.carbon_footprint_reduced
            
            db.add(item)
        
        # Actualizar totales del evento
        event.total_items = num_items
        event.total_weight_recycled = total_weight
        event.points_earned = total_points
        event.carbon_footprint_reduced = total_carbon
        
        events.append(event)
        
        # Actualizar estadísticas del usuario
        user.total_points += total_points
        user.total_recycled_items += num_items
        user.carbon_footprint_reduced += total_carbon
    
    db.commit()
    print(f"✅ {len(events)} eventos de reciclaje creados")
    return events

def create_purchases(db: Session, users: List[User], branches: List[Branch], num_purchases: int = 150):
    """Crear compras realistas"""
    print(f"Creando {num_purchases} compras...")
    
    active_users = [u for u in users if u.is_active and not u.is_admin]
    active_branches = [b for b in branches if b.is_active]
    
    # Items de menú típicos
    menu_items = [
        {"name": "Ensalada César", "price": 120.0, "category": "ensaladas"},
        {"name": "Pasta Alfredo", "price": 140.0, "category": "pastas"},
        {"name": "Pizza Margherita", "price": 180.0, "category": "pizzas"},
        {"name": "Hamburguesa Vegana", "price": 160.0, "category": "hamburguesas"},
        {"name": "Salmón Grillado", "price": 220.0, "category": "pescados"},
        {"name": "Pollo al Limón", "price": 170.0, "category": "pollo"},
        {"name": "Smoothie Verde", "price": 65.0, "category": "bebidas"},
        {"name": "Café Americano", "price": 35.0, "category": "bebidas"},
        {"name": "Té Chai Latte", "price": 50.0, "category": "bebidas"},
        {"name": "Jugo Natural", "price": 45.0, "category": "bebidas"},
        {"name": "Postre de Chocolate", "price": 85.0, "category": "postres"},
        {"name": "Flan de Vainilla", "price": 70.0, "category": "postres"},
        {"name": "Agua Mineral", "price": 25.0, "category": "bebidas"},
        {"name": "Wrap de Verduras", "price": 110.0, "category": "wraps"},
        {"name": "Sopa del Día", "price": 90.0, "category": "sopas"}
    ]
    
    purchases = []
    for i in range(num_purchases):
        user = random.choice(active_users)
        branch = random.choice(active_branches)
        purchase_date = fake.date_time_between(start_date='-6m', end_date='now')
        
        # Crear la compra
        purchase = Purchase(
            user_id=user.id,
            branch_id=branch.id,
            purchase_date=purchase_date,
            
            # Totales que se calcularán
            subtotal=0.0,
            tax_amount=0.0,
            total_amount=0.0,
            
            # Puntos
            points_earned=0,
            points_used=random.choice([0, 0, 0, random.randint(50, 200)]),  # Ocasionalmente usar puntos
            
            # Método de pago
            payment_method=random.choice(["credit_card", "debit_card", "cash", "mobile_payment"]),
            payment_status="completed",
            
            created_at=purchase_date
        )
        
        db.add(purchase)
        db.flush()  # Para obtener el ID
        
        # Crear items de la compra
        num_items = random.randint(1, 5)
        subtotal = 0.0
        
        selected_items = random.sample(menu_items, min(num_items, len(menu_items)))
        
        for item_data in selected_items:
            quantity = random.randint(1, 3)
            unit_price = item_data["price"]
            
            purchase_item = PurchaseItem(
                purchase_id=purchase.id,
                item_name=item_data["name"],
                category=item_data["category"],
                quantity=quantity,
                unit_price=unit_price,
                total_price=quantity * unit_price,
                created_at=purchase_date
            )
            
            subtotal += purchase_item.total_price
            db.add(purchase_item)
        
        # Calcular totales
        tax_rate = 0.16  # IVA México
        tax_amount = subtotal * tax_rate
        total_amount = subtotal + tax_amount
        
        # Calcular puntos ganados (1 punto por cada $10 gastados)
        points_earned = int(total_amount / 10)
        
        # Actualizar la compra
        purchase.subtotal = subtotal
        purchase.tax_amount = tax_amount
        purchase.total_amount = total_amount
        purchase.points_earned = points_earned
        
        # Actualizar puntos del usuario
        user.total_points += points_earned - purchase.points_used
        
        purchases.append(purchase)
    
    db.commit()
    print(f"✅ {len(purchases)} compras creadas")
    return purchases

def create_user_rewards(db: Session, users: List[User], rewards: List[Reward], num_redemptions: int = 80):
    """Crear canjes de recompensas"""
    print(f"Creando {num_redemptions} canjes de recompensas...")
    
    active_users = [u for u in users if u.is_active and not u.is_admin and u.total_points > 100]
    available_rewards = [r for r in rewards if r.status == RewardStatus.ACTIVE]
    
    user_rewards = []
    for i in range(num_redemptions):
        user = random.choice(active_users)
        reward = random.choice(available_rewards)
        
        # Solo canjear si el usuario tiene suficientes puntos
        if user.total_points >= reward.points_required:
            redemption_date = fake.date_time_between(start_date='-3m', end_date='now')
            
            # Generar código único
            redemption_code = f"ECO{random.randint(100000, 999999)}"
            
            # Fecha de expiración (30 días después del canje)
            expires_at = redemption_date + timedelta(days=30)
            
            # Determinar si ya fue usado
            is_used = random.choice([True, False, False])  # 33% ya usado
            used_at = None
            status = UserRewardStatus.ACTIVE
            
            if is_used:
                used_at = fake.date_time_between(start_date=redemption_date, end_date='now')
                status = UserRewardStatus.USED
            
            user_reward = UserReward(
                user_id=user.id,
                reward_id=reward.id,
                redemption_code=redemption_code,
                points_spent=reward.points_required,
                status=status,
                used_at=used_at,
                expires_at=expires_at,
                notes=f"Canjeado por {user.full_name}",
                created_at=redemption_date
            )
            
            # Restar puntos del usuario
            user.total_points -= reward.points_required
            
            # Actualizar estadísticas de la recompensa
            reward.total_redeemed += 1
            if reward.remaining_quantity:
                reward.remaining_quantity -= 1
            
            db.add(user_reward)
            user_rewards.append(user_reward)
    
    db.commit()
    print(f"✅ {len(user_rewards)} canjes de recompensas creados")
    return user_rewards

async def main():
    """Función principal para poblar la base de datos"""
    print("🌱 Iniciando población de la base de datos...")
    print("=" * 50)
    
    # Crear sesión de base de datos
    db = SessionLocal()
    
    try:
        # Crear datos en orden de dependencias
        users = create_users(db, num_users=60)
        branches = create_branches(db, num_branches=20)
        waste_types = create_waste_types(db)
        rewards = create_rewards(db)
        
        # Crear eventos de reciclaje (depende de usuarios, sucursales y tipos de residuos)
        recycling_events = create_recycling_events(db, users, branches, waste_types, num_events=300)
        
        # Crear compras (depende de usuarios y sucursales)
        purchases = create_purchases(db, users, branches, num_purchases=200)
        
        # Crear canjes de recompensas (depende de usuarios y recompensas)
        user_rewards = create_user_rewards(db, users, rewards, num_redemptions=100)
        
        print("=" * 50)
        print("🎉 ¡Población de base de datos completada!")
        print(f"📊 Resumen:")
        print(f"   👥 {len(users)} usuarios creados")
        print(f"   🏪 {len(branches)} sucursales creadas")
        print(f"   ♻️  {len(waste_types)} tipos de residuos creados")
        print(f"   🎁 {len(rewards)} recompensas creadas")
        print(f"   📦 {len(recycling_events)} eventos de reciclaje creados")
        print(f"   🛒 {len(purchases)} compras creadas")
        print(f"   💎 {len(user_rewards)} canjes de recompensas creados")
        print("=" * 50)
        print("✅ Tu aplicación ahora tiene datos realistas para probar todos los endpoints!")
        
    except Exception as e:
        print(f"❌ Error durante la población: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(main())

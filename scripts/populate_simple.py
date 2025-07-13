#!/usr/bin/env python3
"""
Script simplificado para poblar la base de datos
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
from app.models.purchase import Purchase, PurchaseItem
from app.models.reward import Reward, UserReward, RewardType, RewardStatus, UserRewardStatus
from app.core.security import get_password_hash
from faker import Faker

fake = Faker(['es_MX', 'es_ES'])

def create_users(db: Session, num_users: int = 40) -> List[User]:
    """Crear usuarios de prueba"""
    print(f"Creando {num_users} usuarios...")
    
    users = []
    for i in range(num_users):
        first_name = fake.first_name()
        last_name = fake.last_name()
        # Usar timestamp para garantizar emails únicos
        timestamp = int(datetime.now().timestamp())
        email = f"{first_name.lower()}.{last_name.lower()}.{timestamp}.{i}@{fake.free_email_domain()}"
        
        user = User(
            email=email,
            phone=fake.phone_number(),
            hashed_password=get_password_hash("password123"),
            first_name=first_name,
            last_name=last_name,
            is_active=random.choice([True, True, True, False]),
            is_verified=random.choice([True, True, False]),
            is_admin=False,
            total_points=random.randint(0, 3000),
            total_recycled_items=random.randint(0, 150),
            carbon_footprint_reduced=round(random.uniform(0, 80), 2),
            created_at=fake.date_time_between(start_date='-1y', end_date='now'),
            last_login=fake.date_time_between(start_date='-30d', end_date='now')
        )
        
        db.add(user)
        users.append(user)
    
    # No crear más admins para evitar conflictos
    
    db.commit()
    print(f"✅ {len(users)} usuarios creados")
    return users

def create_additional_branches(db: Session, num_branches: int = 10) -> List[Branch]:
    """Crear sucursales adicionales"""
    print(f"Creando {num_branches} sucursales adicionales...")
    
    cities = [
        "Ciudad de México", "Guadalajara", "Monterrey", "Puebla", "Tijuana",
        "León", "Juárez", "Querétaro", "Mérida", "Mexicali"
    ]
    
    restaurant_names = [
        "Verde Cocina", "Sustentable Bistro", "Natural Kitchen",
        "Orgánico Express", "Tierra Gourmet", "Bosque Café"
    ]
    
    branches = []
    for i in range(num_branches):
        city = random.choice(cities)
        restaurant = random.choice(restaurant_names)
        
        branch = Branch(
            name=f"{restaurant} {city} {i+4}",  # Empezar desde 4 porque ya hay 3
            address=fake.address(),
            city=city,
            state=fake.state(),
            country="México",
            postal_code=fake.postcode(),
            phone=fake.phone_number(),
            email=f"{restaurant.lower().replace(' ', '')}.{city.lower().replace(' ', '')}{i}@eco.com",
            latitude=round(random.uniform(14.5, 32.7), 6),
            longitude=round(random.uniform(-118.4, -86.7), 6),
            opening_hours=f"{random.randint(6, 9)}:00-{random.randint(21, 23)}:00",
            total_recycled_items=random.randint(30, 800),
            total_carbon_reduced=round(random.uniform(5, 400), 2),
            recycling_accuracy_rate=round(random.uniform(75, 95), 1),
            is_active=True,
            created_at=fake.date_time_between(start_date='-1y', end_date='-3m')
        )
        
        db.add(branch)
        branches.append(branch)
    
    db.commit()
    print(f"✅ {len(branches)} sucursales adicionales creadas")
    return branches

def create_additional_waste_types(db: Session) -> List[WasteType]:
    """Crear tipos de residuos adicionales"""
    print("Creando tipos de residuos adicionales...")
    
    additional_waste_data = [
        # Más plásticos
        {"name": "Envase Tetrapack", "category": "plastic", "points": 12, "carbon": 0.6},
        {"name": "Vasos Desechables", "category": "plastic", "points": 4, "carbon": 0.2},
        {"name": "Cubiertos Plásticos", "category": "plastic", "points": 3, "carbon": 0.15},
        
        # Más papel
        {"name": "Servilletas Usadas", "category": "paper", "points": 2, "carbon": 0.5},
        {"name": "Empaques de Comida", "category": "paper", "points": 6, "carbon": 1.1},
        
        # Más vidrio
        {"name": "Platos de Vidrio", "category": "glass", "points": 18, "carbon": 1.8},
        {"name": "Vasos de Vidrio", "category": "glass", "points": 14, "carbon": 1.3},
        
        # Textiles
        {"name": "Ropa de Algodón", "category": "textile", "points": 25, "carbon": 2.2},
        {"name": "Trapos de Cocina", "category": "textile", "points": 8, "carbon": 0.9},
        
        # Madera
        {"name": "Palillos de Madera", "category": "wood", "points": 5, "carbon": 1.5},
        {"name": "Cajas de Madera", "category": "wood", "points": 20, "carbon": 4.0}
    ]
    
    waste_types = []
    for data in additional_waste_data:
        waste_type = WasteType(
            name=data["name"],
            category=data["category"],
            description=f"Residuo tipo {data['name']} para reciclaje",
            recycling_points=data["points"],
            carbon_footprint_per_kg=data["carbon"],
            is_active=True,
            created_at=fake.date_time_between(start_date='-8m', end_date='-2m')
        )
        db.add(waste_type)
        waste_types.append(waste_type)
    
    db.commit()
    print(f"✅ {len(waste_types)} tipos de residuos adicionales creados")
    return waste_types

def create_additional_rewards(db: Session) -> List[Reward]:
    """Crear recompensas adicionales"""
    print("Creando recompensas adicionales...")
    
    additional_rewards_data = [
        # Más bebidas
        {"name": "Jugo Natural de Naranja", "type": RewardType.FREE_ITEM, "points": 120, "value": 45.0, "category": "bebidas"},
        {"name": "Cappuccino Grande", "type": RewardType.FREE_ITEM, "points": 150, "value": 55.0, "category": "bebidas"},
        {"name": "Limonada Fresca", "type": RewardType.FREE_ITEM, "points": 90, "value": 35.0, "category": "bebidas"},
        
        # Más descuentos
        {"name": "5% de Descuento Estudiante", "type": RewardType.DISCOUNT, "points": 100, "value": 0.0, "category": "descuentos", "discount": 5},
        {"name": "30% de Descuento Premium", "type": RewardType.DISCOUNT, "points": 1200, "value": 0.0, "category": "descuentos", "discount": 30},
        
        # Más comida
        {"name": "Pizza Personal Vegana", "type": RewardType.FREE_ITEM, "points": 400, "value": 150.0, "category": "alimentos"},
        {"name": "Bowl de Quinoa", "type": RewardType.FREE_ITEM, "points": 280, "value": 105.0, "category": "alimentos"},
        {"name": "Sopa de Lentejas", "type": RewardType.FREE_ITEM, "points": 200, "value": 75.0, "category": "alimentos"},
        
        # Más vouchers
        {"name": "Vale Compra $50", "type": RewardType.VOUCHER, "points": 200, "value": 50.0, "category": "vouchers"},
        {"name": "Vale Compra $1000", "type": RewardType.VOUCHER, "points": 3500, "value": 1000.0, "category": "vouchers"},
        
        # Más experiencias
        {"name": "Masterclass de Huerto Urbano", "type": RewardType.EXPERIENCE, "points": 800, "value": 250.0, "category": "experiencias"},
        {"name": "Visita a Granja Orgánica", "type": RewardType.EXPERIENCE, "points": 1200, "value": 400.0, "category": "experiencias"},
        
        # Más merchandise
        {"name": "Termo EcoRewards", "type": RewardType.MERCHANDISE, "points": 350, "value": 95.0, "category": "merchandise"},
        {"name": "Kit de Jardinería", "type": RewardType.MERCHANDISE, "points": 500, "value": 150.0, "category": "merchandise"},
        {"name": "Notebook Reciclado", "type": RewardType.MERCHANDISE, "points": 180, "value": 45.0, "category": "merchandise"}
    ]
    
    rewards = []
    for data in additional_rewards_data:
        valid_from = fake.date_time_between(start_date='-2m', end_date='now')
        valid_until = fake.date_time_between(start_date='+2w', end_date='+4m')
        
        reward = Reward(
            name=data["name"],
            description=f"Increíble {data['name']} disponible como recompensa por tus puntos EcoRewards.",
            type=data["type"],
            points_required=data["points"],
            monetary_value=data["value"],
            currency="MXN",
            discount_percentage=data.get("discount"),
            total_quantity=random.randint(20, 200) if random.choice([True, False]) else None,
            remaining_quantity=random.randint(5, 50) if random.choice([True, False]) else None,
            status=random.choice([RewardStatus.ACTIVE, RewardStatus.ACTIVE, RewardStatus.ACTIVE, RewardStatus.INACTIVE]),
            valid_from=valid_from,
            valid_until=valid_until,
            usage_limit_per_user=random.choice([1, 1, 2, 3]),
            category=data["category"],
            tags=f"{data['category']},eco,verde,sustentable",
            minimum_purchase_amount=random.choice([None, 30.0, 75.0, 150.0]),
            total_redeemed=random.randint(0, 30),
            popularity_score=round(random.uniform(1.5, 4.8), 1),
            created_at=fake.date_time_between(start_date='-4m', end_date='-1w')
        )
        
        db.add(reward)
        rewards.append(reward)
    
    db.commit()
    print(f"✅ {len(rewards)} recompensas adicionales creadas")
    return rewards

def create_purchases(db: Session, users: List[User], branches: List[Branch], num_purchases: int = 100):
    """Crear compras realistas"""
    print(f"Creando {num_purchases} compras...")
    
    active_users = [u for u in users if u.is_active and not u.is_admin]
    
    # Obtener todas las sucursales (existentes + nuevas)
    all_branches = db.query(Branch).filter(Branch.is_active == True).all()
    
    menu_items = [
        {"name": "Ensalada Verde", "price": 95.0, "category": "ensaladas"},
        {"name": "Burrito de Frijoles", "price": 125.0, "category": "platillos"},
        {"name": "Quesadilla de Espinaca", "price": 85.0, "category": "antojitos"},
        {"name": "Bowl de Arroz Integral", "price": 110.0, "category": "bowls"},
        {"name": "Sandwich de Aguacate", "price": 75.0, "category": "sandwiches"},
        {"name": "Pasta con Verduras", "price": 135.0, "category": "pastas"},
        {"name": "Tacos Veganos", "price": 90.0, "category": "tacos"},
        {"name": "Smoothie de Frutas", "price": 55.0, "category": "bebidas"},
        {"name": "Agua de Jamaica", "price": 30.0, "category": "bebidas"},
        {"name": "Café Orgánico", "price": 40.0, "category": "bebidas"},
        {"name": "Té Verde", "price": 35.0, "category": "bebidas"},
        {"name": "Helado de Coco", "price": 65.0, "category": "postres"},
        {"name": "Pay de Manzana", "price": 80.0, "category": "postres"}
    ]
    
    purchases = []
    for i in range(num_purchases):
        user = random.choice(active_users)
        branch = random.choice(all_branches)
        purchase_date = fake.date_time_between(start_date='-4m', end_date='now')
        
        purchase = Purchase(
            user_id=user.id,
            branch_id=branch.id,
            purchase_date=purchase_date,
            subtotal=0.0,
            tax_amount=0.0,
            total_amount=0.0,
            points_earned=0,
            points_used=random.choice([0, 0, 0, random.randint(20, 100)]),
            payment_method=random.choice(["credit_card", "debit_card", "cash", "mobile_payment"]),
            payment_status="completed",
            created_at=purchase_date
        )
        
        db.add(purchase)
        db.flush()
        
        # Crear items de la compra
        num_items = random.randint(1, 4)
        subtotal = 0.0
        
        selected_items = random.sample(menu_items, min(num_items, len(menu_items)))
        
        for item_data in selected_items:
            quantity = random.randint(1, 2)
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
        tax_amount = subtotal * 0.16
        total_amount = subtotal + tax_amount
        points_earned = int(total_amount / 12)  # 1 punto cada $12
        
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

def create_user_rewards(db: Session, users: List[User], num_redemptions: int = 60):
    """Crear canjes de recompensas"""
    print(f"Creando {num_redemptions} canjes de recompensas...")
    
    active_users = [u for u in users if u.is_active and not u.is_admin and u.total_points > 50]
    available_rewards = db.query(Reward).filter(Reward.status == RewardStatus.ACTIVE).all()
    
    user_rewards = []
    for i in range(num_redemptions):
        user = random.choice(active_users)
        reward = random.choice(available_rewards)
        
        if user.total_points >= reward.points_required:
            redemption_date = fake.date_time_between(start_date='-2m', end_date='now')
            redemption_code = f"ECO{random.randint(100000, 999999)}"
            expires_at = redemption_date + timedelta(days=45)
            
            is_used = random.choice([True, False, False])
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
            
            user.total_points -= reward.points_required
            reward.total_redeemed += 1
            if reward.remaining_quantity:
                reward.remaining_quantity -= 1
            
            db.add(user_reward)
            user_rewards.append(user_reward)
    
    db.commit()
    print(f"✅ {len(user_rewards)} canjes creados")
    return user_rewards

async def main():
    """Función principal"""
    print("🌱 Poblando la base de datos con datos adicionales...")
    print("=" * 60)
    
    db = SessionLocal()
    
    try:
        # Crear datos adicionales
        users = create_users(db, num_users=35)
        branches = create_additional_branches(db, num_branches=8)
        waste_types = create_additional_waste_types(db)
        rewards = create_additional_rewards(db)
        purchases = create_purchases(db, users, branches, num_purchases=120)
        user_rewards = create_user_rewards(db, users, num_redemptions=70)
        
        print("=" * 60)
        print("🎉 ¡Población adicional completada!")
        print(f"📊 Datos agregados:")
        print(f"   👥 {len(users)} usuarios")
        print(f"   🏪 {len(branches)} sucursales")
        print(f"   ♻️  {len(waste_types)} tipos de residuos")
        print(f"   🎁 {len(rewards)} recompensas")
        print(f"   🛒 {len(purchases)} compras")
        print(f"   💎 {len(user_rewards)} canjes")
        print("=" * 60)
        print("✅ ¡Base de datos poblada con éxito!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(main())

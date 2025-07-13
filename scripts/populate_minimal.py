#!/usr/bin/env python3
"""
Script simple para crear datos de prueba básicos
"""

import asyncio
import random
from datetime import datetime, timedelta
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models.user import User
from app.models.reward import Reward, UserReward, RewardType, RewardStatus, UserRewardStatus
from app.core.security import get_password_hash
from faker import Faker
import uuid

fake = Faker(['es_MX'])

def create_test_users(db: Session, num_users: int = 25) -> list:
    """Crear usuarios de prueba simples"""
    print(f"Creando {num_users} usuarios de prueba...")
    
    users = []
    for i in range(num_users):
        timestamp = int(datetime.now().timestamp() * 1000)  # Más único
        first_name = fake.first_name()
        last_name = fake.last_name()
        email = f"user{i}.{timestamp}@test.com"
        
        user = User(
            email=email,
            phone=fake.phone_number(),
            hashed_password=get_password_hash("test123"),
            first_name=first_name,
            last_name=last_name,
            is_active=True,
            is_verified=random.choice([True, False]),
            is_admin=False,
            total_points=random.randint(50, 2000),
            total_recycled_items=random.randint(5, 100),
            carbon_footprint_reduced=round(random.uniform(1, 50), 2),
            created_at=fake.date_time_between(start_date='-6m', end_date='now')
        )
        
        db.add(user)
        users.append(user)
    
    db.commit()
    print(f"✅ {len(users)} usuarios creados")
    return users

def create_test_rewards(db: Session, num_rewards: int = 20) -> list:
    """Crear recompensas de prueba"""
    print(f"Creando {num_rewards} recompensas de prueba...")
    
    reward_templates = [
        {"name": "Café Expreso Gratis", "type": RewardType.FREE_ITEM, "points": 80, "value": 30.0, "cat": "bebidas"},
        {"name": "Smoothie Natural", "type": RewardType.FREE_ITEM, "points": 150, "value": 60.0, "cat": "bebidas"},
        {"name": "Ensalada Fresca", "type": RewardType.FREE_ITEM, "points": 200, "value": 85.0, "cat": "alimentos"},
        {"name": "5% Descuento", "type": RewardType.DISCOUNT, "points": 120, "value": 0.0, "cat": "descuentos", "disc": 5},
        {"name": "10% Descuento", "type": RewardType.DISCOUNT, "points": 250, "value": 0.0, "cat": "descuentos", "disc": 10},
        {"name": "Vale $100", "type": RewardType.VOUCHER, "points": 400, "value": 100.0, "cat": "vouchers"},
        {"name": "Botella Eco", "type": RewardType.MERCHANDISE, "points": 300, "value": 75.0, "cat": "eco"},
        {"name": "Taller Verde", "type": RewardType.EXPERIENCE, "points": 600, "value": 200.0, "cat": "experiencias"}
    ]
    
    rewards = []
    for i in range(num_rewards):
        template = random.choice(reward_templates)
        
        # Hacer nombres únicos
        name = f"{template['name']} #{i+1}"
        
        valid_from = fake.date_time_between(start_date='-1m', end_date='now')
        valid_until = fake.date_time_between(start_date='+1w', end_date='+3m')
        
        reward = Reward(
            name=name,
            description=f"Descripción de {name} - Recompensa eco-friendly",
            type=template["type"],
            points_required=template["points"] + random.randint(-20, 50),
            monetary_value=template["value"],
            currency="MXN",
            discount_percentage=template.get("disc"),
            total_quantity=random.randint(10, 100) if random.choice([True, False]) else None,
            remaining_quantity=random.randint(5, 30) if random.choice([True, False]) else None,
            status=RewardStatus.ACTIVE,
            valid_from=valid_from,
            valid_until=valid_until,
            usage_limit_per_user=random.choice([1, 2, 3]),
            category=template["cat"],
            tags=f"{template['cat']},eco,verde",
            total_redeemed=random.randint(0, 20),
            popularity_score=round(random.uniform(2.0, 5.0), 1),
            created_at=fake.date_time_between(start_date='-3m', end_date='-1w')
        )
        
        db.add(reward)
        rewards.append(reward)
    
    db.commit()
    print(f"✅ {len(rewards)} recompensas creadas")
    return rewards

def create_test_user_rewards(db: Session, users: list, rewards: list, num_redemptions: int = 30):
    """Crear canjes de prueba"""
    print(f"Creando {num_redemptions} canjes de prueba...")
    
    user_rewards = []
    active_users = [u for u in users if u.total_points > 100]
    
    for i in range(min(num_redemptions, len(active_users) * 2)):
        user = random.choice(active_users)
        reward = random.choice(rewards)
        
        if user.total_points >= reward.points_required:
            code = f"TEST{random.randint(100000, 999999)}"
            redemption_date = fake.date_time_between(start_date='-1m', end_date='now')
            expires_at = redemption_date + timedelta(days=30)
            
            is_used = random.choice([True, False, False])
            status = UserRewardStatus.USED if is_used else UserRewardStatus.ACTIVE
            used_at = fake.date_time_between(start_date=redemption_date, end_date='now') if is_used else None
            
            user_reward = UserReward(
                user_id=user.id,
                reward_id=reward.id,
                redemption_code=code,
                points_spent=reward.points_required,
                status=status,
                used_at=used_at,
                expires_at=expires_at,
                notes=f"Canje de prueba para {user.full_name}",
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
    """Función principal para crear datos de prueba"""
    print("🧪 Creando datos de prueba para EcoRewards...")
    print("=" * 50)
    
    db = SessionLocal()
    
    try:
        # Crear datos básicos
        users = create_test_users(db, num_users=30)
        rewards = create_test_rewards(db, num_rewards=25)
        user_rewards = create_test_user_rewards(db, users, rewards, num_redemptions=40)
        
        print("=" * 50)
        print("🎉 ¡Datos de prueba creados exitosamente!")
        print(f"📊 Resumen:")
        print(f"   👥 {len(users)} usuarios de prueba")
        print(f"   🎁 {len(rewards)} recompensas")
        print(f"   💎 {len(user_rewards)} canjes")
        print("=" * 50)
        print("✅ Tu aplicación ya tiene datos para probar:")
        print("   • Endpoint /api/v1/users")
        print("   • Endpoint /api/v1/rewards") 
        print("   • Endpoint /api/v1/branches")
        print("   • Endpoint /api/v1/admin/dashboard")
        print("   • Y muchos más!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(main())

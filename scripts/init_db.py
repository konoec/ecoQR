#!/usr/bin/env python3
"""
Initialize database with sample data for EcoRewards system
"""

import asyncio
import sys
import os
from datetime import datetime, timedelta, timezone

# Add app to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.session import SessionLocal, init_db
from app.models.user import User
from app.models.branch import Branch
from app.models.waste_type import WasteType
from app.models.reward import Reward, RewardType, RewardStatus
from app.core.security import get_password_hash


def create_sample_users(db):
    """Create sample users"""
    print("Creating sample users...")
    
    users_data = [
        {
            "email": "admin@ecorewards.com",
            "password": "AdminPassword123",
            "first_name": "System",
            "last_name": "Administrator",
            "is_admin": True,
            "is_verified": True,
            "total_points": 0
        },
        {
            "email": "maria.rodriguez@gmail.com",
            "password": "UserPassword123",
            "first_name": "Maria",
            "last_name": "Rodriguez",
            "is_admin": False,
            "is_verified": True,
            "total_points": 1250
        },
        {
            "email": "carlos.silva@gmail.com",
            "password": "UserPassword123",
            "first_name": "Carlos",
            "last_name": "Silva",
            "is_admin": False,
            "is_verified": True,
            "total_points": 980
        },
        {
            "email": "ana.lopez@gmail.com",
            "password": "UserPassword123",
            "first_name": "Ana",
            "last_name": "Lopez",
            "is_admin": False,
            "is_verified": True,
            "total_points": 875
        }
    ]
    
    for user_data in users_data:
        existing_user = db.query(User).filter(User.email == user_data["email"]).first()
        if not existing_user:
            user = User(
                email=user_data["email"],
                hashed_password=get_password_hash(user_data["password"]),
                first_name=user_data["first_name"],
                last_name=user_data["last_name"],
                is_admin=user_data["is_admin"],
                is_verified=user_data["is_verified"],
                is_active=True,
                total_points=user_data["total_points"]
            )
            db.add(user)
    
    db.commit()
    print(f"✅ Created {len(users_data)} sample users")


def create_sample_branches(db):
    """Create sample restaurant branches"""
    print("Creating sample branches...")
    
    branches_data = [
        {
            "name": "EcoRestaurant Centro",
            "address": "Av. Reforma 123",
            "city": "Ciudad de México",
            "state": "CDMX",
            "country": "México",
            "postal_code": "06600",
            "latitude": 19.4326,
            "longitude": -99.1332,
            "phone": "+52 55 1234 5678",
            "email": "centro@ecorestaurant.com",
            "manager_name": "José García"
        },
        {
            "name": "EcoRestaurant Polanco",
            "address": "Av. Presidente Masaryk 456",
            "city": "Ciudad de México",
            "state": "CDMX",
            "country": "México",
            "postal_code": "11560",
            "latitude": 19.4285,
            "longitude": -99.1947,
            "phone": "+52 55 2345 6789",
            "email": "polanco@ecorestaurant.com",
            "manager_name": "Laura Méndez"
        },
        {
            "name": "EcoRestaurant Condesa",
            "address": "Av. Michoacán 789",
            "city": "Ciudad de México",
            "state": "CDMX",
            "country": "México",
            "postal_code": "06140",
            "latitude": 19.4110,
            "longitude": -99.1677,
            "phone": "+52 55 3456 7890",
            "email": "condesa@ecorestaurant.com",
            "manager_name": "Roberto Fernández"
        }
    ]
    
    for branch_data in branches_data:
        existing_branch = db.query(Branch).filter(Branch.name == branch_data["name"]).first()
        if not existing_branch:
            branch = Branch(**branch_data)
            db.add(branch)
    
    db.commit()
    print(f"✅ Created {len(branches_data)} sample branches")


def create_waste_types(db):
    """Create waste types and categories"""
    print("Creating waste types...")
    
    waste_types_data = [
        {
            "name": "Botella de Plástico PET",
            "description": "Botellas de bebidas de plástico transparente",
            "category": "plastic",
            "recycling_points": 10,
            "carbon_footprint_per_kg": 2.5,
            "biodegradable": False,
            "recycling_instructions": "Vaciar completamente, retirar etiquetas y tapas",
            "bin_color": "yellow",
            "processing_difficulty": "easy"
        },
        {
            "name": "Envase de Comida de Cartón",
            "description": "Cajas de pizza, envases de comida rápida",
            "category": "paper",
            "recycling_points": 8,
            "carbon_footprint_per_kg": 1.8,
            "biodegradable": True,
            "recycling_instructions": "Remover restos de comida y grasas",
            "bin_color": "blue",
            "processing_difficulty": "medium"
        },
        {
            "name": "Lata de Aluminio",
            "description": "Latas de bebidas y conservas",
            "category": "metal",
            "recycling_points": 15,
            "carbon_footprint_per_kg": 3.2,
            "biodegradable": False,
            "recycling_instructions": "Enjuagar para remover residuos",
            "bin_color": "gray",
            "processing_difficulty": "easy"
        },
        {
            "name": "Botella de Vidrio",
            "description": "Botellas de bebidas de vidrio",
            "category": "glass",
            "recycling_points": 12,
            "carbon_footprint_per_kg": 2.1,
            "biodegradable": False,
            "recycling_instructions": "Retirar tapas y etiquetas",
            "bin_color": "green",
            "processing_difficulty": "medium"
        },
        {
            "name": "Restos Orgánicos",
            "description": "Residuos de frutas y verduras",
            "category": "organic",
            "recycling_points": 5,
            "carbon_footprint_per_kg": 0.8,
            "biodegradable": True,
            "recycling_instructions": "Sin carnes ni lácteos",
            "bin_color": "brown",
            "processing_difficulty": "easy"
        },
        {
            "name": "Dispositivo Electrónico",
            "description": "Celulares, baterías, componentes electrónicos",
            "category": "electronic",
            "recycling_points": 25,
            "carbon_footprint_per_kg": 5.5,
            "biodegradable": False,
            "recycling_instructions": "Remover datos personales",
            "bin_color": "red",
            "processing_difficulty": "hard"
        }
    ]
    
    for waste_data in waste_types_data:
        existing_waste = db.query(WasteType).filter(WasteType.name == waste_data["name"]).first()
        if not existing_waste:
            waste_type = WasteType(**waste_data)
            db.add(waste_type)
    
    db.commit()
    print(f"✅ Created {len(waste_types_data)} waste types")


def create_sample_rewards(db):
    """Create sample rewards"""
    print("Creating sample rewards...")
    
    rewards_data = [
        {
            "name": "Café Gratis",
            "description": "Un café americano o espresso gratis",
            "type": RewardType.FREE_ITEM,
            "points_required": 100,
            "monetary_value": 35.0,
            "currency": "MXN",
            "total_quantity": 500,
            "remaining_quantity": 500,
            "category": "bebidas",
            "valid_until": datetime.now(timezone.utc) + timedelta(days=365)
        },
        {
            "name": "Descuento 15% en tu próxima comida",
            "description": "15% de descuento en cualquier platillo del menú",
            "type": RewardType.DISCOUNT,
            "points_required": 250,
            "monetary_value": 75.0,
            "currency": "MXN",
            "discount_percentage": 15.0,
            "total_quantity": 200,
            "remaining_quantity": 200,
            "category": "descuentos",
            "valid_until": datetime.now(timezone.utc) + timedelta(days=365)
        },
        {
            "name": "Postre Gratis",
            "description": "Cualquier postre del menú sin costo",
            "type": RewardType.FREE_ITEM,
            "points_required": 150,
            "monetary_value": 55.0,
            "currency": "MXN",
            "total_quantity": 300,
            "remaining_quantity": 300,
            "category": "postres",
            "valid_until": datetime.now(timezone.utc) + timedelta(days=365)
        },
        {
            "name": "Bolsa Ecológica EcoRewards",
            "description": "Bolsa reutilizable de material reciclado",
            "type": RewardType.MERCHANDISE,
            "points_required": 500,
            "monetary_value": 120.0,
            "currency": "MXN",
            "total_quantity": 100,
            "remaining_quantity": 100,
            "category": "merchandise",
            "valid_until": datetime.now(timezone.utc) + timedelta(days=365)
        },
        {
            "name": "Experiencia de Compostaje",
            "description": "Taller de 2 horas sobre compostaje doméstico",
            "type": RewardType.EXPERIENCE,
            "points_required": 800,
            "monetary_value": 200.0,
            "currency": "MXN",
            "total_quantity": 50,
            "remaining_quantity": 50,
            "category": "experiencias",
            "valid_until": datetime.now(timezone.utc) + timedelta(days=365)
        }
    ]
    
    for reward_data in rewards_data:
        existing_reward = db.query(Reward).filter(Reward.name == reward_data["name"]).first()
        if not existing_reward:
            reward = Reward(**reward_data)
            db.add(reward)
    
    db.commit()
    print(f"✅ Created {len(rewards_data)} sample rewards")


async def main():
    """Main initialization function"""
    print("🌱 Initializing EcoRewards database with sample data...")
    
    try:
        # Initialize database
        await init_db()
        
        # Create sample data
        db = SessionLocal()
        
        try:
            create_sample_users(db)
            create_sample_branches(db)
            create_waste_types(db)
            create_sample_rewards(db)
            
            print("\n🎉 Database initialization completed successfully!")
            print("\nSample accounts created:")
            print("👤 Admin: admin@ecorewards.com / AdminPassword123")
            print("👤 User: maria.rodriguez@gmail.com / UserPassword123")
            print("👤 User: carlos.silva@gmail.com / UserPassword123")
            print("👤 User: ana.lopez@gmail.com / UserPassword123")
            
        finally:
            db.close()
            
    except Exception as e:
        print(f"❌ Database initialization failed: {str(e)}")
        raise


if __name__ == "__main__":
    asyncio.run(main())

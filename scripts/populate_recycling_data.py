#!/usr/bin/env python3
"""
Populate recycling events data for environmental statistics endpoint
"""

import asyncio
import sys
import os
from datetime import datetime, timedelta, timezone
import random
from faker import Faker

# Add app to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.session import SessionLocal
from app.models.user import User
from app.models.branch import Branch
from app.models.waste_type import WasteType
from app.models.purchase import Purchase
from app.models.recycling import RecyclingEvent, RecyclingItem, RecyclingStatus, ValidationStatus

fake = Faker('es_ES')


def create_recycling_events(db, num_events=150):
    """Create recycling events with items for the last 45 days"""
    print(f"Creating {num_events} recycling events...")
    
    # Get existing data
    users = db.query(User).filter(User.is_admin == False).all()
    branches = db.query(Branch).all()
    waste_types = db.query(WasteType).all()
    purchases = db.query(Purchase).all()
    
    if not users or not branches or not waste_types:
        print("❌ Need users, branches, and waste_types to create recycling events")
        return
    
    # If no purchases exist, create some
    if not purchases:
        print("Creating some purchases first...")
        for i in range(50):        purchase = Purchase(
            user_id=random.choice(users).id,
            branch_id=random.choice(branches).id,
            purchase_code=f"PUR-{fake.random_number(digits=8)}",
            total_amount=round(random.uniform(50, 500), 2),
            currency="MXN",
            payment_method="card",
            created_at=datetime.now(timezone.utc) - timedelta(days=random.randint(1, 60))
        )
        db.add(purchase)
        db.commit()
        purchases = db.query(Purchase).all()
    
    events_created = 0
    
    for i in range(num_events):
        # Random date in last 45 days
        event_date = datetime.now(timezone.utc) - timedelta(
            days=random.randint(1, 45),
            hours=random.randint(0, 23),
            minutes=random.randint(0, 59)
        )
        
        # Create recycling event
        user = random.choice(users)
        branch = random.choice(branches)
        purchase = random.choice([p for p in purchases if p.user_id == user.id] or purchases)
        
        # Generate realistic accuracy score (most events should be good)
        accuracy = random.choices(
            [85, 90, 95, 100],  # Values
            [20, 30, 35, 15]    # Weights (probability)
        )[0] + random.uniform(-5, 5)  # Add some variance
        accuracy = max(70, min(100, accuracy))  # Clamp between 70-100
        
        event = RecyclingEvent(
            user_id=user.id,
            purchase_id=purchase.id,
            branch_id=branch.id,
            event_code=f"REC-{fake.random_number(digits=8)}",
            status=RecyclingStatus.COMPLETED,
            validation_status=ValidationStatus.VALIDATED,
            accuracy_score=round(accuracy, 1),
            ai_confidence_score=round(random.uniform(0.75, 0.98), 3),
            qr_scanned_at=event_date,
            validation_started_at=event_date + timedelta(minutes=1),
            validation_completed_at=event_date + timedelta(minutes=random.randint(2, 8)),
            created_at=event_date,
            updated_at=event_date + timedelta(minutes=10)
        )
        
        db.add(event)
        db.flush()  # Get the ID
        
        # Add 1-5 recycling items per event
        num_items = random.choices([1, 2, 3, 4, 5], [40, 30, 15, 10, 5])[0]
        total_weight = 0
        total_carbon = 0
        total_points = 0
        
        for j in range(num_items):
            waste_type = random.choice(waste_types)
            
            # Realistic weights by category
            weight_ranges = {
                'plastic': (0.05, 0.3),   # 50g - 300g for plastic bottles
                'paper': (0.1, 0.5),      # 100g - 500g for cardboard
                'metal': (0.02, 0.15),    # 20g - 150g for cans
                'glass': (0.2, 0.8),      # 200g - 800g for glass bottles
                'organic': (0.1, 2.0),    # 100g - 2kg for organic waste
                'electronic': (0.1, 1.5)  # 100g - 1.5kg for electronics
            }
            
            weight_range = weight_ranges.get(waste_type.category, (0.1, 0.5))
            weight = round(random.uniform(*weight_range), 3)
            
            # Calculate if correctly classified (based on accuracy)
            is_correct = random.random() < (accuracy / 100)
            confidence = random.uniform(0.7, 0.95) if is_correct else random.uniform(0.4, 0.7)
            
            # Points calculation
            base_points = waste_type.recycling_points
            points_potential = base_points * 1  # Base points
            points_awarded = int(points_potential * (accuracy / 100)) if is_correct else 0
            
            item = RecyclingItem(
                recycling_event_id=event.id,
                waste_type_id=waste_type.id,
                name=f"{waste_type.name} #{j+1}",
                quantity=1,
                weight_recycled=weight,
                is_correctly_classified=is_correct,
                predicted_bin=waste_type.bin_color,
                actual_bin=waste_type.bin_color if is_correct else random.choice(['yellow', 'blue', 'green', 'gray']),
                confidence_score=round(confidence, 3),
                points_potential=points_potential,
                points_awarded=points_awarded,
                validation_notes="AI validated" if is_correct else "Minor classification error",
                created_at=event_date
            )
            
            db.add(item)
            
            total_weight += weight
            total_carbon += weight * waste_type.carbon_footprint_per_kg
            total_points += points_awarded
        
        # Update event with totals
        event.total_weight_recycled = round(total_weight, 3)
        event.carbon_footprint_reduced = round(total_carbon, 3)
        event.points_earned = total_points
        event.points_potential = sum(item.points_potential for item in event.items)
        
        events_created += 1
        
        if events_created % 25 == 0:
            print(f"✅ Created {events_created} recycling events...")
            db.commit()
    
    db.commit()
    print(f"✅ Successfully created {events_created} recycling events with items")
    
    # Print some statistics
    total_events = db.query(RecyclingEvent).count()
    total_items = db.query(RecyclingItem).count()
    
    from sqlalchemy import func
    total_weight = db.query(func.sum(RecyclingEvent.total_weight_recycled)).scalar() or 0
    total_carbon = db.query(func.sum(RecyclingEvent.carbon_footprint_reduced)).scalar() or 0
    
    print(f"\n📊 Database Summary:")
    print(f"   Total Recycling Events: {total_events}")
    print(f"   Total Recycling Items: {total_items}")
    print(f"   Total Weight Recycled: {total_weight:.2f} kg")
    print(f"   Total Carbon Reduced: {total_carbon:.2f} kg CO₂")


def create_additional_purchases(db, num_purchases=100):
    """Create additional purchases to support recycling events"""
    print(f"Creating {num_purchases} additional purchases...")
    
    users = db.query(User).filter(User.is_admin == False).all()
    branches = db.query(Branch).all()
    
    for i in range(num_purchases):
        purchase_date = datetime.now(timezone.utc) - timedelta(
            days=random.randint(1, 60),
            hours=random.randint(8, 22),
            minutes=random.randint(0, 59)
        )
        
        purchase = Purchase(
            user_id=random.choice(users).id,
            branch_id=random.choice(branches).id,
            purchase_code=f"PUR-{fake.random_number(digits=8)}",
            total_amount=round(random.uniform(45, 650), 2),
            currency="MXN",
            payment_method=random.choice(["card", "cash", "digital_wallet"]),
            created_at=purchase_date,
            updated_at=purchase_date + timedelta(minutes=5)
        )
        db.add(purchase)
    
    db.commit()
    print(f"✅ Created {num_purchases} additional purchases")


async def main():
    """Main function to populate recycling data"""
    print("🌱 Populating recycling events for environmental statistics...")
    
    try:
        db = SessionLocal()
        
        try:
            # Check if we have the required base data
            user_count = db.query(User).filter(User.is_admin == False).count()
            branch_count = db.query(Branch).count()
            waste_type_count = db.query(WasteType).count()
            
            print(f"📋 Base data check:")
            print(f"   Users: {user_count}")
            print(f"   Branches: {branch_count}")
            print(f"   Waste Types: {waste_type_count}")
            
            if user_count < 10 or branch_count < 3 or waste_type_count < 3:
                print("⚠️  Warning: Limited base data. Run populate_minimal.py first for better results.")
            
            # Create additional purchases if needed
            purchase_count = db.query(Purchase).count()
            if purchase_count < 50:
                create_additional_purchases(db, 100)
            
            # Create recycling events
            existing_events = db.query(RecyclingEvent).count()
            events_to_create = max(150 - existing_events, 50)
            
            create_recycling_events(db, events_to_create)
            
            print("\n🎉 Recycling data population completed!")
            print("\nYou can now test the environmental stats endpoint:")
            print("GET /api/v1/admin/stats/environmental")
            
        finally:
            db.close()
            
    except Exception as e:
        print(f"❌ Error populating recycling data: {str(e)}")
        raise


if __name__ == "__main__":
    asyncio.run(main())

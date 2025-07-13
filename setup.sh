#!/bin/bash

# EcoRewards Backend - Development Setup Script

echo "🌱 Setting up EcoRewards Backend for development..."

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    cp .env.example .env
    echo "✅ Created .env file. Please review and update the configuration."
fi

# Create upload directory
echo "📁 Creating upload directory..."
mkdir -p uploads

# Build and start services
echo "🐳 Building and starting Docker services..."
docker-compose up --build -d

# Wait for services to be ready
echo "⏳ Waiting for services to be ready..."
sleep 10

# Check if services are running
echo "🔍 Checking service status..."
docker-compose ps

# Initialize database with sample data
echo "🗄️ Initializing database with sample data..."
docker-compose exec api python scripts/init_db.py

echo ""
echo "🎉 EcoRewards Backend setup completed!"
echo ""
echo "🔗 Service URLs:"
echo "   API Documentation: http://localhost:8000/docs"
echo "   API Health Check: http://localhost:8000/health"
echo "   PostgreSQL: localhost:5432"
echo "   MongoDB: localhost:27017"
echo "   Redis: localhost:6379"
echo ""
echo "👤 Test Accounts:"
echo "   Admin: admin@ecorewards.com / AdminPassword123"
echo "   User: maria.rodriguez@gmail.com / UserPassword123"
echo ""
echo "📖 Next steps:"
echo "   1. Review the .env file and update configurations"
echo "   2. Visit http://localhost:8000/docs to explore the API"
echo "   3. Test the endpoints using the provided accounts"
echo ""
echo "🛠️ Useful commands:"
echo "   View logs: docker-compose logs -f"
echo "   Stop services: docker-compose down"
echo "   Restart services: docker-compose restart"
echo "   Run tests: docker-compose exec api pytest"

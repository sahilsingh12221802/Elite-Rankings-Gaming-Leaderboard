#!/bin/bash
# Gaming Leaderboard System - Quick Start Script

set -e

echo "🎮 Gaming Leaderboard System - Quick Start"
echo "=========================================="

# Check Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker not found. Please install Docker first."
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose not found. Please install Docker Compose first."
    exit 1
fi

echo "✓ Docker and Docker Compose are installed"

# Navigate to project directory
PROJECT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$PROJECT_DIR"

# Create .env if doesn't exist
if [ ! -f "backend/.env" ]; then
    echo "📝 Creating .env from .env.example..."
    cp backend/.env.example backend/.env
fi

# Start services
echo "🚀 Starting services..."
docker-compose up -d

echo ""
echo "⏳ Waiting for services to initialize..."
sleep 10

# Check if services are running
echo ""
echo "🔍 Checking service status..."
docker-compose ps

# Test backend health
echo ""
echo "🧪 Testing backend health..."
if curl -s http://localhost:8000/health > /dev/null; then
    echo "✓ Backend is healthy"
else
    echo "⚠️ Backend is still initializing, wait a moment..."
    sleep 5
fi

echo ""
echo "✅ Setup complete!"
echo ""
echo "🎮 Access the application:"
echo "   Frontend: http://localhost:3000"
echo "   Backend API: http://localhost:8000"
echo "   API Docs: http://localhost:8000/docs"
echo ""
echo "📊 Database:"
echo "   PostgreSQL: localhost:5432 (user/password)"
echo "   Redis: localhost:6379"
echo ""
echo "📚 Documentation:"
echo "   Architecture: ARCHITECTURE.md"
echo "   Setup Guide: SETUP.md"
echo ""
echo "🛑 To stop services: docker-compose stop"
echo "🗑️ To remove containers: docker-compose down"
echo ""

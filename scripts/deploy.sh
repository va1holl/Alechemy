#!/bin/bash
# =============================================================================
# Production Deployment Script for Alechemy
# Usage: ./scripts/deploy.sh
# =============================================================================

set -e

echo "🚀 Alechemy Production Deployment"
echo "=================================="

# Check if .env.prod exists
if [ ! -f ".env.prod" ]; then
    echo "❌ .env.prod file not found!"
    echo "   Please create it from .env.prod.example"
    exit 1
fi

# Check if SSL certificates exist
if [ ! -f "nginx/ssl/fullchain.pem" ] || [ ! -f "nginx/ssl/privkey.pem" ]; then
    echo "⚠️  SSL certificates not found in nginx/ssl/"
    echo "   Please add fullchain.pem and privkey.pem"
    read -p "Continue without SSL? (yes/no): " CONTINUE
    if [ "$CONTINUE" != "yes" ]; then
        exit 1
    fi
fi

echo ""
echo "📦 Building Docker images..."
docker-compose -f docker-compose.prod.yml build

echo ""
echo "🔄 Starting services..."
docker-compose -f docker-compose.prod.yml up -d

echo ""
echo "⏳ Waiting for database to be ready..."
sleep 10

echo ""
echo "🔧 Running migrations..."
docker exec alechemy_web python manage.py migrate --noinput

echo ""
echo "📁 Collecting static files..."
docker exec alechemy_web python manage.py collectstatic --noinput

echo ""
echo "🔍 Running system checks..."
docker exec alechemy_web python manage.py check --deploy

echo ""
echo "✅ Deployment completed!"
echo ""
echo "📊 Service status:"
docker-compose -f docker-compose.prod.yml ps

echo ""
echo "📝 Next steps:"
echo "   1. Create superuser: docker exec -it alechemy_web python manage.py createsuperuser"
echo "   2. Check logs: docker-compose -f docker-compose.prod.yml logs -f"
echo "   3. Access site: https://your-domain.com"

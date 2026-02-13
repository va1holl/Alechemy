#!/bin/bash
# =============================================================================
# Development entrypoint script for Alechemy
# Runs migrations and seeds automatically on container start
# =============================================================================

set -e

echo "🚀 Starting Alechemy development container..."

# Wait for database to be ready
echo "⏳ Waiting for database..."
until python manage.py check --database default > /dev/null 2>&1; do
    echo "  Waiting for database connection..."
    sleep 2
done
echo "✅ Database is ready!"

# Run database migrations
echo "📦 Running database migrations..."
python manage.py migrate --noinput

# Run seeds (only if tables are empty)
echo "🌱 Checking and running seeds..."

# Check if scenarios exist, if not - run seeds
python manage.py shell -c "
from events.models import Scenario, Drink, Dish
from recipes.models import Cocktail

if not Scenario.objects.exists():
    print('  → Running seed_scenarios...')
    from django.core.management import call_command
    call_command('seed_scenarios')
else:
    print('  → Scenarios already exist, skipping seed_scenarios')

if not Drink.objects.exists():
    print('  → Running seed_drinks...')
    from django.core.management import call_command
    call_command('seed_drinks')
else:
    print('  → Drinks already exist, skipping seed_drinks')

if not Dish.objects.exists():
    print('  → Running seed_dishes...')
    from django.core.management import call_command
    call_command('seed_dishes')
else:
    print('  → Dishes already exist, skipping seed_dishes')

# Re-run seed_drinks to link drinks to scenarios (if needed)
from events.models import Scenario
if Scenario.objects.exists() and Drink.objects.exists():
    # Check if any scenario has drinks linked
    if not Scenario.objects.filter(drinks__isnull=False).exists():
        print('  → Linking drinks to scenarios...')
        from django.core.management import call_command
        call_command('seed_drinks')

# Seed places (bars, shops, promotions on Kyiv map)
from places.models import Place
if not Place.objects.exists():
    print('  → Running seed_places...')
    from django.core.management import call_command
    call_command('seed_places')
else:
    print('  → Places already exist, skipping seed_places')
"

echo "✅ Seeds completed!"

# Execute the main command (runserver)
echo "🌐 Starting development server..."
exec "$@"

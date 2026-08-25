#!/usr/bin/env bash
# exit on error
set -o errexit

echo "📦 Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo "🎨 Collecting static files..."
python manage.py collectstatic --no-input

echo "🗄️ Running database migrations..."
python manage.py migrate --no-input

echo "🌱 Ensuring seed data / superuser setup..."
# If SEED_MODE is enabled or first run, seeds can run safely
python manage.py seed || true

echo "✅ Build completed successfully!"

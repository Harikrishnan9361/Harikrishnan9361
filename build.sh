#!/usr/bin/env bash
# Exit immediately on error
set -o errexit

# Upgrade pip & install production requirements
pip install --upgrade pip
pip install -r requirements.txt

# Collect static files
python manage.py collectstatic --noinput

# Run database migrations
python manage.py migrate --noinput

# Seed initial categories & destinations (idempotent)
python manage.py seed_data

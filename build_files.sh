#!/usr/bin/env bash
# Build script for Vercel deployment
python3 -m pip install --upgrade pip
python3 -m pip install -r requirements.txt
python3 manage.py collectstatic --noinput --clear


#!/usr/bin/env bash
# Render build script
set -o errexit

pip install -r requirements.txt
python manage.py collectstatic --no-input
python manage.py migrate
python manage.py ensure_admin
python manage.py shell < seed_class2_math_questions.py

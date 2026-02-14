#!/usr/bin/env bash
# Render build script — runs during every deploy

set -o errexit

pip install -r requirements.txt

python manage.py collectstatic --noinput
python manage.py migrate
python manage.py seed_rules

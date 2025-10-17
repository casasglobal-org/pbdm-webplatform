#!/bin/bash
cd casas_web_portal
python3 manage.py collectstatic --no-input
# execute migrations
python3 manage.py migrate
# create translation
python3 manage.py compilemessages

# create user if it doesn't exists
if [ "$(python3 manage.py dbshell -- -c '\dt core_user' 2>/dev/null|wc -l)" == "0" ]; then
  DJANGO_SUPERUSER_USERNAME="${CASAS_USER}" \
  DJANGO_SUPERUSER_EMAIL="${CASAS_EMAIL}" \
  DJANGO_SUPERUSER_PASSWORD="${CASAS_PASSWORD}" \
  python3 manage.py createsuperuser --no-input
fi

exec gunicorn \
     -b 0.0.0.0:8080 \
     --access-logfile - \
     --error-logfile - \
     --timeout ${APP_TIMEOUT} \
     --workers ${APP_WORKERS} \
     casas_web_portal.wsgi:application

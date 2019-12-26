#!/bin/bash

set -e
set -x

cmd="$@"

until redis-cli -h db -p 6379; do
  >&2 echo "Redis is unavailabe"
  sleep 1
done

>&2 echo "Redis is up - executing command"

until python manage.py makemigrations; do
  sleep 1
done

until python manage.py migrate; do
  sleep 1
done

>&2 echo "Migration completed ..."

exec $cmd
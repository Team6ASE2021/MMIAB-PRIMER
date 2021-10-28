#!/usr/bin/env bash

# start redis
redis-server& >> redis.log

# start celery (only for temporal tasks)
celery -A monolith.background worker -B --loglevel=info& >> celery.log

# start celery (for all tasks)
# celery -A monolith.background worker --loglevel=info

# start flask
export FLASK_APP=monolith
export FLASK_ENV=development
export FLASK_DEBUG=true
flask run

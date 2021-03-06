#!/usr/bin/env bash
mkdir -p ./monolith/db
# stop redis if running
pgrep -x redis-server >/dev/null && sudo killall -9 redis-server
# start redis
redis-server &>redis.log &

# stop celery if running
pgrep -x celery >/dev/null && killall -9 celery
# start celery (only for temporal tasks)
celery -b redis://localhost:6379/0 --result-backend redis://localhost:6379 -A monolith.background worker  -B --loglevel=info &>celery.log &# start celery (for all tasks)
# celery -A monolith.background worker --loglevel=info

# start flask
export FLASK_APP=monolith
export FLASK_ENV=development
export FLASK_DEBUG=true
flask run



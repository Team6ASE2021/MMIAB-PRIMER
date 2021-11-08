#!/usr/bin/env bash
mkdir -p /var/run/celery /var/log/celery


exec  celery -A monolith.background worker \
             -B --loglevel=info \
             --logfile=/var/log/celery/worker.log \
             --statedb=/var/run/celery/worker-example@%h.state \
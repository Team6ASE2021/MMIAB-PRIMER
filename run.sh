#!/usr/bin/env bash
mkdir -p ./monolith/db

export FLASK_APP=monolith
export FLASK_ENV=development
export FLASK_DEBUG=true
flask run --host=0.0.0.0

#!/bin/sh

if [ "$1" == "api" ]; then
    NPROC=$(grep -c ^processor /proc/cpuinfo 2>/dev/null || echo -n 1)
    shift
    exec gunicorn api:api -w ${GUNICORN_WORKERS:-$NPROC} -b 0.0.0.0 "$@"
elif [ "$1" == "worker" ]; then
    shift
    exec python worker.py "$@"
else
    cat <<EOF
Unknown command $1
Usage: (api|worker) [options]
EOF
    exit 1
fi

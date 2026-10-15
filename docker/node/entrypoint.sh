#!/bin/sh
set -eu
# Docker stops npm without necessarily forwarding the signal to Vite.
# Always remove Vite's hot marker when a development session ends.
if [ "$#" -ge 3 ] && [ "$1" = npm ] && [ "$2" = run ] && [ "$3" = dev ]; then
    trap 'rm -f /var/www/html/public/hot' EXIT
    trap 'exit 0' INT TERM
    "$@" &
    wait "$!"
else
    exec docker-entrypoint.sh "$@"
fi

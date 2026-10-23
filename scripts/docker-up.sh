#!/usr/bin/env sh
# Запуск из любой директории; существующий .env не изменяется.
set -eu

cd "$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)"

case "${1:-}" in
  "")
    if [ "$#" -ne 0 ]; then
      echo "Использование: $0 [--mock]" >&2
      exit 2
    fi
    docker compose up -d --build --wait
    ;;
  --mock)
    if [ "$#" -ne 1 ]; then
      echo "Использование: $0 [--mock]" >&2
      exit 2
    fi
    docker compose -f docker-compose.yml -f docker-compose.mock.yml up -d --build --wait
    ;;
  *)
    echo "Использование: $0 [--mock]" >&2
    exit 2
    ;;
esac

echo "Интерфейс: http://localhost:5173"
echo "API / Swagger: http://localhost:8000/docs"

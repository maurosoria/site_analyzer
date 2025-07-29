#!/bin/bash
SERVICE_TYPE=$1

case $SERVICE_TYPE in
  rest)
    curl -f http://localhost:5000/api/v1/health || exit 1
    ;;
  grpc)
    if command -v grpcurl &> /dev/null; then
      grpcurl -plaintext localhost:50051 grpc.health.v1.Health/Check || exit 1
    else
      nc -z localhost 50051 || exit 1
    fi
    ;;
  cli)
    ps aux | grep "[p]ython main_refactored.py" || exit 1
    ;;
  *)
    echo "Unknown service type: $SERVICE_TYPE"
    exit 1
    ;;
esac

exit 0

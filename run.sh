#!/usr/bin/env bash
# Simple runner to start backend and frontend (assumes dependencies installed)
echo "Starting backend on http://localhost:8000"
cd backend
uvicorn app:app --reload --port 8000 &
BACK_PID=$!
cd ..
if [ -d frontend ]; then
  echo "Starting frontend on http://localhost:3000"
  cd frontend
  npm install
  npm run dev &
  FRONT_PID=$!
fi

echo "Backend PID: $BACK_PID, Frontend PID: ${FRONT_PID:-none}"
echo "Run 'kill $BACK_PID ${FRONT_PID:-}' to stop"

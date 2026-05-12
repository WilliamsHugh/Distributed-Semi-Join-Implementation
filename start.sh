#!/bin/bash
echo "Starting Node 1 (Employee) on port 8001..."
source venv/bin/activate
nohup uvicorn node1.main:app --port 8001 > node1.log 2>&1 &

echo "Starting Node 2 (Assignment) on port 8002..."
nohup uvicorn node2.main:app --port 8002 > node2.log 2>&1 &

echo "Starting Coordinator (UI) on port 8000..."
nohup uvicorn coordinator.main:app --port 8000 > coordinator.log 2>&1 &

echo "All services started!"
echo "Please wait a few seconds and go to http://127.0.0.1:8000"
echo "To view logs, you can check node1.log, node2.log, and coordinator.log"

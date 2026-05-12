#!/bin/bash
echo "Stopping all Uvicorn services (Node 1, Node 2, Coordinator)..."
pkill -f uvicorn

if [ $? -eq 0 ]; then
    echo "Services stopped successfully."
else
    echo "No running services found."
fi

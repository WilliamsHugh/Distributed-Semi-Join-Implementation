# Distributed Semi-Join Optimization (Topic #11)

<video src="./proof_video.mp4" controls="controls" width="100%">
  Trình duyệt của bạn không hỗ trợ thẻ video.
</video>

This project demonstrates the performance benefits of using a **Distributed Semi-Join** algorithm compared to a standard **Ship-Whole-Table** approach in a distributed database environment.

## Project Structure
- `node1/`: Employee Site (10,000 records).
- `node2/`: Assignment Site (50,000 records).
- `coordinator/`: Orchestrator and Web UI for demonstrating the performance difference.
- `data/`: Directory where mock data is generated.

## Getting Started

### 1. Prerequisites
- Python 3.10+
- Virtual environment (recommended)

### 2. Setup
Install the required dependencies:
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Data Generation
Generate the mock datasets:
```bash
python3 generate_data.py
```

### 4. Running the Demo
You can start all three nodes using the provided script:
```bash
./start.sh
```
The Web UI will be available at [http://127.0.0.1:8000](http://127.0.0.1:8000).

To stop all services:
```bash
./stop.sh
```

## Features
- **Interactive UI**: Real-time comparison of Bytes Transferred and Execution Time.
- **Cost Analysis**: Verification of theoretical cost reduction using the Semi-Join operator.
- **Failure Handling**: Demonstration of system reliability when a participant node fails.

## Theory
This implementation is based on the theory from *"Principles of Distributed Database Systems"* by M. Tamer Özsu and Patrick Valduriez.

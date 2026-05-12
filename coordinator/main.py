from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import httpx
import time
import os

app = FastAPI(title="Distributed Database Demo UI")

NODE1_URL = "http://127.0.0.1:8001"
NODE2_URL = "http://127.0.0.1:8002"

# Mount static files
static_dir = os.path.join(os.path.dirname(__file__), "static")
app.mount("/static", StaticFiles(directory=static_dir), name="static")

@app.get("/", response_class=HTMLResponse)
async def read_index():
    with open(os.path.join(static_dir, "index.html"), "r") as f:
        return f.read()

def measure_request(method, url, json_data=None):
    start_time = time.time()
    try:
        with httpx.Client(timeout=10.0) as client:
            if method == 'GET':
                response = client.get(url)
            elif method == 'POST':
                response = client.post(url, json=json_data)
            response.raise_for_status()
            
            bytes_transferred = len(response.content)
            data = response.json()
            end_time = time.time()
            return data, bytes_transferred, end_time - start_time
    except httpx.RequestError as e:
        print(f"Request Error: {e}")
        return None, 0, time.time() - start_time

@app.get("/api/run-standard")
def api_run_standard():
    assignments, b1, t1 = measure_request('GET', f"{NODE2_URL}/assignments")
    if not assignments: return {"error": "Failed to contact Node 2"}
    
    employees, b2, t2 = measure_request('GET', f"{NODE1_URL}/employees")
    if not employees: return {"error": "Failed to contact Node 1"}
    
    start_join = time.time()
    emp_dict = {e['EmpID']: e for e in employees}
    joined_data = []
    
    unique_emp_ids = set([a['EmpID'] for a in assignments])
    for emp_id in unique_emp_ids:
        if emp_id in emp_dict:
            joined_data.append(emp_dict[emp_id])
            
    end_join = time.time()
    
    total_bytes = b1 + b2
    total_time = t1 + t2 + (end_join - start_join)
    
    # Return a sample of up to 100 to avoid freezing the browser
    return {
        "metrics": {
            "bytesTransferred": total_bytes,
            "executionTime": total_time,
            "node1Bytes": b2,
            "node2Bytes": b1,
            "resultCount": len(joined_data)
        },
        "results": joined_data[:100]
    }

@app.get("/api/run-semi-join")
def api_run_semi_join():
    response_data, b1, t1 = measure_request('GET', f"{NODE2_URL}/assignments/unique-empids")
    if not response_data: return {"error": "Failed to contact Node 2"}
        
    unique_emp_ids = response_data['emp_ids']
    
    employees, b2, t2 = measure_request('POST', f"{NODE1_URL}/employees/semi-join", json_data={"emp_ids": unique_emp_ids})
    if not employees: return {"error": "Failed to contact Node 1"}
    
    b_request = len(str({"emp_ids": unique_emp_ids}).encode('utf-8'))
    
    total_bytes = b1 + b2 + b_request
    total_time = t1 + t2
    
    return {
        "metrics": {
            "bytesTransferred": total_bytes,
            "executionTime": total_time,
            "node1Bytes": b2,
            "node2Bytes": b1,
            "requestBytes": b_request,
            "resultCount": len(employees)
        },
        "results": employees[:100]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

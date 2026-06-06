from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import httpx
import time
import os

app = FastAPI(title="Distributed Database Demo UI")

NODE1_URL = "http://127.0.0.1:8001"
NODE2_URL = "http://127.0.0.1:8002"
NODE3_URL = "http://127.0.0.1:8003"

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

def get_node_metadata(node_url):
    """Fetch the EmpID range metadata from an employee node."""
    data, _, _ = measure_request('GET', f"{node_url}/metadata")
    return data

def emp_ids_overlap(emp_ids_set: set, metadata: dict) -> bool:
    """
    Fragment Pruning: Check if any EmpID in the query overlaps
    with the EmpID range stored at a given node fragment.
    If no overlap, this node can be safely PRUNED (skipped).
    """
    if not metadata or metadata.get('min_id') is None:
        return False
    min_id = metadata['min_id']
    max_id = metadata['max_id']
    return any(min_id <= eid <= max_id for eid in emp_ids_set)

@app.get("/api/fragment-info")
def api_fragment_info():
    """Returns metadata from all employee nodes for visualization."""
    meta1 = get_node_metadata(NODE1_URL)
    meta3 = get_node_metadata(NODE3_URL)
    return {"node1": meta1, "node3": meta3}

@app.get("/api/run-standard")
def api_run_standard(prefix: str = ""):
    assignments, b1, t1 = measure_request('GET', f"{NODE2_URL}/assignments")
    if not assignments: return {"error": "Failed to contact Node 2"}

    employees_1, b2, t2 = measure_request('GET', f"{NODE1_URL}/employees")
    if not employees_1: return {"error": "Failed to contact Node 1"}

    employees_3, b3, t3 = measure_request('GET', f"{NODE3_URL}/employees")
    if not employees_3: return {"error": "Failed to contact Node 3"}

    employees = employees_1 + employees_3

    start_join = time.time()
    emp_dict = {e['EmpID']: e for e in employees}
    joined_data = []
    unique_emp_ids = set([a['EmpID'] for a in assignments if a['EmpID'].startswith(prefix)])
    for emp_id in unique_emp_ids:
        if emp_id in emp_dict:
            joined_data.append(emp_dict[emp_id])
    end_join = time.time()

    total_bytes = b1 + b2 + b3
    total_time = t1 + max(t2, t3) + (end_join - start_join)

    return {
        "metrics": {
            "bytesTransferred": total_bytes,
            "executionTime": total_time,
            "node1Bytes": b2,
            "node2Bytes": b1,
            "node3Bytes": b3,
            "resultCount": len(joined_data)
        },
        "trace": [
            {"step": 1, "desc": "Requesting all Assignments from Node 2", "site": "Node 2", "cost": f"{b1:,} bytes", "type": "normal"},
            {"step": 2, "desc": "Requesting Employees (Part 1) from Node 1", "site": "Node 1", "cost": f"{b2:,} bytes", "type": "normal"},
            {"step": 3, "desc": "Requesting Employees (Part 2) from Node 3", "site": "Node 3", "cost": f"{b3:,} bytes", "type": "normal"},
            {"step": 4, "desc": "No Localization: ALL fragments fetched regardless of relevance", "site": "Coordinator", "cost": "Wasteful", "type": "warning"},
            {"step": 5, "desc": "Performing Local Join at Coordinator", "site": "Coordinator", "cost": "CPU heavy", "type": "normal"}
        ],
        "cost_analysis": {
            "formula": "Total_Cost = (C_msg * #msgs) + (C_tr * #bytes)",
            "c_msg": 10,
            "c_tr": 0.001,
            "msgs": 3,
            "bytes": total_bytes,
            "calculated_comm_cost": (10 * 3) + (0.001 * total_bytes)
        },
        "results": joined_data[:100]
    }

@app.get("/api/run-semi-join")
def api_run_semi_join(prefix: str = ""):
    # Step 1: Get unique EmpIDs from Node 2
    response_data, b1, t1 = measure_request('GET', f"{NODE2_URL}/assignments/unique-empids")
    if not response_data: return {"error": "Failed to contact Node 2"}
    
    all_emp_ids = response_data['emp_ids']
    unique_emp_ids = [eid for eid in all_emp_ids if eid.startswith(prefix)]
    unique_emp_ids_set = set(unique_emp_ids)

    # Step 2: Fragment Pruning — query metadata catalogs (no data transfer)
    meta1 = get_node_metadata(NODE1_URL)
    meta3 = get_node_metadata(NODE3_URL)

    node1_relevant = emp_ids_overlap(unique_emp_ids_set, meta1)
    node3_relevant = emp_ids_overlap(unique_emp_ids_set, meta3)

    pruning_trace = [
        {"step": 1, "desc": "Projecting unique EmpIDs at Node 2", "site": "Node 2", "cost": "CPU light", "type": "normal"},
        {"step": 2, "desc": f"Fetching EmpIDs to Coordinator ({len(all_emp_ids):,} unique IDs)", "site": "Node 2 -> Coord", "cost": f"{b1:,} bytes", "type": "normal"},
    ]
    if prefix:
        pruning_trace.append({"step": len(pruning_trace)+1, "desc": f"Selection Predicate applied: EmpID LIKE '{prefix}%' → {len(unique_emp_ids):,} match", "site": "Coordinator", "cost": "Predicate filter", "type": "prune"})

    pruning_trace.extend([
        {"step": len(pruning_trace)+1, "desc": f"Query Localization: Check Node 1 catalog (range: {meta1['min_id']} to {meta1['max_id']})", "site": "Coordinator", "cost": "0 bytes (catalog only)", "type": "prune"},
        {"step": len(pruning_trace)+2, "desc": f"Query Localization: Check Node 3 catalog (range: {meta3['min_id']} to {meta3['max_id']})", "site": "Coordinator", "cost": "0 bytes (catalog only)", "type": "prune"},
    ])

    step = len(pruning_trace) + 1
    employees = []
    b_request_total = 0
    b_results_total = 0
    t_filter_max = 0
    nodes_queried = []
    nodes_pruned = []

    if node1_relevant:
        nodes_queried.append("Node 1")
        b_req1 = len(str({"emp_ids": unique_emp_ids}).encode('utf-8'))
        b_request_total += b_req1
        emp1, b2, t2 = measure_request('POST', f"{NODE1_URL}/employees/semi-join", json_data={"emp_ids": unique_emp_ids})
        if emp1:
            employees += emp1
            b_results_total += b2
            t_filter_max = max(t_filter_max, t2)
            pruning_trace.append({"step": step, "desc": f"Semi-Join at Node 1: {len(emp1):,} matches found", "site": "Node 1", "cost": f"{b2:,} bytes returned", "type": "normal"})
            step += 1
    else:
        nodes_pruned.append("Node 1")
        pruning_trace.append({"step": step, "desc": "PRUNED: Node 1 skipped — no matching EmpIDs in its range", "site": "Node 1", "cost": "0 bytes (pruned)", "type": "pruned"})
        step += 1

    if node3_relevant:
        nodes_queried.append("Node 3")
        b_req3 = len(str({"emp_ids": unique_emp_ids}).encode('utf-8'))
        b_request_total += b_req3
        emp3, b3, t3 = measure_request('POST', f"{NODE3_URL}/employees/semi-join", json_data={"emp_ids": unique_emp_ids})
        if emp3:
            employees += emp3
            b_results_total += b3
            t_filter_max = max(t_filter_max, t3)
            pruning_trace.append({"step": step, "desc": f"Semi-Join at Node 3: {len(emp3):,} matches found", "site": "Node 3", "cost": f"{b3:,} bytes returned", "type": "normal"})
            step += 1
    else:
        nodes_pruned.append("Node 3")
        pruning_trace.append({"step": step, "desc": "PRUNED: Node 3 skipped — no matching EmpIDs in its range", "site": "Node 3", "cost": "0 bytes (pruned)", "type": "pruned"})
        step += 1

    pruning_trace.append({"step": step, "desc": f"Result: Queried [{', '.join(nodes_queried) or 'none'}] | Pruned [{', '.join(nodes_pruned) or 'none'}]", "site": "Coordinator", "cost": "Union complete", "type": "prune"})

    total_bytes = b1 + b_results_total + b_request_total
    total_time = t1 + t_filter_max

    return {
        "metrics": {
            "bytesTransferred": total_bytes,
            "executionTime": total_time,
            "node2Bytes": b1,
            "requestBytes": b_request_total,
            "resultBytes": b_results_total,
            "resultCount": len(employees),
            "nodesPruned": len(nodes_pruned),
            "nodesQueried": len(nodes_queried)
        },
        "trace": pruning_trace,
        "cost_analysis": {
            "formula": "Total_Cost = (C_msg * #msgs) + (C_tr * #bytes)",
            "c_msg": 10,
            "c_tr": 0.001,
            "msgs": 1 + len(nodes_queried) * 2,
            "bytes": total_bytes,
            "calculated_comm_cost": (10 * (1 + len(nodes_queried) * 2)) + (0.001 * total_bytes)
        },
        "results": employees[:100]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

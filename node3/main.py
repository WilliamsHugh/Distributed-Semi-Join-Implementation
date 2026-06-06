from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
import pandas as pd
import os

app = FastAPI(title="Node 3 - Employees (Part 2)")

# Load data into memory
data_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'employees_site3.csv')
try:
    df_employees = pd.read_csv(data_path)
except Exception as e:
    print(f"Error loading data: {e}")
    df_employees = pd.DataFrame()

class EmpIDList(BaseModel):
    emp_ids: List[str]

@app.get("/metadata")
def get_metadata():
    """
    Returns the metadata (EmpID range) for this node's fragment.
    Used by the Coordinator for Query Localization / Fragment Pruning.
    """
    if df_employees.empty:
        return {"node": "Node 3", "fragment": "employees_site3", "min_id": None, "max_id": None, "count": 0}
    return {
        "node": "Node 3",
        "fragment": "employees_site3",
        "min_id": df_employees['EmpID'].min(),
        "max_id": df_employees['EmpID'].max(),
        "count": len(df_employees)
    }

@app.get("/employees")
def get_all_employees():
    """Return all employees"""
    return df_employees.to_dict(orient="records")

@app.post("/employees/semi-join")
def semi_join_employees(payload: EmpIDList):
    """
    Takes a list of EmpIDs and returns matching employees.
    This simulates the filtering step of a Semi-Join.
    """
    target_ids = set(payload.emp_ids)
    # Filter the dataframe where EmpID is in the target_ids
    filtered_df = df_employees[df_employees['EmpID'].isin(target_ids)]
    return filtered_df.to_dict(orient="records")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8003)

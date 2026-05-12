from fastapi import FastAPI
import pandas as pd
import os

app = FastAPI(title="Node 2 - Assignments")

# Load data into memory
data_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'assignments.csv')
try:
    df_assignments = pd.read_csv(data_path)
except Exception as e:
    print(f"Error loading data: {e}")
    df_assignments = pd.DataFrame()

@app.get("/assignments")
def get_all_assignments():
    """Return all assignments"""
    return df_assignments.to_dict(orient="records")

@app.get("/assignments/unique-empids")
def get_unique_empids():
    """
    Return only the unique EmpIDs from the assignments table.
    This is the first step of a Semi-Join.
    """
    unique_ids = df_assignments['EmpID'].unique().tolist()
    return {"emp_ids": unique_ids}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)

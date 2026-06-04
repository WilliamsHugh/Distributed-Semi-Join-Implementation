import csv
import random
from faker import Faker
import os

fake = Faker()
Faker.seed(42)
random.seed(42)

NUM_EMPLOYEES = 10000
NUM_ASSIGNMENTS = 50000

DATA_DIR = 'data'
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

EMPLOYEES_FILE_1 = os.path.join(DATA_DIR, 'employees_site1.csv')
EMPLOYEES_FILE_3 = os.path.join(DATA_DIR, 'employees_site3.csv')
ASSIGNMENTS_FILE = os.path.join(DATA_DIR, 'assignments.csv')

def generate_data():
    print(f"Generating {NUM_EMPLOYEES} employees across Node 1 and Node 3...")
    employees = []
    emp_ids = []
    
    with open(EMPLOYEES_FILE_1, mode='w', newline='', encoding='utf-8') as f1, \
         open(EMPLOYEES_FILE_3, mode='w', newline='', encoding='utf-8') as f3:
        
        writer1 = csv.writer(f1)
        writer3 = csv.writer(f3)
        
        header = ['EmpID', 'Name', 'Department', 'Email', 'Salary']
        writer1.writerow(header)
        writer3.writerow(header)
        
        for i in range(1, NUM_EMPLOYEES + 1):
            emp_id = f"EMP{i:05d}"
            name = fake.name()
            department = fake.job()
            email = fake.email()
            salary = random.randint(30000, 150000)
            
            row = [emp_id, name, department, email, salary]
            if i <= NUM_EMPLOYEES // 2:
                writer1.writerow(row)
            else:
                writer3.writerow(row)
                
            emp_ids.append(emp_id)

    print(f"Generating {NUM_ASSIGNMENTS} assignments...")
    
    # Randomly select a subset of employees who actually have projects
    # Let's say 80% of employees have projects, some have multiple
    active_employees = random.sample(emp_ids, int(NUM_EMPLOYEES * 0.8))
    
    with open(ASSIGNMENTS_FILE, mode='w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['AssignID', 'EmpID', 'ProjectID', 'HoursLogged'])
        
        for i in range(1, NUM_ASSIGNMENTS + 1):
            assign_id = f"ASN{i:06d}"
            emp_id = random.choice(active_employees)
            project_id = f"PRJ{random.randint(1, 500):03d}"
            hours = random.randint(10, 500)
            
            writer.writerow([assign_id, emp_id, project_id, hours])
            
    print("Data generation complete!")

if __name__ == '__main__':
    generate_data()

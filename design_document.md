# Design Document: Distributed Semi-Join Optimization
**Team:** Data Mavericks  
**Course:** Distributed Database Systems

---

## 1. Introduction
This document outlines the design and theoretical justification for implementing a Distributed Semi-Join ($R \ltimes S$). The project addresses the problem of minimizing network communication cost in distributed query processing, a fundamental topic discussed in *Principles of Distributed Database Systems* by M. Tamer Özsu and Patrick Valduriez. 

Our system demonstrates this by evaluating a query spanning two nodes: one storing `Employees` ($R$) and another storing `Assignments` ($S$). We aim to find all employees currently working on at least one project.

## 2. Architecture & Components
The system is built on a 3-node simulated architecture using Python and FastAPI:
- **Node 1 (Employee Site):** Manages the `Employees` dataset (10,000 records). Exposes REST APIs for full retrieval and semi-join filtering.
- **Node 2 (Assignment Site):** Manages the `Assignments` dataset (50,000 records). Exposes REST APIs to retrieve full records or projected unique foreign keys.
- **Node 3 (Coordinator):** Orchestrates the query execution, measures payload sizes, and calculates total execution time. 

The rationale for using lightweight HTTP APIs (FastAPI) and Pandas DataFrames is to mimic real-world microservice communication while keeping I/O bound operations fast in-memory, allowing us to accurately observe network latency and bandwidth differences.

## 3. Distributed Query Processing (DQP) Logic

According to Özsu and Valduriez, distributed queries can be optimized by reducing the size of intermediate relations shipped across the network. 

### 3.1 Standard Join (Ship-Whole-Table)
In a naive standard join, Node 2 ships the entire `Assignments` table to the Coordinator (or directly to Node 1), followed by the entire `Employees` table. 
- **Bytes Transferred:** Size($S$) + Size($R$)
- **Disadvantage:** High communication cost, especially when $S$ is large.

### 3.2 Semi-Join ($R \ltimes S$)
The semi-join approach reduces the data transfer:
1. **Projection:** Node 2 projects the join attribute (`EmpID`) from $S$ and eliminates duplicates, creating $S'$. 
2. **Transfer:** Node 2 ships $S'$ to Node 1. Because $S'$ only contains unique identifiers, its size is vastly smaller than $S$.
3. **Filtering (Semi-Join):** Node 1 filters $R$ based on $S'$, producing $R' = R \ltimes S$.
4. **Result:** Node 1 sends $R'$ to the Coordinator.
- **Bytes Transferred:** Size($S'$) + Size($R'$)
- **Advantage:** By trading a small amount of local processing (projection and deduplication) at Node 2, we avoid shipping the bulky unneeded columns of $S$.

## 4. Cost Model Analysis
In distributed environments, the total cost $Total\_Cost$ is a linear combination of I/O, CPU, and Communication costs:
$$ Total\_Cost = (C_{cpu} \times \#inst) + (C_{io} \times \#ios) + (C_{msg} \times \#msgs) + (C_{tr} \times \#bytes) $$

Since the datasets reside in memory (ignoring $C_{io}$) and the number of messages ($C_{msg}$) is small and constant for both approaches, the dominant factor becomes $C_{tr} \times \#bytes$.

**Theoretical Evaluation:**
Let $Card(S) = 50,000$ and $Card(S') = 7,985$. Let the size of a single `Assignment` tuple be 80 bytes and a single `EmpID` be 10 bytes.
- Standard Join Payload from S: $50,000 \times 80 = 4,000,000$ bytes.
- Semi-Join Payload from S: $7,985 \times 10 \approx 79,850$ bytes.

This massive reduction in bytes transferred results in a **Size Reduction Factor of ~77%** for the overall query, directly validating Özsu's assertion that Semi-Joins are highly effective for reducing communication overhead in Distributed Databases.

## 5. Failure Handling (Reliability)
To satisfy the grading criteria, our Coordinator implements a basic timeout mechanism. In a distributed transaction, if a participant site fails (e.g., Node 2 goes offline), the Coordinator detects the unreachable endpoint via a `ConnectionError` and safely aborts the transaction rather than hanging indefinitely. This demonstrates foundational fault tolerance.

# Cloud Service Placement Optimization Project  

## Introduction  

This project aims to model and optimize **cloud service placement** across a set of heterogeneous regions, machines and infrastructures, while respecting a set of **availability, security, performance and geographical compliance constraints**.  

The goal is to assign, for each service, a **machine type** and a **deployment region** so as to **minimize overall cost** while guaranteeing an **acceptable level of compliance and performance**.  

The project simulates the behavior of cloud platforms (e.g., AWS, Azure, GCP) and implements several optimization approaches to compare their performance.  

---

## Problem type

The cloud service placement problem belongs to the family of **combinatorial optimization problems**.  

More precisely, it is a **multi-dimensional assignment problem with multiple constraints**, close to an **NP-hard problem**.  

### Justification:
- Each service must be assigned to **a machine and a region** among a finite set → combinatorial.  
- Capacity, security and latency constraints make finding a solution **non-trivial**.  
- The evaluation function includes several sometimes conflicting components (cost ↔ performance ↔ compliance).  
- Exact solutions (linear programming or MILP) become unusable for medium instances → **resort to heuristics and metaheuristics**.  

---

## Educational and technical objectives  

- Build a **consistent data model** (services, regions, flows, machines, constraints).  
- Define an **evaluation function** (costs, SLA, security, compliance).  
- Generate **realistic random instances** of deployments.  
- Implement and compare several **optimization algorithms**. 
- Measure the **performance and convergence** of each method.  
- Perform **unit tests** to validate critical functions.  

---

## Project architecture  

```
project_root/
│
├── algorithms/
│   ├── greedy.py
│   ├── simulated_annealing.py
│   ├── genetic.py
│
├── utils/
│   ├── data_model.py
│   ├── evaluate.py
│   ├── generate_instances.py
│   ├── print_solution.py
│   ├── random_solution_generator.py
│   ├── run_experiment.py
│   ├── visualization.py
│
├── tests/
│   ├── test_data_model.py
│   ├── test_evaluate.py
│   ├── test_generate_instances.py
│   ├── test_greedy.py
│   ├── test_simulated_annealing.py
│   ├── test_genetic.py
│
├── instances/
├── main.py
├── requirements.txt
├── README.md
└── .gitignore
```

---

## Installation  

### 1️ Clone the project  

```bash
git clone https://github.com/oumaima-benha/cloud-optimization
cd cloud-optimization
```

### 2️ Create a virtual environment  

```bash
python -m venv venv
source venv/bin/activate  # on Linux/Mac
venv\Scripts\activate     # on Windows
```

### 3️ Install dependencies  

```bash
pip install -r requirements.txt
```

---

## Phase 1 – Modeling  

Before coding, a **manual mathematical modeling** of the problem was performed to clarify variables, constraints and cost functions.
The goal of this modeling was to provide a clear and rigorous basis before developing solution algorithms.  

The core of the project relies on a clear data model defined in `data_model.py`.

### 🧩 Main entities:

| Entity | Description |
|--------|--------------|
| **Service** | Deployment unit with CPU, memory, storage, SLA, security zone. |
| **MachineType** | Available machine (small, medium, large). |
| **Region** | Geographical location (r1, r2, etc.). |
| **Flow** | Network flow between two services (bandwidth, latency, encryption). |
| **Instance** | Container grouping all services, machines, regions and flows (a problem to solve). |
| **Placement** | Deployment solution (service → machine, region, redundancy, encryption). |

---

## Phase 2 – Evaluation function  

The function `evaluate(instance, placement)` computes the **total cost of a solution** by summing several sub-costs:

| Component | Function | Constraint type | Description |
|------------|-----------|--------------------|--------------|
| Machine cost | `cost_machine()` | Hard | Machine unavailable or redundancy not supported |
| Storage cost | `cost_storage()` | Soft | Penalty if service not placed |
| Network | `cost_network()` | Hard | If network link impossible (math.inf), function stops. |
| Security | `cost_security_violation()` | Hard/Soft | If communication forbidden otherwise penalized (soft) |
| Encryption | `cost_encryption_violation()` | Soft | If encryption missing when required → penalty |
| Performance | `cost_network_performance_violation()` | Soft | If max latency exceeded → penalty (latency > limit), but not infeasible |
| SLA | `cost_availability()` | Hard/Soft | If SLA impossible (math.inf) → hard ; otherwise progressive cost according to SLA |
| Capacity | `cost_capacity_violation()` | Hard/Soft | If critical overflow → math.inf, otherwise moderate penalty. |
| Cybersecurity | `cost_cybersecurity()` | Soft | Overall risk score |
| Geography | `cost_geography_violation()` | Hard/Soft | If region forbidden → math.inf ; otherwise penalty for non-compliance (GDPR, sovereignty) |

Any “hard” constraint leads to `math.inf` → infeasible solution.

---

## Phase 3 – Python project structure  

Each module has a single responsibility:
- `data_model.py` : data structures
- `evaluate.py` : global evaluation function
- `generate_instances.py` : random instance generation
- `print_solution.py` : formatted placement display
- `run_experiment.py` : run an algorithm and measure its cost
- `visualization.py` : charts and comparisons

---

## Phase 4 – Data generation  

The script `generate_instances.py` creates **realistic and random instances**:
- services with random CPU/Mem requirements,  
- regions with variable latencies and costs,  
- inter-service flows with bandwidth and security requirements,  
- instances stored as `.json` in the `instances/` folder.

Example:
```python
instance = generate_instance(nb_services=5, nb_regions=3, nb_machines=2)
```

---

## Phase 5 – Optimization algorithms  
### 1️ Greedy Algorithm

#### Rationale
Greedy was chosen as a **simple and fast initial approach**.  
It provides a reasonable baseline and helps verify model consistency.  
Although it can get stuck in a local minimum, it often gives a correct solution in minimal time.

#### Description and pseudo-code

```text
Input : instance (services, machines, regions, flows, rules...), evaluate(instance, placement)
Output : placement_greedy

Algorithm GreedyPlacement :
  placement <- empty placement
  encryption defaults <- {}
  order_services <- list of services sorted by decreasing importance (e.g.: cpu descending)

  For each service s in order_services :
    best_cost <- +∞
    best_assignment <- None

    For each machine_type m in instance.machines :
      For each region r in s.allowed_regions :
        # attempt: place s on (m,r)
        placement_temp <- deep copy of placement
        placement_temp.placement[s] <- (m, r)
        placement_temp.redundancy[s] <- 1  # by default (could try >1)
        # update encryption of flows involving s: if needed use f.encryption_required
        for each flow f involving s :
          if f.src or f.dst already placed in placement_temp :
            placement_temp.encryption[(f.src,f.dst)] <- f.encryption_required

        (cost, details) <- evaluate(instance, placement_temp)

        If cost < best_cost :
          best_cost <- cost
          best_assignment <- (m, r)

    If best_assignment is not None and best_cost < +∞ :
      place s in placement using best_assignment
    Else :
      leave s unplaced (or mark as impossible)

  Return placement
```

Complexity: **O(n × m × r x e)**  
(n = services, m = machines, r = regions, e = complexity of evaluate call)

If e ~ O(n + f), we get: **O(n × m × r x (n + f))** 

---

### 2️ Simulated Annealing

#### Rationale
Simulated annealing was chosen because it allows exploration of the search space **beyond local minima**, by introducing a notion of **temperature** that gradually decreases.  
It is particularly suited to combinatorial problems with several soft constraints.

#### Description and pseudo-code

```text
Input : instance, evaluate, placement_initial (optional)
Parameters : T0 (initial temperature), Tmin (final temperature), alpha (cooling factor),
             iter_per_T (iterations per temperature level), max_eval (optional)

If placement_initial is None :
  placement_current <- random solution or greedy(instance)
Else :
  placement_current <- placement_initial

cost_current <- evaluate(instance, placement_current)

placement_best <- copy(placement_current)
cost_best <- cost_current

T <- T0
while T > Tmin and number_of_evaluations < max_eval :
  for i in 1..iter_per_T :
    neighbor <- generate_neighbor(placement_current, instance)
      # neighbor = move a service to another (machine, region)
      # or toggle encryption for a flow, or change redundancy
    cost_neighbor <- evaluate(instance, neighbor)

    delta = cost_neighbor - cost_current

    if cost_neighbor < cost_current :
      # always accept improvement
      placement_current <- neighbor
      cost_current <- cost_neighbor
      if cost_neighbor < cost_best :
        placement_best <- copy(neighbor)
        cost_best <- cost_neighbor
    else :
      # accept with probability exp(-delta / T)
      prob = exp(-delta / T)
      if random() < prob :
        placement_current <- neighbor
        cost_current <- cost_neighbor

  T <- T * alpha  # cooling

Return placement_best
```

Complexity: **O(k × n)**  
(k = number of iterations, n = services)

---

### 3️ Genetic Algorithm

#### Rationale
Genetic algorithms allow **global exploration** of the solution space through combination (crossover) and mutation of multiple individuals.  
They are effective for large-scale, multi-criteria problems.

#### Description and pseudo-code

```text
Input : instance, evaluate
Parameters : pop_size, generations, elite_count, mutation_rate

Function GeneticAlgorithm(instance):
  # 1. Initialization : create a population of random individuals (placements)
  population <- [random_individual(instance) for i in 1..pop_size]
  evaluate each individual -> fitness = cost (lower = better)

  For g from 1 to generations :
    # 2. Selection : keep the best (elitism) + select parents for reproduction
    sort population by increasing fitness
    new_population <- best elite_count individuals (elite)

    # 3. Reproduction : produce children until pop_size
    while len(new_population) < pop_size :
      parent1 <- selection(parent pool)   # e.g.: tournament
      parent2 <- selection(parent pool)
      child <- crossover(parent1, parent2)
      mutate(child) with probability mutation_rate
      add child to new_population

    population <- new_population
    evaluate population (fitness)
    update global best if improved

  Return best individual (placement) and its cost
```

Complexity: **O(pop × gen × e)**  
(pop = population size, gen = number of generations, e = evaluate)

---

## Phase 6 – Comparison and visualization  

###  Objective  
Compare the performance of algorithms on the same instance:  
- final cost,  
- execution time,  

### 📁 `utils/run_experiment.py`
Runs an algorithm, measures time and returns a uniform results dictionary.  

### 📁 `utils/visualization.py`
- `plot_comparison_cout(df)` → comparative barplot of costs.  
- `plot_comparison_temps(df)` → comparative barplot of execution times. 

---

## Phase 7 – Unit tests  

Tests are in `tests/` and verify:
- data structures (`test_data_model.py`),
- cost consistency (`test_evaluate.py`),
- instance generation (`test_generate_instances.py`),
- solution validity (`test_greedy.py`, `test_simulated_annealing.py`, `test_genetic.py`).

Run:
```bash
python -m pytest -v
```

Example output:
```
collected 7 items

tests/test_data_model.py::test_service_creation PASSED                     [ 14%]
tests/test_data_model.py::test_instance_structure PASSED                   [ 28%]
tests/test_evaluate.py::test_evaluate_simple_case PASSED                   [ 42%]
tests/test_generate_instances.py::test_generate_instance_structure PASSED  [ 57%]
tests/test_genetic.py::test_genetic_algorithm_valid_result PASSED          [ 71%]
tests/test_greedy.py::test_greedy_valid_solution PASSED                    [ 85%]
tests/test_simulated_annealing.py::test_simulated_annealing_runs PASSED    [100%]

=================================== 7 passed in 0.16s ===================================
```

---

## Phase 8 – Results and comparison

## 📈 Experimental results 
For an instance: nb_services=300, nb_regions=140, nb_machines=150

| Algorithm | Total cost | Time (s) |
|-------------|-------------|-----------|
| Random baseline | 284491.504587 | 0.000 |
| Greedy | 263399.268650 | 57.816 |
| Simulated Annealing | 129678.486697 | 60.909 |
| Genetic Algorithm | 205734.048572 | 1.342 |


![Cost comparison](/results/Figure_1_nb_services=300_nb_regions=140_nb_machines=150.png)
![Execution time comparison](/results/Figure_2_nb_services=300_nb_regions=140_nb_machines=150.png)

---
And for an instance: nb_services=500, nb_regions=120, nb_machines=200

| Algorithm | Total cost | Time (s) |
|-------------|-------------|-----------|
| Random baseline | 464363.203794 | 0.001 |
| Greedy | 432593.335044 | 145.671 |
| Simulated Annealing | 269491.114653 | 167.845 |
| Genetic Algorithm | 371297.544809 | 2.599 |

![Cost comparison](/results/Figure_1_nb_services=500_nb_regions=120_nb_machines=200.png)
![Execution time comparison](/results/Figure_2_nb_services=500_nb_regions=120_nb_machines=200.png)
---
## 📈 Analysis of results
The first essential remark is that the “black box” functions used for cost calculation must be replaced with their real implementations to obtain a more realistic estimate of partial costs and the total cost. Indeed, in the current version, these functions are only placeholders allowing the algorithms to run and be tested, which does not provide exact cost values.

Therefore, the results presented only provide an approximate picture of what one might obtain, without faithfully reflecting the real differences between the costs produced by each algorithm’s solutions.

Nevertheless, the results show a clear improvement in total cost with stochastic methods.

## Execution time analysis
Regarding execution time, we can observe that the Greedy and Simulated Annealing algorithms require longer computation times, around 2 to 3 minutes for processing 500 to 1000 services to assign.
In contrast, the Genetic Algorithm is significantly faster, with an execution time of only 2 to 3 seconds, while producing cost results close to those obtained by Simulated Annealing.

This performance difference can be explained by each method’s algorithmic complexity. Simulated Annealing relies on an iterative local search process requiring many successive solution evaluations, while the Genetic Algorithm exploits recombination of solutions within a population, which allows efficient exploration of the search space while limiting the total number of iterations. As for the Greedy method, although simple in principle, it can become costly when it must evaluate multiple possible choices at each step for large problem instances.

---

## Phase 9 – Sensitivity analysis of parameters

## Simulated Annealing

### **Figure 1 – Heatmap: Influence of T₀ and α on average cost**
![Simulated Annealing Heatmap](/results/Figure_1.png)
The first figure illustrates the variation of the average cost obtained as a function of the **initial temperature (T₀)** and the **cooling factor (α)**.  
We observe that:
- A **too low initial temperature (T₀ = 500)** often yields high costs: the algorithm explores the search space less and risks getting stuck in a local minimum.  
- An **intermediate or high value of T₀ (1000–2000)** combined with a **factor α ≈ 0.85–0.9** provides the **best cost/time trade-offs**.  
- Values of α that are too low (0.8) cool the system too quickly, limiting exploration and degrading solution quality.

✅ **Conclusion :**
Simulated annealing is sensitive to the pair *(T₀, α)*.  
A good balance between exploration and exploitation typically lies around:
```
T₀ ≈ 1000 – 2000
α ≈ 0.85 – 0.9
```
These parameters allow smoother convergence and minimal average cost.

---

### **Figure 2 – Evolution of average cost as a function of T₀**
![Average cost vs T₀](/results/Figure_2.png)

This curve confirms the previous trend:  
the average cost decreases markedly when T₀ increases from 500 to 1000, then stabilizes beyond 1000.  
This reflects an **initial improvement thanks to wider exploration**, followed by **diminishing returns** when the temperature becomes too high.

---

## Genetic Algorithm

### **Figure 3 – Heatmap: Influence of population size and mutation rate**
![GA Heatmap](/results/Figure_1_GA.png)
The heatmap highlights two observations:
- A **larger population (pop_size 20–30)** tends to improve result quality (lower cost), because it increases genetic diversity.  
- A **moderate mutation rate (0.1)** often yields the best results:  
  - Too low (0.05) → risk of premature stagnation,  
  - Too high (0.2) → too much perturbation, loss of convergence.  

✅ **Conclusion :**
Best trade-offs are reached for:
```
pop_size ≈ 20–30
mutation_rate ≈ 0.1
```
The model is thus more stable with moderate genetic diversity and a balanced mutation rate.

---

### **Figure 4 – Evolution of average cost according to population size**
![Average cost vs population size](/results/Figure_2_GA.png)

This curve illustrates a **decreasing trend of average cost** as population increases.  
This confirms that **more diversity in the initial population improves the average quality of solutions**, although computation time increases slightly.

---

## 🧩 Overall interpretation

| Algorithm | Key parameters | Main observation | Optimal zone |
|-------------|----------------|------------------------|----------------|
| Simulated Annealing | T₀, α | Too low → local minimum ; too high → slow convergence | T₀ = 1000–2000 ; α = 0.85–0.9 |
| Genetic | pop_size, mutation_rate | Too low → stagnation ; too high → instability | pop_size = 20–30 ; mutation_rate = 0.1 |

---

## 💬 General conclusion
- **Simulated Annealing** offers stable and fast convergence, but depends heavily on thermal calibration.  
- The **Genetic Algorithm** is more robust to parameter variations, but requires a sufficient population to ensure diversity.  
- In both cases, sensitivity is moderate but significant: poor tuning can multiply the final cost by 1.3 to 1.5.  
These results show that an **automatic tuning phase** could further improve the overall performance of the system.
---
## ⚠️ Limits and perspectives  

Several improvements are possible:  

The first identified perspective and limitation is to replace the “black box” functions used for cost calculation with their real implementations in order to obtain a more realistic estimate of partial costs and the total cost. Indeed, in this version, these functions are only placeholders used to run and test the algorithms, which does not provide exact cost values.
### 🔹 On the model
- Integrate **dynamic** costs depending on real traffic.  
- Add **energy and carbon footprint** constraints.  
- Introduce **service migration** (dynamic placement over time).  

### 🔹 On the algorithms
- Combine Greedy + Simulated Annealing in a **hybrid algorithm**.  
- Test other metaheuristics: **Tabu Search, Ant Colony, Particle Swarm Optimization**.  
- Add a **parallelization** module for cost evaluations.  


These perspectives open the way to a more robust, intelligent and realistic optimization system for cloud placement management.

---

## How to run the project  

```bash
python main.py
```

✅ This script :
1. Generates a random instance,  
2. Runs the 4 algorithms,  
3. Compares costs and times,  
4. Displays placements and charts.  

---

## Tools and dependencies  

| Tool | Use |
|-------|--------------|
| Python 3.10+ | Main language |
| Pandas, Numpy | Analysis and results comparison |
| Matplotlib, Seaborn | Visualizations |
| Pytest | Unit tests |
| GitHub | Versioning and documentation |

---

## Author & credits  

**Project carried out by:** *Oumaima Ben*  
As part of a cloud optimization and modeling project.

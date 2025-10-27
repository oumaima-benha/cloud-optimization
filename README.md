#  Cloud Placement Optimizer

##  Description
Projet d’optimisation du **placement de services cloud** dans différentes régions et machines,
en prenant en compte :
- les coûts de machines, de stockage et de réseau,
- la latence, la redondance et le chiffrement,
- les contraintes géographiques, de capacité et de disponibilité (SLA).

Ce projet s’appuie sur un modèle de données générique (`Instance`, `Service`, `MachineType`, etc.)
et une fonction d’évaluation flexible (`evaluate`) qui combine plusieurs fonctions de coût ("boîtes noires").

---

## 📂 Structure du projet

cloud_optimization/
│
├── data_model.py
├── evaluate.py
├── generate_instances.py
├── main.py
│
├── algorithms/
│   ├── 
│   ├──
│
├── instances/
│   ├── small_example.json
│   ├── medium.json
│
├── notebooks/
│   ├── exploration.ipynb
│   ├── analysis.ipynb
│
├── tests/
│   ├── 
│
├── requirements.txt
└── README.md
---

##  Installation

### Cloner le dépôt
```bash
git clone https://github.com/<ton_nom>/cloud-placement-project.git
cd cloud-placement-project

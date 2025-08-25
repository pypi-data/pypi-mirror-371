# MOHAF: Multi-Objective Hierarchical Auction Framework

## Overview
This repository provides the implementation and supporting materials for the paper:

"MOHAF: A Multi-Objective Hierarchical Auction Framework for Scalable and Fair Resource Allocation in IoT Ecosystems"

MOHAF is a distributed resource allocation mechanism for heterogeneous IoT environments.  
It combines hierarchical clustering, submodular optimization, and dynamic pricing to achieve:

- Efficient allocation of resources in large-scale IoT ecosystems  
- Joint optimization of cost, energy efficiency, quality of service (QoS), and fairness  
- Theoretical guarantees with a (1 - 1/e) approximation ratio  
- Perfect fairness across participants (Jain’s Index = 1.000 in experiments)  

We provide code, experimental setup, and references to enable reproducibility and extension of this work.

---
## Repository Contents

```
MOHAF-Resource-Allocation
├─ .gitignore
├─ LICENSE
├─ MOHAF.ipynb
├─ README.md
├─ docs
│  ├─ index.md
│  ├─ mohaf_paper.pdf
│  └─ usage.md
├─ examples
│  ├─ analyze_results.ipynb
│  └─ run_experiments.py
├─ mohaf
│  ├─ __init__.py
│  ├─ auction_mechanisms.py
│  ├─ core.py
│  ├─ scenarios.py
│  └─ utils.py
├─ pyproject.toml
├─ requirements.txt
└─ tests
   ├─ __init__.py
   ├─ test_auction_mechanisms.py
   └─ test_core.py
```
---

## Installation

You can install MOHAF directly from PyPI:

```bash
pip install mohaf
```

## Usage

After installation, you can import MOHAF in your Python scripts:

```python
from mohaf.auction_mechanisms import MOHAFAuction
from mohaf.scenarios import generate_synthetic_scenario

# 1. Initialize the auction mechanism
mohaf_auction = MOHAFAuction(alpha=0.3, beta=0.3, gamma=0.2, delta=0.2)

# 2. Generate a synthetic scenario
resources, requests = generate_synthetic_scenario(n_resources=50, n_requests=30)

# 3. Run the auction
results = mohaf_auction.run_auction(resources, requests)
metrics = mohaf_auction.calculate_metrics(results)

print("Auction completed!")
print(f"  Allocation Efficiency: {metrics['allocation_efficiency']:.3f}")
print(f"  Revenue: ${metrics['revenue']:.2f}")
```

For more detailed examples and to reproduce the experiments from the paper, please see the `examples/` directory and the `MOHAF.ipynb` notebook in the repository.  

---

## Dataset
Experiments rely on the publicly available Google Cluster Data: https://github.com/google/cluster-data  

---

## License
This project is licensed under the MIT License.  

---

## Citation
If you use this repository, please cite the associated paper:

```
@misc{Agrawal2025,
  author       = {Agrawal, Kushagra and Goktas, Polat and Bandopadhyay, Anjan, and Ghosh, Debolina and Jena, Junali Jasmine and Gourisaria, Mahendra Kumar},
  title        = {MOHAF: A Multi-Objective Hierarchical Auction Framework for Scalable and Fair Resource Allocation in IoT Ecosystems},
  year         = {2025},
  eprint       = {2508.14830},
  archivePrefix= {arXiv},
  primaryClass = {cs.DC},
  doi          = {10.48550/arXiv.2508.14830},
  url          = {https://arxiv.org/abs/2508.14830}
}
```

---

📌 Repository link: https://github.com/afrilab/MOHAF-Resource-Allocation/tree/main

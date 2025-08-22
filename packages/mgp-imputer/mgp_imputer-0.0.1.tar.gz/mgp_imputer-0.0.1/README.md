# MGP-Imputer: Missing Value Imputation with Deep Gaussian Processes

[![PyPI version](https://badge.fury.io/py/mgp-imputer.svg)](https://badge.fury.io/py/mgp-imputer)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A PyTorch-based implementation of Missing Gaussian Processes (MGP) for missing value imputation, wrapped in a user-friendly `scikit-learn` compatible API.

This package allows you to seamlessly integrate Deep Gaussian Process models into your data preprocessing pipelines for robust and uncertainty-aware imputation. It is based on the paper ["Gaussian processes for missing value imputation"](https://www.sciencedirect.com/science/article/pii/S0950705123003532).

## Features

- **Scikit-learn Compatible:** Use `fit`, `predict`, and `fit_transform` methods just like any other scikit-learn transformer.
- **Two Imputation Strategies:**
    - `chained` (Default): Builds a separate GP layer for each feature with missing values, modeling dependencies in a chained fashion (MGP).
    - `holistic`: Builds a single, multi-output Deep GP to model all features simultaneously.
- **Probabilistic Imputation:** Returns both the imputed values and the standard deviation, giving you a measure of uncertainty for each imputed value.
- **GPU Accelerated:** Leverages PyTorch to run on CUDA devices for significant speedups.

## Installation

You can install `mgp-imputer` directly from PyPI:

```bash
pip install mgp-imputer
```



## **Quick Start**
Here's how to use `MGPImputer` to fill in missing values (`np.nan`) in your dataset.
```bash
import numpy as np
import pandas as pd
from mgp import MGPImputer

# 1. Create a synthetic dataset with 20% missing values
np.random.seed(42)
n_samples, n_features = 200, 5
X_true = np.random.rand(n_samples, n_features) * 10
X_missing = X_true.copy()
missing_mask = np.random.rand(n_samples, n_features) < 0.2
X_missing[missing_mask] = np.nan

print(f"Created a dataset with {np.sum(missing_mask)} missing values.")

# 2. Initialize the MGPImputer
# Strategies can be 'chained' (default) or 'holistic'
imputer = MGPImputer(
    imputation_strategy='chained',
    n_inducing_points=1000,
    n_iterations=1000, # Use more iterations for real data
    learning_rate=0.01,
    batch_size=64,
    verbose=True,
    seed=42
)

# 3. Fit on the data and transform it to get imputed values
# The imputer returns the imputed data and the standard deviation of the predictions
X_imputed, X_std = imputer.fit_transform(X_missing)

# 4. Evaluate the imputation quality
rmse = np.sqrt(np.mean((X_imputed[missing_mask] - X_true[missing_mask])**2))
print(f"\nImputation complete.")
print(f"RMSE on missing values: {rmse:.4f}")

# The result is a complete numpy array
print("\nImputed data shape:", X_imputed.shape)
print("Number of NaNs in imputed data:", np.isnan(X_imputed).sum())
```


## **Citation**
If you use this work in your research, please cite the original paper:

Jafrasteh, B., Hernández-Lobato, D., Lubián-López, S. P., & Benavente-Fernández, I. (2023). Gaussian processes for missing value imputation. Knowledge-Based Systems, 273, 110603.
[Missing GPs](https://www.sciencedirect.com/science/article/pii/S0950705123003532)



## Getting Started

### Prerequisites

Install the dependencies using the following command:

```bash
pip install -r requirements.txt
```






### Using the code

Put your data in "datasets" folder and run your experiments using the following command with optional arguments.

```
python run_experiment.py -h
  -h, --help            show this help message and exit
  --dataset_name DATASET_NAME
                        name of the data set (should have subfolders with the
                        name s0, s1, s2, etc.) (default: None)
  --scaling SCALING     scaling method [MeanStd|MinMax|MaxAbs|Robust|None]
                        (default: MeanStd)
  --split_number split_number
                        data set split number [0|1|2|etc] (default: 0)
  --name svgp           svgp
  --nGPU NGPU           GPU number (for cpu use -1) [-1|0|1|2] (default: -1)
  --minibatch_size BATCHSIZE
                        Batch size (default: 100) (default: 100)
  --M NIP             number of inducing points (default: 100) (default:
                        1024)
  --M2 NIP2             number of inducing points (default: 100) (default:
                        1024)
  --imputation mean     mean|median|knn|mice|None
  
  --kernel              Matern|RBF (defaults:matern)
  
  --likelihood_var      variance noise gaussian likelihood (0.01)
  
  --lrate               learning rate (0.01)
  
  --missing             consider missing (should be on for MGP, otherwise return normal SVGP)
  
  --nGPU                GPU number
  
  --n_epoch             number of training epochs
  
  --n_samples           number of MC samples
  
  --nolayers            number of layers
  
  --numThreads          number of threads
  
  --var_noise           variance noise
  
  --consider_miss       consider missing for DGP and VSGP

```

You can run experiments using UCI data set with the above options.
To replicate results from the paper:
```bash
python run_experiment.py --dataset_name parkinson_10 --lrate 0.01 --split_number 0 --name svgp --n_samples 20 --M 100 --M2 100 --no_iterations 10000 --nolayers 1 --nGPU 0 --minibatch_size 100 --fitting --imputation mean --missing
```

## Cite
Jafrasteh, B., Hernández-Lobato, D., Lubián-López, S. P., & Benavente-Fernández, I. (2023). Gaussian processes for missing value imputation. Knowledge-Based Systems, 273, 110603.
[Missing GPs](https://www.sciencedirect.com/science/article/pii/S0950705123003532)

## License

This project is licensed under the MIT License.


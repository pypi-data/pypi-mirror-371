# ml_model_handler

A lightweight Python package for training, managing, and predicting with multiple machine learning models.  
Supports classical ML algorithms, pipelines, ensemble learning (Voting), and user-defined custom estimators.  

---

## Features
- Preconfigured ML models: Logistic Regression, KNN, Naive Bayes, Decision Tree, Random Forest, Gradient Boosting, XGBoost, SVM, SGD.  
- Voting Classifier support (soft/hard voting).  
- Plug-and-play with **custom estimators**.  
- Built-in pipelines with `StandardScaler` where useful.  
- Easy single prediction and batch predictions.  
- Probability predictions (`predict_proba`) when available.  

---

## Installation
```
pip install ml-model-handler
```

---

## Quick Start

```python
import pandas as pd
from ml_model_handler import MLModelHandler

# Example dataset
X = pd.DataFrame({
    "feature1": [1, 2, 3, 4],
    "feature2": [10, 20, 30, 40]
})
y = [0, 1, 0, 1]

# Initialize handler
model_handler = MLModelHandler()

# Train default models
model_handler.train_models(X, y)

# Single prediction
print(model_handler.predict("logistic", [5, 50]))

# Batch prediction
batch_features = [
    [6, 60],
    [7, 70]
]
model_handler.batch_predict("knn", batch_features)

# Probability prediction
print(model_handler.predict_proba("logistic", [5, 50]))
```

---

## Voting Classifier

The `voting` estimator combines predictions from multiple trained models (soft or hard voting).

```python
# Use Logistic, KNN and Voting
model_handler.train_models(X, y, estimators=["logistic", "knn"], voting_type="soft")

print(model_handler.predict("voting", [7, 70]))
```

⚠️ If fewer than 2 base models are given with `voting`, it falls back to all trained models with a warning.

---

## Custom Estimators

You can extend with your own models:

```python
from sklearn.linear_model import RidgeClassifier

custom = {
    "ridge": RidgeClassifier()
}

model_handler.train_models(X, y, estimators=["ridge"])
print(model_handler.predict("ridge", [8, 80]))
```

---

## Project Structure
```
ml_model_handler/
 ├── __init__.py
 └── main.py          # MLModelHandler class
README.md
setup.py
```

---

## Contributing
Contributions are welcome!  
- Fork the repo  
- Create a feature branch  
- Submit a pull request

---

## License
[MIT License](https://github.com/Rucha-Ambaliya/ml_model_handler/blob/main/LICENSE)
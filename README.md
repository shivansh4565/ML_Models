# Titanic Survival Prediction using Logistic Regression

## Overview

This project builds a Machine Learning model to predict whether a passenger survived the Titanic disaster using Logistic Regression. The workflow includes data preprocessing, feature encoding, train-test splitting, model training, and performance evaluation using Scikit-Learn.

## Dataset

The project uses the Titanic dataset, which contains passenger information such as age, gender, passenger class, fare, and survival status.

**Target Variable:** `Survived`

* 0 = Did Not Survive
* 1 = Survived

## Technologies Used

* Python
* Pandas
* NumPy
* Scikit-Learn

## Project Workflow

1. Load and explore the dataset
2. Handle missing values
3. Encode categorical features
4. Split data into training and testing sets
5. Train a Logistic Regression model
6. Make predictions on test data
7. Evaluate model performance

## Evaluation Metrics

The model is evaluated using:

* Accuracy Score
* Confusion Matrix
* Classification Report

  * Precision
  * Recall
  * F1-Score

## Results

The Logistic Regression model achieves strong classification performance on the Titanic dataset and demonstrates the complete machine learning pipeline from preprocessing to evaluation.

## Project Structure

titanic-survival-prediction-logistic-regression/

├── data/

│   └── Titanic-Dataset.csv

├── src/

│   └── train.py

├── requirements.txt

├── README.md

└── .gitignore

## Installation

```bash
git clone (https://github.com/shivansh4565/ML_Models)

cd 

pip install -r requirements.txt
```

## Run the Project

```bash
cd src
python train.py
```

## Key Learning Outcomes

* Data preprocessing techniques
* Handling missing values
* Feature encoding
* Logistic Regression implementation
* Model evaluation and interpretation
* Machine Learning workflow using Scikit-Learn

## Future Improvements

* Hyperparameter tuning using GridSearchCV
* Feature engineering for improved accuracy
* Cross-validation implementation
* Model deployment using Flask or Streamlit
* Comparison with Random Forest and XGBoost models
* Interactive dashboard for predictions

## Author

Shivansh

If you found this project useful, consider giving it a ⭐ on GitHub.

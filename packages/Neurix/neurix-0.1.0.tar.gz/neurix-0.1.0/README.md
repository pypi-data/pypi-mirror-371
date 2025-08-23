# NEURIX

![MyPackage Logo](logo/Neurix.png)



Neurix is a custom-built Python machine learning library. It contains modules for classification, regression, data preprocessing, statistical relationships, and evaluation metrics.

---

##  Directory Structure

```
├── Classification
│   ├── LogisticRegression.py
│   └── __init__.py
├── preprocessing
│   ├── MasAbsScaler.py
│   ├── MeanScaler.py
│   ├── MinMaxScaler.py
│   ├── SimpleImputer.py
│   ├── StandardScaler.py
│   └── __init__.py
├── Regression
│   ├── GDRidgeRegression.py
│   ├── LinearRegression.py
│   ├── OLSRidgeRegression.py
│   └── __init__.py
├── relation
│   ├── covariance.py
│   ├── Pearson_corr.py
│   └── __init__.py
├── score
│   ├── score.py
│   └── __init__.py
└── __init__.py
```

---

#  Modules Overview

## Classification

A custom implementation of **multiclass logistic regression using softmax**. Supports early stopping and one-hot encoding internally.

---

## Class: `LogisticRegression`

### **Constructor**

```python
LogisticRegression(epochs=1000, learning_rate=0.1, patience=20, min_del=1e-4)
```

#### Parameters:
- `epochs` *(int)*: Number of iterations for training.
- `learning_rate` *(float)*: Step size for weight updates.
- `patience` *(int)*: Number of epochs to wait for improvement before early stopping.
- `min_del` *(float)*: Minimum decrease in loss to be considered an improvement.

---

##  Methods

### 🔹 `fit(X, y)`
Fits the logistic regression model to the training data.

#### Parameters:
- `X` *(numpy.ndarray)*: Feature matrix of shape `(m, n)` where `m` is the number of samples and `n` is the number of features.
- `y` *(numpy.ndarray)*: Target vector of shape `(m,)` containing class labels.

---

### 🔹 `predict(X)`
Predicts class labels for given input data.

#### Parameters:
- `X` *(numpy.ndarray)*: Feature matrix of shape `(m, n)`.

#### Returns:
- `numpy.ndarray`: Predicted class labels of shape `(m,)`.

---

### 🔹 `predict_prob(X)`
Returns the class probabilities (softmax scores) for each sample.

#### Parameters:
- `X` *(numpy.ndarray)*: Feature matrix.

#### Returns:
- `numpy.ndarray`: Probability matrix of shape `(m, k)`, where `k` is the number of classes.

---

## ⚙️ Internal Methods 

### 🔸 `softmax(z)`
Applies the softmax activation function.

### 🔸 `one_hot(y)`
Converts labels to one-hot encoded format.

### 🔸 `compute_loss(y_true, y_pred)`
Computes the cross-entropy loss.

---

##  Early Stopping
Stops training if the loss does not improve by `min_del` for `patience` consecutive epochs.

---

## 📌 Example

```python
from Neurix.Classification import LogisticRegression
import numpy as np

# Sample data
X = np.random.rand(100, 4)
y = np.random.randint(0, 3, size=(100,))

model = LogisticRegression(epochs=500, learning_rate=0.05)
model.fit(X, y)

predictions = model.predict(X)
probs = model.predict_prob(X)
```

---



# Regression

# LinearRegression

A custom implementation of **simple linear regression** using the **closed-form (Normal Equation)** solution. This class supports fitting and predicting with NumPy arrays.

---

## Class: `LinearRegression`

### **Constructor**

```python
LinearRegression()
```

Creates an instance of the linear regression model. No parameters are required during initialization.

---

## Methods

### 🔹 `fit(X_train, y_train)`
Fits the linear regression model using the closed-form solution.


#### Parameters:
- `X_train` *(numpy.ndarray)*: Training data of shape `(m, n)` where `m` is the number of samples and `n` is the number of features.
- `y_train` *(numpy.ndarray)*: Target values of shape `(m,)`.

---

### 🔹 `predict(X_test)`
Predicts continuous target values for the input features.



#### Parameters:
- `X_test` *(numpy.ndarray)*: Feature matrix of shape `(m, n)`.

#### Returns:
- `numpy.ndarray`: Predicted values of shape `(m,)`.

---

## ⚙️ Attributes

- `coef` *(numpy.ndarray)*: Coefficients of the trained linear model, shape `(n,)`.
- `intercept` *(float)*: Intercept term (bias).

---

## 📌 Example

```python
from Neurix.Regression import LinearRegression
import numpy as np

# Example dataset
X = np.array([[1], [2], [3], [4]])
y = np.array([2.5, 4.9, 7.4, 9.8])

# Model training
model = LinearRegression()
model.fit(X, y)

# Predictions
X_test = np.array([[5], [6]])
preds = model.predict(X_test)
print(preds)
```

---
# GDRidge

A custom implementation of **Ridge Regression** using **Gradient Descent**. This model is used for linear regression with L2 regularization to prevent overfitting.

---

## Class: `GDRidge`

### **Constructor**

```python
GDRidge(epochs, learning_rate, alpha)
```
#### Parameters:

- `epochs` (int): Number of iterations to run gradient descent.

- `learning_rate` (float): Step size for updating weights.

- `alpha` (float): Regularization strength (L2 penalty).

## Methods
### 🔹 `fit(X_train, y_train)`

Trains the ridge regression model using gradient descent.


#### Parameters:

- `X_train` (ndarray): Training features of shape (m, n) where m = number of samples, n = number of features.

- `y_train` (ndarray): Target values of shape (m,).

---

### 🔹`predict(X_test)`
Predicts target values using the trained model.

### Parameters:

- `X_test` (ndarray): Test features of shape (m, n).

Returns:

- `ndarray`: Predicted target values of shape (m,).

---
### Attributes:

- `coef` (ndarray): Weights learned for each feature. Shape: (n,)

- `intercept` (float): Bias term of the model.

```python 
from GDRidgeRegression import GDRidge
import numpy as np

# Example dataset
X = np.array([[1], [2], [3]])
y = np.array([2, 4, 6])

# Create and train model
model = GDRidge(epochs=1000, learning_rate=0.01, alpha=0.1)
model.fit(X, y)

# Predict on new data
X_test = np.array([[4], [5]])
predictions = model.predict(X_test)
print(predictions)
```

# OLSRidge

A custom implementation of **Ridge Regression using the Closed-Form (Normal Equation)** solution. This model includes **L2 regularization** and solves the optimization problem analytically.

---

##  Class: `OLSRidge`

### **Constructor**

```python
OLSRidge(alpha=0.1)
```

### Parameters:

- `alpha` (float): L2 regularization strength. Defaults to 0.1.

## Methods:
### 🔹 `fit(X_train, y_train)`



### Parameters:

- `X_train` (ndarray): Training data of shape (m, n) — m samples, n features.

- `y_train` (ndarray): Target values of shape (m,).

### 🔹 `predict(X_test)`

Predicts continuous values for the test data using the learned weights.

### Parameters:

- `X_test` (ndarray): Input features of shape (m, n).

Returns:

- `ndarray`: Predicted values of shape (m,).

### Attributes

- `coef` (ndarray): Weights for each feature (shape (n,)).

- `intercept` (float): Bias term of the model.

```python
from Neurix.Regression import OLSRidge
import numpy as np

# Sample training data
X = np.array([[1], [2], [3]])
y = np.array([3, 6, 9])

# Train the model
model = OLSRidge(alpha=0.1)
model.fit(X, y)

# Make predictions
X_test = np.array([[4], [5]])
predictions = model.predict(X_test)
print(predictions)
```

---

# Preprocessing
## SimpleImputer

A custom implementation of a simple data imputer for handling **missing values (NaNs)** in numeric arrays. Supports replacing missing values using **mean**, **median**, **mode**, or a specific constant.

---

## Class: `SimpleImputer`

### **Constructor**

```python
SimpleImputer(fill_value='mean')
```
### Parameters:

- `fill_value` (str or float or int): Strategy to fill missing values.

### Supported options:

- `'mean'`: Replace missing values with the mean.

- `'median'`: Replace with the median.

- `'mode'`: Replace with the most frequent value.

- `numeric`: Replace with a constant numeric value.

## Methods
- `fill(X)`

Fills missing values in the input array using the specified strategy.

## Parameters:

- `X` (array-like): Input 1D array or list with possible np.nan values.

## Returns:

- `ndarray`: A NumPy array with all missing values filled.

## Raises:

- ValueError: If fill_value is not one of 'mean', 'median', 'mode', or a number.

```python
from Neurix.preprocessing import SimpleImputer
import numpy as np

X = [1, 2, np.nan, 4, np.nan, 5]

# Using mean
imputer = SimpleImputer(fill_value='mean')
filled = imputer.fill(X)
print("Mean-filled:", filled)

# Using mode
imputer = SimpleImputer(fill_value='mode')
filled = imputer.fill(X)
print("Mode-filled:", filled)

# Using a constant value
imputer = SimpleImputer(fill_value=0)
filled = imputer.fill(X)
print("Constant-filled:", filled)
```

## Notes

- Input array is internally converted to NumPy with dtype=float to handle np.nan.

- Only supports 1D arrays or lists.

- Does not support categorical/factor variables.

---

## StandardScaler

A custom implementation of the **StandardScaler**, which standardizes features by removing the mean and scaling to unit variance.

---

## Class: `StandardScaler`

### **Constructor**

```python
StandardScaler()
```
Initializes the scaler. No parameters are required.
---
## Methods:
## 🔹 `fit(X_train)`

Computes the mean and standard deviation for each feature from the training data.

## Parameters:

- `X_train` (ndarray): Training data of shape (m, n).

Returns:

self: Returns the scaler instance itself.

## 🔹 `fit_transform(X_train)`

Fits to the data and then transforms it.

### Parameters:

- `X_train` (ndarray): Training data of shape (m, n).

Returns:

- ndarray: Standardized training data of shape (m, n).

## 🔹 `transform(X_test)`

Standardizes new data using the previously computed mean and standard deviation.

### Parameters:

- `X_test` (ndarray): Data to transform, shape (m, n).

Returns:

- `ndarray`: Transformed data of shape (m, n).

### Attributes

- `mean` (ndarray): Mean of each feature in the training data.

- `std` (ndarray): Standard deviation of each feature in the training data. Zero std values are replaced with 1 to avoid division by zero.


```python
from Neurix.preprocessing import StandardScaler
import numpy as np

X_train = np.array([[1, 2], [3, 4], [5, 6]])
X_test = np.array([[7, 8]])

scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

print("Train scaled:\n", X_train_scaled)
print("Test scaled:\n", X_test_scaled)
```
## Notes

- This scaler is safe against zero standard deviation (division by 0) — such values are treated as 1.

- Assumes input is numeric and NumPy-compatible.
---


# MinMaxScaler

A custom implementation of the **Min-Max Scaler** that rescales features to a specified range `[min, max]`. Default range is `[0, 1]`.

---

##  Class: `MinMaxScaler`

### **Constructor**

```python
MinMaxScaler(min=0, max=1)
```
## Parameters:

- `min` (float): Minimum value of the transformed data. Default is 0.

- `max` (float): Maximum value of the transformed data. Default is 1.

Raises Exception: If min > max.

## Methods
## 🔹 `fit(x)`

Computes the min_val and max_val for each feature from the training data.

### Parameters:

- `x` (ndarray): Training data of shape (m, n).

Returns:

- self: The fitted scaler instance.

## 🔹 `fit_transform(x)`

Fits the scaler to the training data, then transforms it.

### Parameters:

- `x` (ndarray): Training data of shape (m, n).

Returns:

- `ndarray`: Scaled data of shape (m, n).

## 🔹 `transform(x)`

Transforms new data using the previously computed min_val and max_val.

### Parameters:

- `x` (ndarray): Data to transform, shape (m, n).

Returns:

- `ndarray`: Scaled data of shape (m, n).

## Attributes

- `min_val` (ndarray): Minimum value of each feature in the training data.

- `max_val` (ndarray): Maximum value of each feature in the training data.

- `scale_` (ndarray): Feature-wise scaling factors. If a feature has zero range, it is scaled by 1.


```python
from Neurix.preprocessing import MinMaxScaler
import numpy as np

X_train = np.array([[1, 2], [3, 4], [5, 6]])
X_test = np.array([[7, 8]])

scaler = MinMaxScaler(min=0, max=1)
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

print("Train scaled:\n", X_train_scaled)
print("Test scaled:\n", X_test_scaled)
```
## Notes

- The scaler handles zero-range features by replacing zero denominators with 1.

- Assumes input is numeric and compatible with NumPy operations.



# MeanScaler

A simple custom scaler that centers data by subtracting the **mean** of each feature. This transformation results in **zero-mean features**, but does **not scale the variance**.

---

## Class: `MeanScaler`

### **Constructor**

```python
MeanScaler()
```
Initializes the scaler. No parameters are required.

## Methods
## 🔹 `fit(X_train)`

Computes the mean of each feature from the training data.

### Parameters:

- `X_train` (ndarray): Training data of shape (m, n).

### Returns:

self: The fitted scaler instance.

## 🔹 `fit_transform(X_train)`

Fits the scaler to the training data, then transforms it.

### Parameters:

- `X_train` (ndarray): Training data of shape (m, n).

### Returns:

- `ndarray`: Centered data of shape (m, n).

## 🔹 `transform(X_test)`

Centers new data using the previously computed mean.

### Parameters:

- `X_test` (ndarray): Test data to transform, shape (m, n).

### Returns:

- `ndarray`: Centered data of shape (m, n).

## Attribute:

- `mean` (ndarray): Mean of each feature in the training data.

```python
from Nuerix.preprocessing import MeanScaler
import numpy as np

X_train = np.array([[1, 2], [3, 4], [5, 6]])
X_test = np.array([[7, 8]])

scaler = MeanScaler()
X_train_centered = scaler.fit_transform(X_train)
X_test_centered = scaler.transform(X_test)

print("Train centered:\n", X_train_centered)
print("Test centered:\n", X_test_centered)

```

## Notes:

- This scaler only performs mean centering; it does not scale variance.

- Assumes input is numeric and NumPy-compatible.
---

# MaxAbsScaler

A custom implementation of the **Max Absolute Scaler**, which scales each feature by its **maximum absolute value**, transforming data to the range `[-1, 1]`. It is especially useful for sparse data and when preserving the sign of the data is important.

---

## Class: `MaxAbsScaler`

### **Constructor**

```python
MaxAbsScaler()
```
Initializes the scaler. No parameters are required.

## Methods
## 🔹 `fit(x)`

Computes the maximum absolute value for each feature in the training data.

### Parameters:

- `x` (ndarray): Training data of shape (m, n).

### Returns:

- self: The fitted scaler instance.

## 🔹 `fit_transform(x)`

Fits the scaler to the training data, then transforms it.

### Parameters:

- `x` (ndarray): Training data of shape (m, n).

### Returns:

- `ndarray`: Scaled data of shape (m, n).

## 🔹 `transform(x)`

Transforms the input data using the previously computed maximum absolute values.

### Parameters:

- `x` (ndarray): Data to transform, shape (m, n).

### Returns:

- `ndarray`: Scaled data of shape (m, n).

## Attributes

- `Absmax` (ndarray): Maximum absolute value for each feature.

- `scale_` (ndarray): Scaling factors for each feature. Features with 0 max absolute value are scaled using 1 to avoid division by zero.

```python
from Neurix.preprocessing import MaxAbsScaler
import numpy as np

X_train = np.array([[1, -2], [-3, 4], [5, -6]])
X_test = np.array([[7, -8]])

scaler = MaxAbsScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

print("Train scaled:\n", X_train_scaled)
print("Test scaled:\n", X_test_scaled)

```

## Notes:

- This scaler does not center the data (mean remains unchanged).

- Useful when you want to scale data between -1 and 1 while preserving sparsity.

- Automatically handles zero-valued features.

---

# relation

# covariance

A simple implementation of the **covariance** calculation between two numerical features. Covariance measures the degree to which two variables vary together.

---

## Class: `covariance`

### **Constructor**

```python
covariance()
```
Initializes the object and internal variables for computing covariance.

## Methods
## 🔹 `cov(x, y)`

Computes the sample covariance between two 1D arrays.

### Parameters:

- `x` (ndarray): 1D NumPy array of shape (n,).

- `y` (ndarray): 1D NumPy array of shape (n,).

### Returns:

- float: Covariance between x and y.

Raises Exception: If the input arrays x and y do not have the same length.

## Attributes

- `x_mean` (float): Mean of array x.

- `y_mean` (float): Mean of array y.

- `feat_len` (int): Number of samples in the input arrays.



```python
from Neurix.relation import covariance
import numpy as np

x = np.array([1, 2, 3, 4])
y = np.array([5, 6, 7, 8])

cov_calc = covariance()
result = cov_calc.cov(x, y)

print("Covariance:", result)
```
## Notes

- This implementation uses the sample covariance formula (denominator is n - 1).

- Assumes both x and y are numeric and 1D.

- Does not support missing values (NaN).

---

# Pearson_corr

A custom implementation of the **Pearson Correlation Coefficient**, which measures the **linear relationship** between two variables. Values range from `-1` (perfect negative correlation) to `+1` (perfect positive correlation).

---

## Class: `Pearson_corr`

### **Constructor**

```python
Pearson_corr()
```
Initializes internal variables required for computing correlation.

## Methods
## 🔹 `corr(x, y)`

Computes the Pearson correlation coefficient between two 1D arrays.

### Parameters:

- `x` (ndarray): 1D NumPy array of shape (n,).

- `y` (ndarray): 1D NumPy array of shape (n,).

### Returns:

- float: Pearson correlation coefficient between x and y.

Raises Exception: If the lengths of x and y do not match.

## Attributes

- `x_mean` (float): Mean of input array x.

- `y_mean` (float): Mean of input array y.

- `x_std` (float): Sample standard deviation of x.

- `y_std` (float): Sample standard deviation of y.

- `feat_len` (int): Number of elements in input arrays.

```python
from relation.Pearson_corr import Pearson_corr
import numpy as np

x = np.array([10, 20, 30, 40])
y = np.array([15, 25, 35, 45])

corr_calc = Pearson_corr()
result = corr_calc.corr(x, y)

print("Pearson Correlation Coefficient:", result)
```
## Notes:

- Uses sample standard deviation (ddof=1) in the denominator.

- Assumes both inputs are numeric, 1D arrays of equal length.

- Pearson correlation is undefined if either standard deviation is zero.

---


# score

A custom class to compute multiple **regression evaluation metrics** such as R², Adjusted R², MSE, RMSE, and MAE.

---

## Class: `score`

### **Constructor**

```python
score(y_test, y_pred)
```
Initializes the score object with actual and predicted values.

## Parameters:

- `y_test` (ndarray): Actual target values of shape (n,).

- `y_pred` (ndarray): Predicted values of shape (n,).

Raises ValueError: If y_test and y_pred have different lengths.

## Methods:
## 🔹 `r2_score()`

Computes the coefficient of determination \( R^2 \).

### Returns:

- `float`: R² score (between 0 and 1).

Raises ValueError: If the total variance is zero (undefined R²).

## 🔹 `adjusted_r2_score(n_features_in)`

Computes the Adjusted R² score, which adjusts R² for the number of features.

### Parameters:

- `n_features_in` (int): Number of input features used during prediction.

### Returns:

- float: Adjusted R² score.

## 🔹 `mse()`

Computes the Mean Squared Error.

### Returns:

- float: MSE value.

## 🔹 `rmse()`

Computes the Root Mean Squared Error.

### Returns:

- float: RMSE value.

## 🔹 `mae()`

Computes the Mean Absolute Error.

### Returns:

- float: MAE value.


```python
from Neurix.score import score
import numpy as np

y_test = np.array([3.0, -0.5, 2.0, 7.0])
y_pred = np.array([2.5, 0.0, 2.0, 8.0])

sc = score(y_test, y_pred)

print("R² Score:", sc.r2_score())
print("Adjusted R² Score:", sc.adjusted_r2_score(n_features_in=1))
print("MSE:", sc.mse())
print("RMSE:", sc.rmse())
print("MAE:", sc.mae())

```





---

## 📦 Installation

```bash
pip install Neurix
```

---



---

## 👨‍💻 Author

Avatanshu Gupta  
- GitHub- https://github.com/AvatanshuGupta
- LinkedIn- https://www.linkedin.com/in/avatanshu-gupta-073699310/
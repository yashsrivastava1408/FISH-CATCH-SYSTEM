import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score
import pickle

# Load the historical fish catch data
data = pd.read_csv('catch_data.csv')

# Handle missing values (Optional, depending on your dataset)
# For this example, we'll drop rows with missing values
data = data.dropna()

# Feature Engineering (convert date to day of year)
data['date'] = pd.to_datetime(data['date'])
data['day_of_year'] = data['date'].dt.dayofyear

# Select features and target variable
X = data[['day_of_year']]  # Feature (Day of the year)
y = data['quantity']       # Target (Fish catch quantity)

# Split the data into training and test sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train a simple linear regression model
model = LinearRegression()
model.fit(X_train, y_train)

# Evaluate the model only if there are enough test samples
if len(y_test) > 1:
    # Predict the values for the test set
    y_pred = model.predict(X_test)
    
    # Calculate the Mean Squared Error
    mse = mean_squared_error(y_test, y_pred)
    print(f'Mean Squared Error: {mse}')

    # Calculate R-squared only if we have enough data
    r2 = r2_score(y_test, y_pred)
    print(f'R-squared: {r2}')
else:
    print("Test set is too small to evaluate the model properly.")

# Save the trained model
with open('model.pkl', 'wb') as f:
    pickle.dump(model, f)

print("Model trained and saved as 'model.pkl'")

# Load the model for future predictions (Optional)
with open('model.pkl', 'rb') as f:
    loaded_model = pickle.load(f)

# Example usage of the loaded model to make predictions
new_data = pd.DataFrame({'day_of_year': [150]})  # Example input for day of the year
prediction = loaded_model.predict(new_data)

print(f'Predicted fish catch for day 150: {prediction[0]}')

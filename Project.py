import pandas as pd
import pickle
from datetime import datetime
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report

df = pd.read_csv("Youtube_Data.csv", encoding='latin1')

df['post_date'] = pd.to_datetime(df['post_date'],
 format='%d-%b-%y', errors='coerce')

current_date = pd.to_datetime(datetime.now().date())  # Use the current date
df['video_age'] = (current_date - df['post_date']).dt.days

df.dropna(subset=['video_age', 'video_title_length', 'views', 'likes', 'Viral'], inplace=True)

print(df.head())
print(df.shape)
print(df.isnull().sum())
print(df.columns)

features = ['video_title_length', 'views', 'likes', 'video_age']
target = 'Viral'

X = df[features]
y = df[target] 

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

y_pred = model.predict(X_test)

accuracy = accuracy_score(y_test, y_pred)
report = classification_report(y_test, y_pred)

print(f'Accuracy: {accuracy:.2f}')
print('Classification Report:')
print(report)

with open('random_forest_model.pkl', 'wb') as file:
    pickle.dump(model, file)
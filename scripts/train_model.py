import pandas as pd
from sklearn.ensemble import RandomForestClassifier
import pickle

df = pd.read_csv("data.csv")
df['Target'] = df['Close'].shift(-1) > df['Close']
df = df.dropna()

features = ['Open', 'High', 'Low', 'Close', 'Volume']
X = df[features]
y = df['Target'].astype(int)

model = RandomForestClassifier()
model.fit(X, y)

pickle.dump(model, open("../backend/model.pkl", "wb"))
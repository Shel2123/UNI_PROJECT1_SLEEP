import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
from dotenv import dotenv_values
import joblib

class ModelTrainer:
    def __init__(self, csv_path: str, model_path: str):
        self.csv_path: str = csv_path
        self.model_path: str = model_path
        self.model = None
        self.data = None
        self.X = None
        self.y = None
        self.categorical_cols = ["Gender", "Occupation"]
        self.numeric_cols = ["Age", "Sleep Duration", "Quality of Sleep", "Physical activity level"]

    def load_data(self):
        self.data = pd.read_csv(self.csv_path)
        print(f"Data loaded from {self.csv_path}")

    def preprocess_data(self):
        target = "Stress Level"
        self.X = self.data.drop(columns=[target])
        self.y = self.data[target]
        print("Data is ready.")

    def build_pipeline(self):
        categorical_transformer = OneHotEncoder(handle_unknown="ignore")

        preprocessor = ColumnTransformer(
            transformers=[
                ("cat", categorical_transformer, self.categorical_cols)
            ],
            remainder="passthrough"
        )

        self.model = Pipeline([
            ("preprocessing", preprocessor),
            ("regressor", RandomForestRegressor(n_estimators=100, random_state=42))
        ])
        print("Pipeline created.")

    def train_model(self):
        X_train, X_test, y_train, y_test = train_test_split(
            self.X, self.y, test_size=0.2, random_state=42
        )
        self.model.fit(X_train, y_train)
        print("Model learned.")

    def evaluate_model(self):
        X_train, X_test, y_train, y_test = train_test_split(
            self.X, self.y, test_size=0.2, random_state=42
        )
        score = self.model.score(X_test, y_test)
        print(f"Model accuracy: {score:.2f}")

    def save_model(self):
        joblib.dump(self.model, self.model_path)
        print(f"Model saved in {self.model_path}")

    def run(self):
        self.load_data()
        self.preprocess_data()
        self.build_pipeline()
        self.train_model()
        self.evaluate_model()
        self.save_model()

if __name__ == "__main__":
    CSV_PATH = dotenv_values('.env')['PATH']
    MODEL_PATH = dotenv_values('.env')['MODEL_PATH']

    trainer = ModelTrainer(CSV_PATH, MODEL_PATH)
    trainer.run()

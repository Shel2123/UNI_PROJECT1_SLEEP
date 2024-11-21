import pandas as pd


PATH = "data/Sleep_health_and_lifestyle_dataset.csv"

columns_to_remove = ["BMI Category", "Blood Pressure", "Heart Rate", "Daily Steps", "Sleep Disorder"]
df = pd.read_csv(PATH)
df = df.drop(columns=columns_to_remove, errors='ignore')
df.to_csv(PATH, index=False)

import pandas as pd
df = pd.read_excel("salary_data.xlsx")
df.to_csv("salary_data.csv", index=False)

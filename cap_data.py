"""Shrink + clean the huge CSV: drop ultra-rare diseases, then cap to 20k rows."""
import pandas as pd
from sklearn.model_selection import train_test_split

PATH = 'disease_data.csv'
MIN_COUNT = 10     # keep only diseases with at least 10 records
MAX_ROWS = 20000

df = pd.read_csv(PATH)
label = next(c for c in df.columns if 'disease' in c.lower())
print(f'Original: {len(df)} rows | {df.shape[1]-1} symptoms | {df[label].nunique()} diseases')

counts = df[label].value_counts()
keep = counts[counts >= MIN_COUNT].index
df = df[df[label].isin(keep)]
print(f'After dropping diseases with <{MIN_COUNT} records: '
      f'{len(df)} rows | {df[label].nunique()} diseases')

if len(df) > MAX_ROWS:
    small, _ = train_test_split(df, train_size=MAX_ROWS, random_state=42,
                                stratify=df[label])
    df = small

df.to_csv(PATH, index=False)
print(f'✅ Saved → {PATH}: {len(df)} rows | {df[label].nunique()} diseases')
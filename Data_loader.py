import pandas as pd
from sqlalchemy import create_engine
import os

# Create data folder if not exists
os.makedirs('data', exist_ok=True)

# Sheet names
sheets = ['ANTI', 'CATO', 'CHOH', 'GWMP', 'HAFE',
          'MANA', 'MONO', 'NACE', 'PRWI', 'ROCR', 'WOTR']

# Load Forest data
print("Loading Forest data...")
forest_dfs = []
for sheet in sheets:
    try:
        df = pd.read_excel('data/Bird_Monitoring_Data_FOREST.XLSX', 
                           sheet_name=sheet)
        forest_dfs.append(df)
        print(f"  Loaded sheet: {sheet}")
    except:
        print(f"  Skipped sheet: {sheet}")

forest_data = pd.concat(forest_dfs, ignore_index=True)
print(f"Forest rows: {len(forest_data)}")

# Load Grassland data
print("\nLoading Grassland data...")
grassland_dfs = []
for sheet in sheets:
    try:
        df = pd.read_excel('data/Bird_Monitoring_Data_GRASSLAND.XLSX', 
                           sheet_name=sheet)
        grassland_dfs.append(df)
        print(f"  Loaded sheet: {sheet}")
    except:
        print(f"  Skipped sheet: {sheet}")

grassland_data = pd.concat(grassland_dfs, ignore_index=True)
print(f"Grassland rows: {len(grassland_data)}")

# Fix missing columns
if 'Site_Name' not in grassland_data.columns:
    grassland_data['Site_Name'] = 'N/A'
if 'Previously_Obs' not in forest_data.columns:
    forest_data['Previously_Obs'] = None

# Combine both
combined = pd.concat([forest_data, grassland_data], ignore_index=True)
print(f"\nTotal combined rows: {len(combined)}")

# Clean Date column
combined['Date'] = pd.to_datetime(combined['Date'], errors='coerce')
combined['Month'] = combined['Date'].dt.month
combined['Year'] = combined['Date'].dt.year
combined['Season'] = combined['Month'].apply(
    lambda m: 'Spring' if m in [3,4,5] else
              'Summer' if m in [6,7,8] else
              'Autumn' if m in [9,10,11] else 'Winter')

# Fill missing values
combined['Sex'] = combined['Sex'].fillna('Unknown')
combined['Disturbance'] = combined['Disturbance'].fillna('Unknown')
combined['Common_Name'] = combined['Common_Name'].fillna('Unknown')
combined['Temperature'] = pd.to_numeric(
    combined['Temperature'], errors='coerce')
combined['Temperature'] = combined['Temperature'].fillna(
    combined['Temperature'].median())
combined['Humidity'] = pd.to_numeric(
    combined['Humidity'], errors='coerce')
combined['Humidity'] = combined['Humidity'].fillna(
    combined['Humidity'].median())

# Save to SQL database
engine = create_engine('sqlite:///data/bird_data.db')
combined.to_sql('bird_observations', con=engine, 
                if_exists='replace', index=False)
print("\nDatabase created successfully at data/bird_data.db!")

# Verify
test = pd.read_sql("SELECT COUNT(*) as total FROM bird_observations", 
                   con=engine)
print("Total records in database:", test['total'][0])
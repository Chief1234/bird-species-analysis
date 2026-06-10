# 🐦 Bird Species Observation Analysis

Analysis of bird species observations across Forest and Grassland habitats
in 11 National Park units.

## 📊 Key Findings
- **17,077** total observations
- **108** Forest species | **107** Grassland species
- **ANTI** has highest bird activity (3,921 observations)
- **Summer** is peak season (67.2% of sightings)
- **8 at-risk species** identified on PIF Watchlist
- **Singing** is the most common identification method (57.7%)

## 🛠️ Tech Stack
- Python, Pandas, SQLAlchemy
- Streamlit, Plotly
- SQLite Database
- Jupyter Notebook

## 🚀 How to Run
1. Clone the repo
2. Create virtual environment: `python -m venv venv`
3. Activate: `venv\Scripts\activate`
4. Install libraries: `pip install -r requirements.txt`
5. Add Excel files to `data/` folder
6. Run: `python Data_loader.py`
7. Launch dashboard: `streamlit run app.py`

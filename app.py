import dash
import dash_bootstrap_components as dbc
import pandas as pd
from layout import layout
from callbacks import register_callbacks

# Initialize Dash app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server  # Needed for deployment

# Load data
df = pd.read_csv("salary_data.csv")

# Rename columns to English-friendly names
df.rename(columns={
    "Befattning": "Job Title",
    "Arbetsplats": "Department",
    "Antal hela \u00e5r med arbete i klinisk verksamhet": "ExperienceYears",
    "M\u00e5nadsl\u00f6n totalt": "Månadslön totalt"
}, inplace=True)

# Assign layout to app
app.layout = layout

# Register callbacks (pass the app and df)
register_callbacks(app, df)

if __name__ == "__main__":
    app.run_server(debug=True)

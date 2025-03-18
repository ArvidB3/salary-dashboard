import dash
import dash_bootstrap_components as dbc
import pandas as pd
from layout import layout
from callbacks import register_callbacks
import dash_core_components as dcc

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

# Fill NaN values with "Not Specified"
df["Job Title"] = df["Job Title"].fillna("Not Specified")
df["Department"] = df["Department"].fillna("Not Specified")
df["Specialist eller ST-fysiker"] = df["Specialist eller ST-fysiker"].fillna("Not Specified")

# Get all unique values before Dash initializes
all_jobs = sorted(df["Job Title"].unique().tolist())
all_depts = sorted(df["Department"].unique().tolist())
all_specialists = ["Specialist", "ST-fysiker", "Nej"]

# Inject these predefined checklists into `layout`
layout["job-title-filter"] = dcc.Checklist(
    id="job-title-filter",
    options=[{"label": job, "value": job} for job in all_jobs],
    value=all_jobs,  # Default: All selected
    style={"display": "flex", "flexDirection": "column"}
)

layout["department-filter"] = dcc.Checklist(
    id="department-filter",
    options=[{"label": dept, "value": dept} for dept in all_depts],
    value=all_depts,  # Default: All selected
    style={"display": "flex", "flexDirection": "column"}
)

layout["specialist-filter"] = dcc.Checklist(
    id="specialist-filter",
    options=[{"label": spec, "value": spec} for spec in all_specialists],
    value=all_specialists,  # Default: All selected
    style={"display": "flex", "flexDirection": "column"}
)

# Assign layout to app
app.layout = layout

# Register callbacks (pass the app and df)
register_callbacks(app, df)

if __name__ == "__main__":
    app.run_server(debug=True)
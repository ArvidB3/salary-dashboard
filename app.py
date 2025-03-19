import dash
import dash_bootstrap_components as dbc
import pandas as pd
import os
from layout import layout
from callbacks import register_callbacks, update_filter_options
from dash import dcc
from cache_config import cache, init_cache


# Initialize Dash app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server  # Needed for deployment
init_cache(app)

# Load data
local_path = "salary_data.csv"

if os.path.exists(local_path):
    df = pd.read_csv(local_path)
else:
    print("❌ ERROR: CSV file not found in either location.")
    df = None  # Handle the case where the dataframe is empty

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
df["Specialist eller ST-fysiker"] = df["Specialist eller ST-fysiker"].fillna("Nej")

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


# **Manually trigger the callback to get initial options & values**
initial_options = update_filter_options(None, all_jobs, all_depts, all_specialists, [0, 50], df)  # Simulate first callback call

# Inject checklists into layout dynamically
layout["job-title-filter"] = dcc.Checklist(id="job-title-filter", options=initial_options[0], value=initial_options[1])
layout["department-filter"] = dcc.Checklist(id="department-filter", options=initial_options[2], value=initial_options[3])
layout["specialist-filter"] = dcc.Checklist(id="specialist-filter", options=initial_options[4], value=initial_options[5])


# Assign layout to app
app.layout = layout

# Register callbacks (pass the app and df)
register_callbacks(app, df)


if __name__ == "__main__":
    IS_AZURE = "WEBSITE_HOSTNAME" in os.environ
    app.run_server(
        host="0.0.0.0" if IS_AZURE else "127.0.0.1", 
        port=8000 if IS_AZURE else 8050, 
        debug=not IS_AZURE  # Enables auto-reloading locally, but not in Azure
    )
import dash_bootstrap_components as dbc
from dash import dcc, html

layout = dbc.Container(fluid=True, style={"height": "100vh"}, children=[
    html.H1("Salary Dashboard", className="text-center my-3"),
    
    # Filters (Always Visible)
    dbc.Row([
        dbc.Col([
            html.Label("Color By:"),
            dcc.Dropdown(
                id="color-by-dropdown",
                options=[
                    {"label": "Job Title", "value": "Job Title"},
                    {"label": "Specialist Type", "value": "Specialist eller ST-fysiker"},
                    {"label": "Department", "value": "Department"}
                ],
                value="Job Title",  # Default color by Job Title
                clearable=False
            )
        ], width=2),
        dbc.Col([
            html.Label("Job Title:"),
            dcc.Checklist(
                id="job-title-filter",
                options=[],  # Will be set dynamically
                value=[],  # Default: All checked (set dynamically)
                style={"display": "flex", "flexDirection": "column"}
            )
        ], width=4),
        dbc.Col([
            html.Label("Department:"),
            dcc.Checklist(
                id="department-filter",
                options=[],  # Will be set dynamically
                value=[],  # Default: All checked (set dynamically)
                style={"display": "flex", "flexDirection": "column"}
            )
        ], width=4),
        dbc.Col([
            html.Label("Specialist:"),
            dcc.Checklist(
                id="specialist-filter",
                options=[],  # Will be set dynamically
                value=[],  # Default: All checked (set dynamically)
                style={"display": "flex", "flexDirection": "column"}
            )
        ], width=4),
        dbc.Col([
            html.Label("Years of Experience:"),
            dcc.RangeSlider(id="exp-slider", min=0, max=50, step=1, value=[0, 50],
                            marks={i: str(i) for i in range(0, 51, 5)})  # Marks every 5 years
        ], width=3)
    ], className="mb-4"),

    # Tabs for switching views
    dcc.Tabs(id="tabs", value="scatterplot2", children=[
        dcc.Tab(label="Salary Distribution", value="histogram"),
        dcc.Tab(label="Salary vs Experience", value="scatterplot"),
        dcc.Tab(label="Salary vs Experience 2", value="scatterplot2"),  # New tab
    ]),

    # Graph container
    html.Div(id="tab-content", style={"flex": "1", "height": "80vh"})
])

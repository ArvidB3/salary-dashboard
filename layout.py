import dash_bootstrap_components as dbc
from dash import dcc, html

layout = dbc.Container(fluid=True, style={"height": "100vh"}, children=[
    html.H1("Salary Dashboard", className="text-center my-3"),
    
    # Filters (Always Visible)
    dbc.Row([
        dbc.Col([
            html.Label("Job Title:"),
            dcc.Dropdown(id="job-dropdown", clearable=True, placeholder="Select job title")
        ], width=4),
        dbc.Col([
            html.Label("Department:"),
            dcc.Dropdown(id="dept-dropdown", clearable=True, placeholder="Select department")
        ], width=4),
        dbc.Col([
            html.Label("Years of Experience:"),
            dcc.RangeSlider(id="exp-slider")
        ], width=4)
    ], className="mb-4"),

    # Tabs for multiple views
    dcc.Tabs(id="tabs", value="histogram", children=[
        dcc.Tab(label="Salary Distribution", value="histogram"),
        dcc.Tab(label="Salary vs Experience", value="scatterplot")
    ]),
    
    # Default Tab Content (Must Be Initialized)
    html.Div(id="tab-content", children=dcc.Graph(id="salary-histogram"))
])

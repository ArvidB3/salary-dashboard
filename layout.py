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
            dcc.RangeSlider(id="exp-slider", min=0, max=50, step=1, value=[0, 50],  # Default range
                            marks={i: str(i) for i in range(0, 51, 5)})  # Show marks every 5 years
        ], width=4)
    ], className="mb-4"),

    # Tabs for switching views
    dcc.Tabs(id="tabs", value="histogram", children=[
        dcc.Tab(label="Salary Distribution", value="histogram"),
        dcc.Tab(label="Salary vs Experience", value="scatterplot")
    ]),

    # Graph container
    html.Div(id="tab-content", style={"flex": "1", "height": "80vh"})  # Ensure the graph takes full height
])

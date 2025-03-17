from dash import Input, Output, dcc
import plotly.express as px

def register_callbacks(app, df):
    @app.callback(
        Output("tab-content", "children"),  # Output is the Div holding the graph
        [Input("tabs", "value"),           # Active tab selection
         Input("job-dropdown", "value"),   # Selected job title
         Input("dept-dropdown", "value"),  # Selected department
         Input("exp-slider", "value")]     # Selected experience range
    )
    def update_graph(selected_tab, selected_job, selected_dept, exp_range):
        # Filter data
        dff = df.copy()
        if selected_job:
            dff = dff[dff["Job Title"] == selected_job]
        if selected_dept:
            dff = dff[dff["Department"] == selected_dept]
        if exp_range:
            dff = dff[(dff["ExperienceYears"] >= exp_range[0]) & (dff["ExperienceYears"] <= exp_range[1])]

        # Generate the correct graph based on the selected tab
        if selected_tab == "histogram":
            fig = px.histogram(dff, x="Månadslön totalt", nbins=20, title="Salary Distribution",
                               labels={"Månadslön totalt": "Total Monthly Salary"},
                               marginal="box", opacity=0.7)
            fig.update_layout(bargap=0.1)

        elif selected_tab == "scatterplot":
            fig = px.scatter(dff, x="ExperienceYears", y="Månadslön totalt",
                             title="Salary vs Experience",
                             labels={"ExperienceYears": "Years of Experience", "Månadslön totalt": "Total Monthly Salary"},
                             color="Job Title",  # Different colors per Job Title
                             hover_data=["Department"],
                             trendline="ols")  # Adds trendline
        
        fig.update_layout(
            autosize=True,
            height=None,  # Let it scale automatically
            width=None,
            margin=dict(l=20, r=20, t=50, b=50)  # Adjust margins to prevent cutoff
        )
        # fig.update_layout(
        #     height=1200,  # Adjust height in pixels
        #     width=2000   # Adjust width in pixels
        # )

        
        return dcc.Graph(figure=fig, style={"width": "100%", "height": "80vh"})   # Returns the graph inside the div

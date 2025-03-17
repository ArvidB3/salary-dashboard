from dash import Input, Output, State, dcc
import plotly.express as px

def register_callbacks(app, df):
    @app.callback(
        Output("job-dropdown", "options"),
        Output("dept-dropdown", "options"),
        Input("job-dropdown", "value"),
        Input("dept-dropdown", "value"),
        Input("exp-slider", "value")
    )
    def update_dropdown_options(selected_job, selected_dept, exp_range):
        # Make a copy of the dataset
        dff = df.copy()

        # Replace NaN values with "Not Specified"
        dff["Job Title"] = dff["Job Title"].fillna("Not Specified")
        dff["Department"] = dff["Department"].fillna("Not Specified")

        # Apply filters, but exclude the current dropdown's category
        filtered_dff = df.copy()
        if selected_dept:
            filtered_dff = filtered_dff[filtered_dff["Department"] == selected_dept]
        if exp_range:
            filtered_dff = filtered_dff[(filtered_dff["ExperienceYears"] >= exp_range[0]) & (filtered_dff["ExperienceYears"] <= exp_range[1])]

        filtered_job_counts = filtered_dff["Job Title"].value_counts().to_dict()

        filtered_dff = df.copy()  # Reset before applying the job title filter
        if selected_job:
            filtered_dff = filtered_dff[filtered_dff["Job Title"] == selected_job]
        if exp_range:
            filtered_dff = filtered_dff[(filtered_dff["ExperienceYears"] >= exp_range[0]) & (filtered_dff["ExperienceYears"] <= exp_range[1])]

        filtered_dept_counts = filtered_dff["Department"].value_counts().to_dict()

        # Get all job titles and departments (without filtering them out)
        all_jobs = sorted(df["Job Title"].fillna("Not Specified").unique())
        all_depts = sorted(df["Department"].fillna("Not Specified").unique())

        # Create dropdown options with counts based on **filtered** results
        job_options = [{"label": f"{job} ({filtered_job_counts.get(job, 0)})", "value": job} for job in all_jobs]
        dept_options = [{"label": f"{dept} ({filtered_dept_counts.get(dept, 0)})", "value": dept} for dept in all_depts]

        return job_options, dept_options


    # Update graph based on filters and active tab
    @app.callback(
        Output("tab-content", "children"),
        [Input("tabs", "value"),
         Input("job-dropdown", "value"),
         Input("dept-dropdown", "value"),
         Input("exp-slider", "value")]
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

        return dcc.Graph(figure=fig, style={"width": "100%", "height": "100%"})

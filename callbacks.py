import html
from dash import Input, Output, State, dcc, html
import pandas as pd
import plotly.express as px

def register_callbacks(app, df):
    @app.callback(
        Output("job-dropdown", "options"),
        Output("dept-dropdown", "options"),
        Output("specialist-filter", "options"),
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

        # Apply filters (excluding the dropdown being updated)
        filtered_dff = df.copy()
        filtered_dff["Job Title"] = filtered_dff["Job Title"].fillna("Not Specified")
        filtered_dff["Department"] = filtered_dff["Department"].fillna("Not Specified")

        if selected_dept:
            filtered_dff = filtered_dff[filtered_dff["Department"] == selected_dept]
        if exp_range:
            filtered_dff = filtered_dff[(filtered_dff["ExperienceYears"] >= exp_range[0]) & (filtered_dff["ExperienceYears"] <= exp_range[1])]

        filtered_job_counts = filtered_dff["Job Title"].value_counts().to_dict()

        filtered_dff = df.copy()
        filtered_dff["Job Title"] = filtered_dff["Job Title"].fillna("Not Specified")
        filtered_dff["Department"] = filtered_dff["Department"].fillna("Not Specified")

        if selected_job:
            filtered_dff = filtered_dff[filtered_dff["Job Title"] == selected_job]
        if exp_range:
            filtered_dff = filtered_dff[(filtered_dff["ExperienceYears"] >= exp_range[0]) & (filtered_dff["ExperienceYears"] <= exp_range[1])]

        filtered_dept_counts = filtered_dff["Department"].value_counts().to_dict()

        # Get **all** unique job titles and departments
        all_jobs = sorted(df["Job Title"].fillna("Not Specified").unique())
        all_depts = sorted(df["Department"].fillna("Not Specified").unique())

        # Ensure "Not Specified" is included in counts (even if missing)
        filtered_job_counts["Not Specified"] = filtered_job_counts.get("Not Specified", 0)
        filtered_dept_counts["Not Specified"] = filtered_dept_counts.get("Not Specified", 0)

        # Create dropdown options with counts (show 0 if no results)
        job_options = [{"label": f"{job} ({filtered_job_counts.get(job, 0)})", "value": job} for job in all_jobs]
        dept_options = [{"label": f"{dept} ({filtered_dept_counts.get(dept, 0)})", "value": dept} for dept in all_depts]
        specialist_counts = filtered_dff["Specialist eller ST-fysiker"].value_counts().to_dict()
        all_specialists = ["Specialist", "ST-fysiker", "Nej"]
        specialist_options = [
            {"label": html.Span(f"{spec} ({specialist_counts.get(spec, 0)})", style={"margin-left": "4px"}), "value": spec}
            for spec in all_specialists
        ]

        return job_options, dept_options, specialist_options





    # Update graph based on filters and active tab
    @app.callback(
        Output("tab-content", "children"),
        [Input("tabs", "value"),
         Input("job-dropdown", "value"),
         Input("dept-dropdown", "value"),
         Input("exp-slider", "value"),
         Input("specialist-filter", "value")]  # **New Input for Checkbox Filter**

    )
    def update_graph(selected_tab, selected_job, selected_dept, exp_range, selected_specialists):
        dff = df.copy()

        # Replace NaN values
        dff["Job Title"] = dff["Job Title"].fillna("Not Specified")
        dff["Department"] = dff["Department"].fillna("Not Specified")
        dff["Specialist eller ST-fysiker"] = dff["Specialist eller ST-fysiker"].fillna("Nej")

        # Apply filters
        filtered_dff = dff.copy()
        if selected_job:
            filtered_dff = filtered_dff[filtered_dff["Job Title"] == selected_job]
        if selected_dept:
            filtered_dff = filtered_dff[filtered_dff["Department"] == selected_dept]
        if exp_range:
            filtered_dff = filtered_dff[(filtered_dff["ExperienceYears"] >= exp_range[0]) & (filtered_dff["ExperienceYears"] <= exp_range[1])]
        filtered_dff = filtered_dff[filtered_dff["Specialist eller ST-fysiker"].isin(selected_specialists)]
        # if selected_specialists:

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
        elif selected_tab == "scatterplot2":
            # Default: All dots are faded and small
            dff["opacity"] = 0.2
            dff["size"] = 10
            
            if not filtered_dff.empty:
                
                # Create a unique identifier for each row to properly match
                dff['row_id'] = dff.apply(lambda row: f"{row['Job Title']}_{row['Department']}_{row['ExperienceYears']}_{row['Månadslön totalt']}", axis=1)
                filtered_dff['row_id'] = filtered_dff.apply(lambda row: f"{row['Job Title']}_{row['Department']}_{row['ExperienceYears']}_{row['Månadslön totalt']}", axis=1)
                
                # Use this identifier to highlight the matching rows
                dff.loc[dff['row_id'].isin(filtered_dff['row_id']), "opacity"] = 0.9
                dff.loc[dff['row_id'].isin(filtered_dff['row_id']), "size"] = 20
            
                # Clean up temporary column
                dff = dff.drop('row_id', axis=1)

            # Create the scatter plot
            fig = px.scatter(dff, x="ExperienceYears", y="Månadslön totalt",
                            title="Salary vs Experience 2",
                            labels={"ExperienceYears": "Years of Experience", "Månadslön totalt": "Total Monthly Salary"},
                            color="Job Title",
                            hover_data=["Department"],
                            size=dff["size"])

            # **Apply per-point opacity manually**
            for trace in fig.data:
                job_title = trace.name  # Get the job title associated with this trace
                trace_opacity = dff[dff["Job Title"] == job_title]["opacity"].tolist()  # Get correct opacities
                trace.marker.opacity = trace_opacity  # Assign correct per-point opacity

            
            # Remove global trendline and add a filtered one
            if not filtered_dff.empty:
                trend_fig = px.scatter(filtered_dff, x="ExperienceYears", y="Månadslön totalt",
                                    trendline="ols", trendline_scope="overall",
                                    color_discrete_sequence=["black"])  
                fig.add_trace(trend_fig.data[1])  # Add only the trendline

        return dcc.Graph(figure=fig, style={"width": "100%", "height": "100%"})

    
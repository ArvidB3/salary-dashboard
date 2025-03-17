import colorsys
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
         Input("specialist-filter", "value"),
         Input("color-by-dropdown", "value")]

    )
    def update_graph(selected_tab, selected_job, selected_dept, exp_range, selected_specialists, color_by):
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
                            color=color_by,
                            hover_data=["Department"],
                            size=dff["size"])

            # **Apply per-point opacity manually**
            for trace in fig.data:
                category_value = trace.name  # Get the job title associated with this trace
                trace_opacity = dff[dff[color_by] == category_value]["opacity"].tolist()  # Get correct opacities
                trace.marker.opacity = trace_opacity  # Assign correct per-point opacity

            # **Add general trend line for all data (black)**
            if not filtered_dff.empty:
                trend_fig = px.scatter(filtered_dff, x="ExperienceYears", y="Månadslön totalt",
                                    trendline="ols", trendline_scope="overall",
                                    color_discrete_sequence=["black"])  # General trend line in black
                fig.add_trace(trend_fig.data[1])  # Add only the trend line

            # **Generate trend lines only for filtered groups**
            # **Get only the unique categories that are still present after filtering**
            visible_categories = filtered_dff[color_by].unique()
            category_color_map = {trace.name: trace.marker.color for trace in fig.data}
            for category_value in visible_categories:
                group_df = filtered_dff[filtered_dff[color_by] == category_value]  

                if not group_df.empty:  # Ensure the group has data
                    def darken_color(hex_color, factor=0.8):
                        """Darkens a hex color by a given factor (default: 20% darker)."""
                        hex_color = hex_color.lstrip('#')
                        rgb = tuple(int(hex_color[i:i+2], 16) / 255.0 for i in (0, 2, 4))  # Convert HEX to RGB (0-1)
                        
                        # Convert RGB to HLS, reduce lightness
                        h, l, s = colorsys.rgb_to_hls(*rgb)
                        darker_rgb = colorsys.hls_to_rgb(h, max(0, l * factor), s)  # Reduce lightness
                        
                        # Convert back to HEX
                        return f'#{int(darker_rgb[0] * 255):02X}{int(darker_rgb[1] * 255):02X}{int(darker_rgb[2] * 255):02X}'

                    # Get original color and darken it
                    original_color = category_color_map.get(category_value, "gray")
                    trend_color = darken_color(original_color)

                    # **Generate the "outline" as a slightly thicker black trend line**
                    outline_trend = px.scatter(group_df, x="ExperienceYears", y="Månadslön totalt",
                                            trendline="ols", trendline_scope="overall",
                                            color_discrete_sequence=["white"])  # Black outline
                    outline_trend.data[1].line.width = 6  # Make it thicker
                    fig.add_trace(outline_trend.data[1])  # Add outline first (behind)

                    # **Generate the actual colored trend line on top**
                    group_trend = px.scatter(group_df, x="ExperienceYears", y="Månadslön totalt",
                                            trendline="ols", trendline_scope="overall",
                                            color_discrete_sequence=[trend_color])  # Use exact dot color
                    group_trend.data[1].line.width = 4  # Keep it thinner
                    fig.add_trace(group_trend.data[1])  # Add main trend line on top




        return dcc.Graph(figure=fig, style={"width": "100%", "height": "100%"})

    
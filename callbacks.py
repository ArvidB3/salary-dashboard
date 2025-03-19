import colorsys
import html
from dash import Input, Output, State, dcc, html
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


def update_filter_options(_, selected_jobs, selected_depts, selected_specialists, exp_range, df):
    # Make a copy of the dataset
    dff = df.copy()

    # Apply filters (excluding the dropdown being updated)
    filtered_dff = df.copy()
    filtered_dff = filtered_dff[filtered_dff["Department"].isin(selected_depts)]
    filtered_dff = filtered_dff[filtered_dff["Job Title"].isin(selected_jobs)]
    filtered_dff = filtered_dff[filtered_dff["Specialist eller ST-fysiker"].isin(selected_specialists)]
    if exp_range:
        filtered_dff = filtered_dff[
            (filtered_dff["ExperienceYears"] >= exp_range[0]) & (filtered_dff["ExperienceYears"] <= exp_range[1])
        ]

    # Get the updated counts for each category
    job_counts = filtered_dff["Job Title"].value_counts().to_dict()
    dept_counts = filtered_dff["Department"].value_counts().to_dict()
    specialist_counts = filtered_dff["Specialist eller ST-fysiker"].value_counts().to_dict()

    # Get **all** unique job titles, departments, and specialists
    all_jobs = sorted(df["Job Title"].fillna("Not Specified").unique())
    all_depts = sorted(df["Department"].fillna("Not Specified").unique())
    all_specialists = ["Specialist", "ST-fysiker", "Nej"]

    # Ensure "Not Specified" is included in counts (even if missing)
    job_counts["Not Specified"] = job_counts.get("Not Specified", 0)
    dept_counts["Not Specified"] = dept_counts.get("Not Specified", 0)

    # Create checklist options with counts
    job_options = [
        {"label": html.Span(f"{job} ({job_counts.get(job, 0)})", style={"margin-left": "8px"}), "value": job}
        for job in all_jobs
    ]
    dept_options = [
        {"label": html.Span(f"{dept} ({dept_counts.get(dept, 0)})", style={"margin-left": "8px"}), "value": dept}
        for dept in all_depts
    ]
    specialist_options = [
        {"label": html.Span(f"{spec} ({specialist_counts.get(spec, 0)})", style={"margin-left": "8px"}), "value": spec}
        for spec in all_specialists
    ]

    return job_options, selected_jobs, dept_options, selected_depts, specialist_options, selected_specialists

def register_callbacks(app, df):
    @app.callback(
        [
            Output("job-title-filter", "options"),
            Output("job-title-filter", "value", allow_duplicate=True),
            Output("department-filter", "options"),
            Output("department-filter", "value", allow_duplicate=True),
            Output("specialist-filter", "options"),
            Output("specialist-filter", "value", allow_duplicate=True),
        ],
        [
            Input("job-title-filter", "value"),
            Input("department-filter", "value"),
            Input("specialist-filter", "value"),
            Input("exp-slider", "value"),
        ],
        prevent_initial_call=True  # Ensures the callback does not trigger on app load
    )
    def callback_update_filter_options(selected_jobs, selected_depts, selected_specialists, exp_range):
        return update_filter_options(None, selected_jobs, selected_depts, selected_specialists, exp_range, df)

    # Update graph based on filters and active tab
    @app.callback(
        Output("tab-content", "children"),
        [Input("tabs", "value"),
         Input("job-title-filter", "value"),
         Input("department-filter", "value"),
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
        filtered_dff = filtered_dff[filtered_dff["Job Title"].isin(selected_job)]
        filtered_dff = filtered_dff[filtered_dff["Department"].isin(selected_dept)]
        filtered_dff = filtered_dff[filtered_dff["Specialist eller ST-fysiker"].isin(selected_specialists)]
        if exp_range:
            filtered_dff = filtered_dff[(filtered_dff["ExperienceYears"] >= exp_range[0]) & (filtered_dff["ExperienceYears"] <= exp_range[1])]



            
        # Generate the correct graph based on the selected tab
        if selected_tab == "histogram":
            if filtered_dff.empty:
                return html.Div([html.H4("No data available for the selected filters.", style={"text-align": "center", "margin-top": "20px"})])
            else:
                fig = px.histogram(filtered_dff, x="Månadslön totalt", nbins=20,
                                labels={"Månadslön totalt": "Total Monthly Salary"},
                                marginal="box", opacity=0.7)
                fig.update_layout(bargap=0.1)
        elif selected_tab == "statistics":
            # Create table rows as a list
            table_rows = [
                html.Tr([
                    html.Td("Number of entries", style={"text-align": "right"}),
                    html.Td(f"{len(df)}", style={"text-align": "right"}),
                    html.Td(f"{len(filtered_dff)}", style={"text-align": "right"})
                ]),
                html.Tr([
                    html.Td("25th percentile salary", style={"text-align": "right"}),
                    html.Td(f"{df['Månadslön totalt'].quantile(0.25):,.0f}", style={"text-align": "right"}),
                    html.Td(f"{filtered_dff['Månadslön totalt'].quantile(0.25):,.0f}", style={"text-align": "right"})
                ]),
                html.Tr([
                    html.Td("Median salary", style={"text-align": "right", "border-bottom": "2px solid black", "border-top": "2px solid black"}),
                    html.Td(f"{df['Månadslön totalt'].median():,.0f}", style={"text-align": "right", "border-bottom": "2px solid black", "border-top": "2px solid black"}),
                    html.Td(f"{filtered_dff['Månadslön totalt'].median():,.0f}", style={"text-align": "right", "border-bottom": "2px solid black", "border-top": "2px solid black"})
                ]),
                html.Tr([
                    html.Td("Average salary", style={"text-align": "right"}),
                    html.Td(f"{df['Månadslön totalt'].mean():,.0f}", style={"text-align": "right"}),
                    html.Td(f"{filtered_dff['Månadslön totalt'].mean():,.0f}", style={"text-align": "right"})
                ]),
                html.Tr([
                    html.Td("75th percentile salary", style={"text-align": "right"}),
                    html.Td(f"{df['Månadslön totalt'].quantile(0.75):,.0f}", style={"text-align": "right"}),
                    html.Td(f"{filtered_dff['Månadslön totalt'].quantile(0.75):,.0f}", style={"text-align": "right"})
                ]),
                html.Tr([
                    html.Td("Average experience (years)", style={"text-align": "right"}),
                    html.Td(f"{df['ExperienceYears'].mean():.1f}", style={"text-align": "right"}),
                    html.Td(f"{filtered_dff['ExperienceYears'].mean():.1f}", style={"text-align": "right"})
                ])
            ]

            # Create the table
            stats_table = html.Div(
                dbc.Table(
                    [
                        html.Thead(html.Tr([
                            html.Th("Metric", style={"text-align": "right", "min-width": "150px", "white-space": "nowrap"}),  
                            html.Th("Full Set", style={"text-align": "right", "min-width": "120px", "white-space": "nowrap"}),  
                            html.Th("Filtered Set", style={"text-align": "right", "min-width": "120px", "white-space": "nowrap"})
                        ])),
                        html.Tbody(table_rows)
                    ],
                    bordered=True,
                    striped=True,
                    hover=True,
                    className="mb-4",
                    style={"width": "auto"}
                ),
                style={"display": "flex", "justify-content": "center", "margin-top": "40px"}
            )


            return stats_table
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
            
            # Fix legend
            for trace in fig.data:
                trace.showlegend = False
                if not "trendline" in trace.name.lower():
                    trace.marker.opacity = dff[dff[color_by] == trace.name]["opacity"].tolist()  # Apply opacity to points
                
                    # Add a fully opaque dummy legend marker
                    fig.add_trace(
                        go.Scatter(
                            x=[None], y=[None],  # Invisible data point
                            mode="markers",
                            marker=dict(size=10, color=trace.marker.color, opacity=1.0),  # Full opacity legend marker
                            name=trace.name,  # Keep legend label
                            showlegend=True  # Ensures it appears in the legend
                        )
                    )
            fig.update_layout(
                legend=dict(
                    font=dict(size=16)  # Adjust size as needed
                )
            )




        return dcc.Graph(figure=fig, style={"width": "100%", "height": "100%"})

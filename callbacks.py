import colorsys
import html
from dash import Input, Output, State, dcc, html, callback_context
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from cache_config import cache
import time

@cache.memoize(timeout=300)
def get_filtered_data(selected_jobs, selected_depts, selected_specialists, exp_range, df):
    print("\tRunning get_filtered_data")
    print(f"\tSelected Jobs: {selected_jobs}\n")

    # Apply filters
    filtered_dff = df.copy()
    filtered_dff = filtered_dff[filtered_dff["Department"].isin(selected_depts)]
    filtered_dff = filtered_dff[filtered_dff["Job Title"].isin(selected_jobs)]
    filtered_dff = filtered_dff[filtered_dff["Specialist eller ST-fysiker"].isin(selected_specialists)]
    if exp_range:
        filtered_dff = filtered_dff[
            (filtered_dff["ExperienceYears"] >= exp_range[0]) & (filtered_dff["ExperienceYears"] <= exp_range[1])
        ]

    return filtered_dff

def get_filtered_data_wrapper(selected_jobs, selected_depts, selected_specialists, exp_range, df):
    return get_filtered_data(
                  tuple(sorted(selected_jobs)), 
                  tuple(sorted(selected_depts)), 
                  tuple(sorted(selected_specialists)), 
                  tuple(map(int, exp_range)),
                  df)

@cache.memoize(timeout=300)
def update_filter_options(filtered_dff, df):
    print("Running update_filter_options\n")

    # Count occurrences in the already filtered dataframe
    job_counts = filtered_dff["Job Title"].value_counts().to_dict()
    dept_counts = filtered_dff["Department"].value_counts().to_dict()
    specialist_counts = filtered_dff["Specialist eller ST-fysiker"].value_counts().to_dict()

    # Get all unique job titles, departments, and specialists (from full dataset)
    all_jobs = sorted(df["Job Title"].fillna("Not Specified").unique())
    all_depts = sorted(df["Department"].fillna("Not Specified").unique())
    all_specialists = ["Specialist", "ST-fysiker", "Nej"]

    # Ensure "Not Specified" is included
    job_counts["Not Specified"] = job_counts.get("Not Specified", 0)
    dept_counts["Not Specified"] = dept_counts.get("Not Specified", 0)

    # Create checklist options with updated counts
    job_options = [{"label": html.Span(f"{job} ({job_counts.get(job, 0)})", style={"margin-left": "8px"}), "value": job} for job in all_jobs]
    dept_options = [{"label": html.Span(f"{dept} ({dept_counts.get(dept, 0)})", style={"margin-left": "8px"}), "value": dept} for dept in all_depts]
    specialist_options = [{"label": html.Span(f"{spec} ({specialist_counts.get(spec, 0)})", style={"margin-left": "8px"}), "value": spec} for spec in all_specialists]

    return job_options, dept_options, specialist_options

def register_callbacks(app, df):
    # Update graph based on filters and active tab
    @app.callback(
        [
            Output("tab-content", "children"),  # Graph
            Output("job-title-filter", "options"),
            Output("job-title-filter", "value"),
            Output("department-filter", "options"),
            Output("department-filter", "value"),
            Output("specialist-filter", "options"),
            Output("specialist-filter", "value"),
        ],
        [
            Input("tabs", "value"),
            Input("job-title-filter", "value"),
            Input("department-filter", "value"),
            Input("specialist-filter", "value"),
            Input("exp-slider", "value"),
            Input("color-by-dropdown", "value"),
            Input("reset-filters", "n_clicks"),
        ]
    )
    def update_graph(selected_tab, selected_jobs, selected_depts, selected_specialists, exp_range, color_by, reset_clicks):
        # Apply filters
        start_time = time.time()  # Start measuring time

        ctx = callback_context
        trigger_id = ctx.triggered[0]["prop_id"].split(".")[0] if ctx.triggered else None

        # First Load (No trigger detected) or Reset Button Clicked
        if not ctx.triggered or trigger_id == "reset-filters":
            selected_jobs = df["Job Title"].dropna().unique().tolist()
            selected_depts = df["Department"].dropna().unique().tolist()
            selected_specialists = ["Specialist", "ST-fysiker", "Nej"]
            
        dff = df.copy()
        filtered_dff = get_filtered_data_wrapper(selected_jobs, selected_depts, selected_specialists, exp_range, df)

        job_options, dept_options, specialist_options = update_filter_options(filtered_dff, df)

        filtering_done_time = time.time()
            
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


            return stats_table, job_options, selected_jobs, dept_options, selected_depts, specialist_options, selected_specialists
        elif selected_tab == "scatterplot2":
            # Default: All dots are faded and small
            dff["opacity"] = 0.2
            dff["size"] = 10
            
            if not filtered_dff.empty:
                
                # Create a unique identifier for each row to properly match
                dff['row_id'] = dff.apply(lambda row: f"{row['Job Title']}_{row['Department']}_{row['ExperienceYears']}_{row['Månadslön totalt']}", axis=1)
                filtered_dff['row_id'] = filtered_dff.apply(lambda row: f"{row['Job Title']}_{row['Department']}_{row['ExperienceYears']}_{row['Månadslön totalt']}", axis=1)

                # dff['row_id'] = dff.apply(lambda row: f"{row['Job Title']}_{row['Department']}_{row['ExperienceYears']}_{row['Månadslön totalt']}", axis=1)
                # filtered_dff['row_id'] = filtered_dff.apply(lambda row: f"{row['Job Title']}_{row['Department']}_{row['ExperienceYears']}_{row['Månadslön totalt']}", axis=1)
                
                # Use this identifier to highlight the matching rows
                filtered_ids = set(filtered_dff['row_id'])
                dff.loc[dff['row_id'].isin(filtered_ids), ["opacity", "size"]] = [0.9, 20]
                # dff.loc[dff['row_id'].isin(filtered_dff['row_id']), "opacity"] = 0.9
                # dff.loc[dff['row_id'].isin(filtered_dff['row_id']), "size"] = 20

            
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
                    # outline_trend = px.scatter(group_df, x="ExperienceYears", y="Månadslön totalt",
                    #                         trendline="ols", trendline_scope="overall",
                    #                         color_discrete_sequence=["white"])  # Black outline
                    # outline_trend.data[1].line.width = 6  # Make it thicker
                    # fig.add_trace(outline_trend.data[1])  # Add outline first (behind)

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

        all_done_time = time.time()
        filtering_done = round(filtering_done_time - start_time, 4)  # Measure execution time
        graph_time = round(all_done_time - filtering_done_time, 4)  # Measure execution time
        everything_done = filtering_done + graph_time

        debug_info = (
            f"Time to Filter: {filtering_done}s | "
            f"Time to Generate Graph: {graph_time}s | "
            f"Total Time: {everything_done}s"
        )

        print(f"Timing Info: {debug_info}")  # Logs to backend console


        return (
            html.Div([
                dcc.Graph(figure=fig, style={"width": "100%", "height": "100%"}),
                html.P(debug_info, style={"margin-top": "10px", "font-size": "14px", "color": "gray"})
            ])
        ), job_options, selected_jobs, dept_options, selected_depts, specialist_options, selected_specialists


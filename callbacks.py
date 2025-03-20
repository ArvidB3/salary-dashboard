import colorsys
import html
from dash import Input, Output, State, dcc, html, callback_context
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from cache_config import cache
import time
import numpy as np
import statsmodels.api as sm
from statistics_module import compute_trendline

idx_to_color = {
    0: "blue",
    1: "red",
    2: "green",
    3: "purple",
    4: "orange"
}
# color_variants = {
#     'blue': {'opaque': 'rgba(31, 119, 180, 1.0)', 'faded': 'rgba(31, 119, 180, 0.2)', 'darker': 'rgba(24, 95, 144, 1.0)'},
#     'red': {'opaque': 'rgba(214, 39, 40, 1.0)', 'faded': 'rgba(214, 39, 40, 0.2)', 'darker': 'rgba(171, 31, 31, 1.0)'},
#     'green': {'opaque': 'rgba(44, 160, 44, 1.0)', 'faded': 'rgba(44, 160, 44, 0.2)', 'darker': 'rgba(35, 128, 35, 1.0)'},
#     'purple': {'opaque': 'rgba(148, 103, 189, 1.0)', 'faded': 'rgba(148, 103, 189, 0.2)', 'darker': 'rgba(118, 70, 162, 1.0)'},
#     'orange': {'opaque': 'rgba(255, 127, 14, 1.0)', 'faded': 'rgba(255, 127, 14, 0.2)', 'darker': 'rgba(215, 100, 0, 1.0)'}
#     'cyan': 
# }

color_variants = {
    'blue': {'opaque': 'rgba(99, 110, 250, 1.0)', 'faded': 'rgba(99, 110, 250, 0.2)', 'darker': 'rgba(79, 88, 200, 1.0)'},
    'red': {'opaque': 'rgba(239, 85, 56, 1.0)', 'faded': 'rgba(239, 85, 56, 0.2)', 'darker': 'rgba(191, 68, 45, 1.0)'},
    'green': {'opaque': 'rgba(0, 204, 150, 1.0)', 'faded': 'rgba(0, 204, 150, 0.2)', 'darker': 'rgba(0, 163, 120, 1.0)'},
    'purple': {'opaque': 'rgba(171, 99, 250, 1.0)', 'faded': 'rgba(171, 99, 250, 0.2)', 'darker': 'rgba(137, 79, 200, 1.0)'},
    'orange': {'opaque': 'rgba(255, 161, 90, 1.0)', 'faded': 'rgba(255, 161, 90, 0.2)', 'darker': 'rgba(204, 129, 72, 1.0)'},
    'cyan': {'opaque': 'rgba(25, 211, 243, 1.0)', 'faded': 'rgba(25, 211, 243, 0.2)', 'darker': 'rgba(20, 169, 195, 1.0)'}
}


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
            
            # Unique row identifier for filtering
            dff['row_id'] = dff[['Job Title', 'Department', 'ExperienceYears', 'Månadslön totalt']].astype(str).agg('_'.join, axis=1)
            filtered_dff['row_id'] = filtered_dff[['Job Title', 'Department', 'ExperienceYears', 'Månadslön totalt']].astype(str).agg('_'.join, axis=1)

            # Determine which rows are in the filtered DataFrame
            filtered_set = set(filtered_dff['row_id'])  # Convert to set for faster lookup
            dff['is_filtered'] = dff['row_id'].apply(lambda x: x in filtered_set)

            # Split data into two groups
            filtered_points = dff[dff['is_filtered']]
            unfiltered_points = dff[~dff['is_filtered']]
            
            all_categories = dff[color_by].unique()
            visible_categories = filtered_dff[color_by].unique()

            # Create traces for filtered and unfiltered points
            fig = go.Figure()

            # Loop through each category and create separate traces
            trend_traces = []
            for idx, category in enumerate(all_categories):
                category_df = dff[dff[color_by] == category]
                filtered_points = category_df[category_df['is_filtered']]
                unfiltered_points = category_df[~category_df['is_filtered']]
                categori_visible = category in visible_categories

                # Get color based on index, cycle if more than 5 categories
                color_name = idx_to_color[idx % len(idx_to_color)]
                base_color = color_variants[color_name]

                # Filtered (highlighted) points
                fig.add_trace(go.Scattergl(
                    x=filtered_points['ExperienceYears'],
                    y=filtered_points['Månadslön totalt'],
                    mode='markers',
                    marker=dict(size=20, color=base_color['opaque'], line=dict(width=1, color="white")),
                    name=category,
                    showlegend=categori_visible,
                ))
                
                # Unfiltered (faded) points
                fig.add_trace(go.Scattergl(
                    x=unfiltered_points['ExperienceYears'],
                    y=unfiltered_points['Månadslön totalt'],
                    mode='markers',
                    marker=dict(size=15, color=base_color['faded']),
                    name=category,
                    showlegend=not categori_visible
                ))

                group_df = filtered_dff[filtered_dff[color_by] == category]  

                if not group_df.empty:  # Ensure the group has data
                    # Find the index of the category in all_categories
                    trend_color = base_color["darker"]

                    trend_data = compute_trendline(group_df["ExperienceYears"], group_df["Månadslön totalt"])
                    if trend_data:
                        trend_x, trend_y = trend_data
                        trend_trace = go.Scattergl(
                            x=trend_x, y=trend_y, mode="lines",
                            line=dict(color=trend_color, width=2),
                            showlegend=False  # Hide from legend
                        )
                        trend_traces.append(trend_trace)
                        


            # **Add general trend line for all data (black)**
            if not filtered_dff.empty:
                trend_data = compute_trendline(filtered_dff["ExperienceYears"], filtered_dff["Månadslön totalt"])
                if trend_data:
                    trend_x, trend_y = trend_data
                    fig.add_trace(go.Scattergl(
                        x=trend_x, y=trend_y, mode="lines",
                        line=dict(color="black", width=2),
                        name="Trend line",
                        showlegend=True
                    ))

            for trend_trace in trend_traces:
                trend_trace.showlegend = False  # Hide from legend
                fig.add_trace(trend_trace)

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


        return dcc.Graph(figure=fig, style={"width": "100%", "height": "100%"}), job_options, selected_jobs, dept_options, selected_depts, specialist_options, selected_specialists
    
        # return (
        #     html.Div([
        #         dcc.Graph(figure=fig, style={"width": "100%", "height": "100%"}),
        #         html.P(debug_info, style={"margin-top": "10px", "font-size": "14px", "color": "gray"})
        #     ])
        # ), job_options, selected_jobs, dept_options, selected_depts, specialist_options, selected_specialists


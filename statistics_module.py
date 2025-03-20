import numpy as np
import plotly.graph_objects as go
from cache_config import cache

@cache.memoize(timeout=300)
def compute_trendline(x_values, y_values):
    """
    Compute a simple linear trendline (straight line) given x and y values.

    Args:
        x_values (array-like): X-axis values (ExperienceYears).
        y_values (array-like): Y-axis values (Månadslön totalt).

    Returns:
        tuple | None: (trend_x, trend_y) arrays for plotting, or None if insufficient data.
    """
    if len(x_values) < 2:  # No trendline if fewer than 2 points
        return None  

    # Fit a simple linear regression (1st-degree polynomial)
    slope, intercept = np.polyfit(x_values, y_values, 1)

    # Generate trendline endpoints (only start & end for a straight line)
    trend_x = np.array([min(x_values), max(x_values)])
    trend_y = slope * trend_x + intercept

    return trend_x, trend_y

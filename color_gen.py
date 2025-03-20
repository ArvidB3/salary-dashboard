import colorsys

# Helper function to convert a hex color to an RGBA string
def hex_to_rgba(hex_color, alpha):
    hex_color = hex_color.lstrip('#')
    r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    return f'rgba({r}, {g}, {b}, {alpha})'

# Helper function to darken a hex color by a given factor
def darken_color(hex_color, factor=0.8):
    hex_color = hex_color.lstrip('#')
    # Convert HEX to RGB (0-1)
    r, g, b = (int(hex_color[i:i+2], 16) / 255.0 for i in (0, 2, 4))
    # Convert RGB to HLS
    h, l, s = colorsys.rgb_to_hls(r, g, b)
    # Reduce lightness, ensure it doesn't go below 0
    l = max(0, l * factor)
    # Convert back to RGB
    r_d, g_d, b_d = colorsys.hls_to_rgb(h, l, s)
    # Convert back to HEX
    return f'#{int(r_d*255):02X}{int(g_d*255):02X}{int(b_d*255):02X}'

# Define the base colors (using Plotly default colors)
base_colors = {
    'blue': '#1f77b4',
    'red': '#d62728',
    'green': '#2ca02c',
    'purple': '#9467bd',
    'orange': '#ff7f0e'
}

# Precompute the variants for each base color
color_variants = {}
for name, hex_color in base_colors.items():
    opaque = hex_to_rgba(hex_color, 1.0)      # Fully opaque
    faded = hex_to_rgba(hex_color, 0.2)         # 20% opacity
    # Darken the base color then make it fully opaque
    darker_hex = darken_color(hex_color, factor=0.8)
    darker = hex_to_rgba(darker_hex, 1.0)
    color_variants[name] = {
        'opaque': opaque,
        'faded': faded,
        'darker': darker
    }

# Example output:
for color, variants in color_variants.items():
    print(f"{color}: {variants}")
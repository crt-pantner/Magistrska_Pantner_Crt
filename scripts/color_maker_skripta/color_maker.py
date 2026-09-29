import pandas as pd
from pathlib import Path
import argparse    
import colorsys
import pandas as pd
import numpy as np
import matplotlib.colors as mcolors

def main():
    arguments = parse_arguments()
    df = pd.read_csv(filepath_or_buffer=arguments.metadata, delimiter=",")
    color_df = pd.read_csv(filepath_or_buffer=arguments.colors, delimiter=",")
    
    df["order"] = df["order"].fillna(df["no rank"])
    df["family"] = df["family"].fillna(df["no rank"])
    
    merged_df = df.merge(color_df, on="order")
    
    # Group by order, count unique families, and convert to a dictionary
    families_per_order_dict = merged_df.groupby("order")["family"].unique().to_dict()


    # 2. Function to generate N shades of a base color
    def generate_shades(base_color, n_shades, min_lightness=0.30, max_lightness=0.80):
        """Generates n_shades of a color by varying its lightness in HLS space."""
        rgb = mcolors.to_rgb(base_color)
        h, l, s = colorsys.rgb_to_hls(*rgb)
        
        if n_shades == 1:
            return [mcolors.to_hex(rgb)]
        
        # From min_lightness (darkest) to max_lightness (lightest)
        lightness_steps = np.linspace(min_lightness, max_lightness, n_shades)
        
        return [
            mcolors.to_hex(colorsys.hls_to_rgb(h, new_l, s))
            for new_l in lightness_steps
        ]

    # 3. Build the (order, family) -> shade mapping ordered by abundance
    FALLBACK_COLOR = '#cccccc'
    order_color_map = dict(zip(color_df['order'], color_df['color']))

    # Count family occurrences per order and sort from most abundant to least abundant
    family_counts = (
        merged_df.groupby(['order', 'family'], dropna=False)
        .size()
        .reset_index(name='family_count')
        .sort_values(['order', 'family_count', 'family'], ascending=[True, False, True])
    )

    shade_records = []
    for order, group in family_counts.groupby('order', sort=False):
        # Fetch base color or fall back to neutral grey if order is unmapped
        base_color = order_color_map.get(order, FALLBACK_COLOR)
        
        families = group['family'].tolist()
        counts = group['family_count'].tolist()
        
        # Generate shades (even unmapped orders get shaded variations of the fallback grey,
        # or you can lock them to flat FALLBACK_COLOR if preferred)
        shades = generate_shades(base_color, len(families))
        
        for fam, count, shade in zip(families, counts, shades):
            shade_records.append({
                'order': order,
                'family': fam,
                'family_count': count,
                'order_color': mcolors.to_hex(mcolors.to_rgb(base_color)),
                'family_shade': shade
            })

    shade_map_df = pd.DataFrame(shade_records)

    # 4. Merge back into metadata DataFrame and catch any remaining NaNs
    df = df.merge(shade_map_df, on=['order', 'family'], how='left')
    df['order_color'] = df['order_color'].fillna(FALLBACK_COLOR)
    df['family_shade'] = df['family_shade'].fillna(FALLBACK_COLOR)

    df.insert(0, "final_name", "jgi|" + df["Organism Id"].astype(str) + "|" + df["Protein Id"].astype(str) + "|" + df["Name"].astype(str))

    df.to_csv(arguments.output, index=False)

    
"""
# Get user input for colors
order_colors = {}
for order in sorted_orders:
    color = input(f"Color for {order}: ").strip()
    order_colors[order] = color

# Generate lighter colors for each family
family_colors = {}
for order, families in order_families.items():
    num_families = len(families)
    base_color = order_colors[order]
    
    for i, family in enumerate(families):
        factor = 0.3 + 0.7 * (i / max(1, num_families - 1))  # Adjust factor to create a gradient
        family_colors[family] = lighten_color(base_color, factor)"""


#def generate_ligher_colors()

def print_panda(dataframe: pd.DataFrame):
    dataframe.to_html("printed.html")

def parse_arguments():
    # Initialize the parser
    parser = argparse.ArgumentParser(
        description="Program generates colors based on metadata file and phylogeny."
    )

    # Add arguments
    parser.add_argument(
        "-m",
        "--metadata", 
        type=Path,
        required=True, 
        default="", 
        help="Path to metadata file."
    )
    
    parser.add_argument(
        "-c", "--colors", 
        type=Path, 
        default="", 
        help="Path to order/color mapping"
    )

    parser.add_argument(
            "-o", "--output", 
            type=Path, 
            default="", 
            help="Path to output file."
        )
    
    parser.add_argument(
        "-v", "--verbose", 
        action="store_true", 
        help="Enable verbose output"
    )

    # Parse and return the arguments
    return parser.parse_args()



if __name__=="__main__":
    main()

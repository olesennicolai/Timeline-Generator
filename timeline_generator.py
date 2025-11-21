#!/usr/bin/env python3
"""
Timeline Generator - Creates horizontal timeline visualizations from CSV data
Exports as PNG with customizable styling options
"""

import sys
import json
from datetime import datetime
from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates


def load_config(config_path="config.json"):
    """Load configuration from JSON file"""
    try:
        with open(config_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Warning: {config_path} not found. Using default configuration.")
        return get_default_config()


def get_default_config():
    """Return default configuration if config file is missing"""
    return {
        "dimensions": {"width": 16, "height": 10, "dpi": 300, "margin_left": 1.0,
                      "margin_right": 1.0, "margin_top": 1.5, "margin_bottom": 1.5},
        "colors": {"background": "#FFFFFF", "timeline_line": "#2C3E50",
                  "above_items": "#3498DB", "below_items": "#E74C3C",
                  "text": "#2C3E50", "date_text": "#7F8C8D"},
        "fonts": {"family": "sans-serif", "title_size": 16, "label_size": 10, "date_size": 8},
        "visual": {"timeline_line_width": 2, "marker_size": 10, "connector_line_width": 1,
                  "vertical_spacing": 0.8, "date_format_display": "%d.%m.%Y"}
    }


def parse_european_date(date_str):
    """Parse European date format (DD.MM.YYYY)"""
    try:
        return datetime.strptime(date_str.strip(), "%d.%m.%Y")
    except ValueError as e:
        raise ValueError(f"Invalid date format: '{date_str}'. Expected DD.MM.YYYY format.") from e


def load_timeline_data(csv_path):
    """Load and parse CSV timeline data"""
    try:
        df = pd.read_csv(csv_path)
    except FileNotFoundError:
        raise FileNotFoundError(f"CSV file not found: {csv_path}")

    # Check required columns
    required_cols = ['name', 'date']
    missing_cols = [col for col in required_cols if col not in df.columns]
    if missing_cols:
        raise ValueError(f"Missing required columns: {', '.join(missing_cols)}")

    # Parse dates
    df['parsed_date'] = df['date'].apply(parse_european_date)

    # Sort by date
    df = df.sort_values('parsed_date')

    # Handle position column
    has_position = 'position' in df.columns
    if not has_position:
        # Alternate positions if not specified
        df['position'] = ['above' if i % 2 == 0 else 'below' for i in range(len(df))]
    else:
        # Normalize position values and fill missing with alternating
        df['position'] = df['position'].fillna('')
        for idx, pos in enumerate(df['position']):
            if pd.isna(pos) or str(pos).strip().lower() not in ['above', 'below']:
                df.loc[df.index[idx], 'position'] = 'above' if idx % 2 == 0 else 'below'
            else:
                df.loc[df.index[idx], 'position'] = str(pos).strip().lower()

    return df


def create_timeline(df, config, output_path):
    """Create timeline visualization and save as PNG"""

    # Extract configuration
    dims = config['dimensions']
    colors = config['colors']
    fonts = config['fonts']
    visual = config['visual']

    # Create figure
    fig, ax = plt.subplots(figsize=(dims['width'], dims['height']), dpi=dims['dpi'])
    fig.patch.set_facecolor(colors['background'])
    ax.set_facecolor(colors['background'])

    # Set up the plot - convert dates to numeric format
    dates = df['parsed_date'].tolist()
    min_date = min(dates)
    max_date = max(dates)

    # Convert to numeric dates for matplotlib
    dates_numeric = [mdates.date2num(d) for d in dates]
    min_date_num = mdates.date2num(min_date)
    max_date_num = mdates.date2num(max_date)

    # Add some padding to the date range
    date_range = max_date_num - min_date_num
    padding = max(date_range * 0.05, 1)  # 5% padding

    # Draw main timeline line
    ax.plot([min_date_num, max_date_num], [0, 0],
            color=colors['timeline_line'],
            linewidth=visual['timeline_line_width'],
            zorder=1)

    # Plot each event
    for idx, row in df.iterrows():
        date = row['parsed_date']
        date_num = mdates.date2num(date)
        name = row['name']
        position = row['position']

        # Determine y-position and color
        if position == 'above':
            y_pos = visual['vertical_spacing']
            color = colors['above_items']
            va = 'bottom'
            y_text = y_pos + 0.1
        else:
            y_pos = -visual['vertical_spacing']
            color = colors['below_items']
            va = 'top'
            y_text = y_pos - 0.1

        # Draw connector line from timeline to marker
        ax.plot([date_num, date_num], [0, y_pos],
                color=color,
                linewidth=visual['connector_line_width'],
                alpha=0.6,
                zorder=2)

        # Draw marker using scatter
        ax.scatter(date_num, y_pos,
                  s=visual['marker_size']**2,
                  color=color,
                  zorder=3,
                  edgecolors='white',
                  linewidths=1)

        # Add label
        ax.text(date_num, y_text, name,
                ha='center',
                va=va,
                fontsize=fonts['label_size'],
                fontfamily=fonts['family'],
                color=colors['text'],
                wrap=True,
                zorder=4)

        # Add date below timeline marker
        date_str = date.strftime(visual['date_format_display'])
        date_y = -0.15 if position == 'above' else 0.15
        ax.text(date_num, date_y, date_str,
                ha='center',
                va='top' if position == 'above' else 'bottom',
                fontsize=fonts['date_size'],
                fontfamily=fonts['family'],
                color=colors['date_text'],
                style='italic',
                zorder=4)

    # Configure axes
    ax.set_xlim(min_date_num - padding, max_date_num + padding)
    ax.set_ylim(-visual['vertical_spacing'] - 0.8,
                visual['vertical_spacing'] + 0.8)

    # Format x-axis to show dates
    ax.xaxis.set_major_formatter(mdates.DateFormatter(visual['date_format_display']))
    ax.xaxis.set_major_locator(mdates.AutoDateLocator())
    plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha='right')

    # Remove y-axis
    ax.yaxis.set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
    ax.spines['bottom'].set_visible(False)

    # Adjust layout
    plt.subplots_adjust(left=dims['margin_left']/dims['width'],
                       right=1-dims['margin_right']/dims['width'],
                       top=1-dims['margin_top']/dims['height'],
                       bottom=dims['margin_bottom']/dims['height'])

    # Save figure
    plt.savefig(output_path,
                dpi=dims['dpi'],
                bbox_inches='tight',
                facecolor=colors['background'])
    plt.close()

    print(f"Timeline successfully created: {output_path}")


def main():
    """Main entry point"""
    if len(sys.argv) < 3:
        print("Usage: python timeline_generator.py <input.csv> <output.png> [config.json]")
        print("\nInput CSV format:")
        print("  Required columns: name, date")
        print("  Optional column: position (values: 'above' or 'below')")
        print("  Date format: DD.MM.YYYY (e.g., 15.03.2024)")
        print("\nExample:")
        print("  python timeline_generator.py events.csv timeline.png")
        print("  python timeline_generator.py events.csv timeline.png custom_config.json")
        sys.exit(1)

    input_csv = sys.argv[1]
    output_png = sys.argv[2]
    config_file = sys.argv[3] if len(sys.argv) > 3 else "config.json"

    try:
        # Load configuration
        config = load_config(config_file)

        # Load and process data
        print(f"Loading timeline data from: {input_csv}")
        df = load_timeline_data(input_csv)
        print(f"Loaded {len(df)} events")

        # Create timeline
        print(f"Generating timeline...")
        create_timeline(df, config, output_png)

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

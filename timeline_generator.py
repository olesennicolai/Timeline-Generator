#!/usr/bin/env python3
"""
Timeline Generator - Creates horizontal timeline visualizations from CSV data
Exports as PNG with customizable styling options
"""

import sys
import json
from datetime import datetime
from dateutil.relativedelta import relativedelta
from pathlib import Path

import pandas as pd
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend for web/server usage
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
                  "text": "#2C3E50", "date_text": "#7F8C8D",
                  "month_boundary": "#2C3E50", "month_label": "#2C3E50",
                  "year_label": "#2C3E50", "year_box_fill": "#FFFFFF",
                  "year_box_outline": "#2C3E50", "marker_outline": "#FFFFFF"},
        "fonts": {"family": "sans-serif", "title_size": 16, "label_size": 10, "date_size": 8,
                 "month_label_size": 8, "year_label_size": 10,
                 "label_bold": False, "label_italic": False,
                 "date_bold": False, "date_italic": False,
                 "month_label_bold": False, "year_label_bold": True},
        "visual": {"timeline_line_width": 2, "marker_size": 10, "connector_line_width": 1,
                  "connector_line_alpha": 0.6, "vertical_spacing": 0.8,
                  "date_format_display": "%d.%m.%Y", "month_boundary_width": 0.5,
                  "month_boundary_alpha": 0.3, "month_boundary_style": "--",
                  "month_label_offset": 0.08, "month_label_alpha": 0.7,
                  "month_tick_height": 0.1, "show_dates": True, "year_box_padding": 0.3, "year_box_linewidth": 1.5,
                  "marker_outline_width": 1, "event_label_offset": 0.1,
                  "event_date_offset": 0.15}
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


def check_overlap(bbox1, bbox2, padding=0.05):
    """Check if two bounding boxes overlap with optional padding"""
    return not (bbox1.x1 + padding < bbox2.x0 or
                bbox1.x0 > bbox2.x1 + padding or
                bbox1.y1 + padding < bbox2.y0 or
                bbox1.y0 > bbox2.y1 + padding)


def adjust_label_positions(ax, fig, label_data, visual, colors):
    """
    Adjust label positions to prevent overlaps using a middle-out stacking approach.
    Labels can swap between above/below positions if needed.

    Args:
        ax: matplotlib axes object
        fig: matplotlib figure object
        label_data: list of dicts with keys: text_obj, date_num, original_y, position, name, color
        visual: visual configuration dict
        colors: colors configuration dict

    Returns:
        max_y_extent: maximum y-coordinate used (for adjusting axis limits)
    """
    if not label_data:
        return visual['vertical_spacing'] + 0.8

    # Render to get bounding boxes
    fig.canvas.draw()

    # Get bounding boxes in data coordinates
    for item in label_data:
        bbox_display = item['text_obj'].get_window_extent(renderer=fig.canvas.get_renderer())
        item['bbox'] = bbox_display.transformed(ax.transData.inverted())
        item['current_y'] = item['original_y']
        item['final_position'] = item['position']  # Track if swapped

    # Sort by date to find middle event
    sorted_labels = sorted(label_data, key=lambda x: x['date_num'])
    middle_idx = len(sorted_labels) // 2

    # Mark middle event as positioned
    sorted_labels[middle_idx]['positioned'] = True

    # Stack spacing
    stack_increment = 0.2
    collision_padding = 0.05

    # Process events outward from middle
    max_y_extent = abs(visual['vertical_spacing']) + 0.8

    def find_non_overlapping_position(label, positioned_labels, start_y, is_above):
        """Find a y-position where label doesn't overlap with any positioned labels"""
        current_y = start_y
        max_attempts = 10

        for attempt in range(max_attempts):
            # Update label position temporarily
            label['text_obj'].set_position((label['date_num'], current_y))
            fig.canvas.draw()
            bbox_display = label['text_obj'].get_window_extent(renderer=fig.canvas.get_renderer())
            test_bbox = bbox_display.transformed(ax.transData.inverted())

            # Check for overlaps
            has_overlap = False
            for other in positioned_labels:
                if other is label:
                    continue
                if check_overlap(test_bbox, other['bbox'], collision_padding):
                    has_overlap = True
                    break

            if not has_overlap:
                # Found a good position
                label['bbox'] = test_bbox
                label['current_y'] = current_y
                return current_y, is_above

            # Try next stack level
            if is_above:
                current_y += stack_increment
            else:
                current_y -= stack_increment

            # After 3 attempts on same side, try opposite side
            if attempt == 3:
                is_above = not is_above
                if is_above:
                    current_y = visual['vertical_spacing'] + visual['event_label_offset']
                else:
                    current_y = -visual['vertical_spacing'] - visual['event_label_offset']

        # Fallback: use last attempted position
        label['bbox'] = test_bbox
        label['current_y'] = current_y
        return current_y, is_above

    # Process labels before middle (going backward)
    positioned = [sorted_labels[middle_idx]]
    for i in range(middle_idx - 1, -1, -1):
        label = sorted_labels[i]
        is_above = label['position'] == 'above'
        start_y = label['original_y']

        new_y, new_side = find_non_overlapping_position(label, positioned, start_y, is_above)
        label['current_y'] = new_y
        label['final_position'] = 'above' if new_side else 'below'
        label['positioned'] = True
        positioned.append(label)
        max_y_extent = max(max_y_extent, abs(new_y) + 0.3)

    # Process labels after middle (going forward)
    for i in range(middle_idx + 1, len(sorted_labels)):
        label = sorted_labels[i]
        is_above = label['position'] == 'above'
        start_y = label['original_y']

        new_y, new_side = find_non_overlapping_position(label, positioned, start_y, is_above)
        label['current_y'] = new_y
        label['final_position'] = 'above' if new_side else 'below'
        label['positioned'] = True
        positioned.append(label)
        max_y_extent = max(max_y_extent, abs(new_y) + 0.3)

    return max_y_extent


def create_timeline(df, config, output_path):
    """Create timeline visualization and save as PNG"""

    # Extract configuration
    dims = config['dimensions']
    colors = config['colors']
    fonts = config['fonts']
    visual = config['visual']

    # Create figure
    fig, ax = plt.subplots(figsize=(dims['width'], dims['height']), dpi=dims['dpi'])
    fig.patch.set_facecolor('none')
    ax.set_facecolor('none')

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

    # Add month names and year labels on the timeline
    # Generate month boundaries from min_date to max_date
    current_date = datetime(min_date.year, min_date.month, 1)
    last_year = None

    while current_date <= max_date:
        month_start_num = mdates.date2num(current_date)
        next_month = current_date + relativedelta(months=1)
        month_end_num = mdates.date2num(next_month)

        # Check if we're within the visible range
        if month_start_num >= min_date_num - padding and month_start_num <= max_date_num + padding:
            # Draw tick mark at month boundary (small vertical line on timeline)
            tick_height = visual.get('month_tick_height', 0.1)  # Height of tick mark above and below timeline
            ax.plot([month_start_num, month_start_num],
                   [-tick_height, tick_height],
                   color=colors['month_boundary'],
                   linewidth=visual['month_boundary_width'],
                   alpha=visual['month_boundary_alpha'],
                   linestyle='-',  # Solid line for tick marks
                   zorder=0)

            # Calculate center of the month for label placement
            month_center_num = (month_start_num + month_end_num) / 2

            # Check if this is a new year
            if last_year is None or current_date.year != last_year:
                # Add year label on the timeline
                year_weight = 'bold' if fonts.get('year_label_bold', True) else 'normal'
                ax.text(month_start_num, 0, f' {current_date.year} ',
                       ha='left',
                       va='center',
                       fontsize=fonts['year_label_size'],
                       fontfamily=fonts['family'],
                       color=colors['year_label'],
                       fontweight=year_weight,
                       bbox=dict(boxstyle=f'round,pad={visual["year_box_padding"]}',
                                facecolor=colors['year_box_fill'],
                                edgecolor=colors['year_box_outline'],
                                linewidth=visual['year_box_linewidth']),
                       zorder=5)
                last_year = current_date.year

            # Add month name above the timeline (centered in the month)
            if month_center_num >= min_date_num - padding and month_center_num <= max_date_num + padding:
                month_name = current_date.strftime('%b')  # Abbreviated month name
                month_weight = 'bold' if fonts.get('month_label_bold', False) else 'normal'
                ax.text(month_center_num, visual['month_label_offset'],
                       month_name,
                       ha='center',
                       va='bottom',
                       fontsize=fonts['month_label_size'],
                       fontfamily=fonts['family'],
                       color=colors['month_label'],
                       fontweight=month_weight,
                       alpha=visual['month_label_alpha'],
                       zorder=5)

        # Move to next month
        current_date = next_month

    # First pass: Create markers and store event data for labels
    label_data = []
    event_markers = []

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
            y_text = y_pos + visual['event_label_offset']
        else:
            y_pos = -visual['vertical_spacing']
            color = colors['below_items']
            va = 'top'
            y_text = y_pos - visual['event_label_offset']

        # Draw marker using scatter (will be repositioned later)
        marker = ax.scatter(date_num, y_pos,
                           s=visual['marker_size']**2,
                           color=color,
                           zorder=3,
                           edgecolors=colors['marker_outline'],
                           linewidths=visual['marker_outline_width'])

        # Create label (but don't finalize position yet)
        label_weight = 'bold' if fonts.get('label_bold', False) else 'normal'
        label_style = 'italic' if fonts.get('label_italic', False) else 'normal'
        text_obj = ax.text(date_num, y_text, name,
                          ha='center',
                          va=va,
                          fontsize=fonts['label_size'],
                          fontfamily=fonts['family'],
                          color=colors['text'],
                          fontweight=label_weight,
                          style=label_style,
                          wrap=True,
                          zorder=4)

        # Store label data for collision detection
        label_data.append({
            'text_obj': text_obj,
            'date_num': date_num,
            'original_y': y_text,
            'marker_y': y_pos,
            'position': position,
            'name': name,
            'color': color,
            'va': va,
            'marker_obj': marker
        })

        # Store marker data
        event_markers.append({
            'date_num': date_num,
            'marker_y': y_pos,
            'color': color,
            'marker_obj': marker
        })

        # Add date below timeline marker (if enabled)
        if visual.get('show_dates', True):
            date_str = date.strftime(visual['date_format_display'])
            date_y = -visual['event_date_offset'] if position == 'above' else visual['event_date_offset']
            date_weight = 'bold' if fonts.get('date_bold', False) else 'normal'
            date_style = 'italic' if fonts.get('date_italic', False) else 'normal'
            ax.text(date_num, date_y, date_str,
                    ha='center',
                    va='top' if position == 'above' else 'bottom',
                    fontsize=fonts['date_size'],
                    fontfamily=fonts['family'],
                    color=colors['date_text'],
                    fontweight=date_weight,
                    style=date_style,
                    zorder=4)

    # Adjust label positions to prevent overlaps
    max_y_extent = adjust_label_positions(ax, fig, label_data, visual, colors)

    # Second pass: Update marker positions and draw connector lines with adjusted positions
    for label_info in label_data:
        date_num = label_info['date_num']
        label_y = label_info['current_y']
        color = label_info['color']
        marker_obj = label_info['marker_obj']

        # Calculate marker position (at the end of the connector line, just before label)
        if label_y > 0:
            # Label is above timeline
            marker_y = label_y - visual['event_label_offset']
        else:
            # Label is below timeline
            marker_y = label_y + visual['event_label_offset']

        # Update marker position
        marker_obj.set_offsets([[date_num, marker_y]])

        # Draw single connector line from timeline to marker
        ax.plot([date_num, date_num], [0, marker_y],
                color=color,
                linewidth=visual['connector_line_width'],
                alpha=visual['connector_line_alpha'],
                zorder=2)

    # Configure axes with dynamic y-limits based on label stacking
    ax.set_xlim(min_date_num - padding, max_date_num + padding)
    ax.set_ylim(-max_y_extent, max_y_extent)

    # Hide all axes (month/year labels are on the timeline itself)
    ax.xaxis.set_visible(False)
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
                transparent=True)
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

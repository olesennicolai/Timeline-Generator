# Timeline Generator

A Python tool for creating beautiful horizontal timeline visualizations from CSV data, with customizable styling and PNG export.

## Features

- **Horizontal timeline layout** with events above and below the line
- **European date format** support (DD.MM.YYYY)
- **Smart positioning**: Manual control via CSV or automatic alternating
- **Fully customizable styling** through JSON configuration
- **High-quality PNG export** with configurable DPI
- **Simple command-line interface**

## Installation

1. Install Python dependencies:

```bash
pip install -r requirements.txt
```

## Quick Start

### Basic Usage

```bash
python timeline_generator.py example_timeline.csv output.png
```

### With Custom Configuration

```bash
python timeline_generator.py my_events.csv my_timeline.png custom_config.json
```

## CSV Format

Your input CSV file should have the following columns:

### Required Columns

- **name**: The event name/label (string)
- **date**: The event date in DD.MM.YYYY format (e.g., 15.03.2024)

### Optional Columns

- **position**: Placement on timeline - either "above" or "below"
  - If not specified or empty, events will alternate automatically

### Example CSV

```csv
name,date,position
Project Kickoff,01.01.2024,above
Initial Research,15.01.2024,below
Prototype Complete,01.02.2024,above
User Testing,14.02.2024,below
Beta Release,01.03.2024,above
```

See `example_timeline.csv` for a complete example.

## Customization

### Configuration File

The `config.json` file controls all visual aspects of the timeline. Here's what you can customize:

#### Dimensions

```json
"dimensions": {
  "width": 16,           // Figure width in inches
  "height": 10,          // Figure height in inches
  "dpi": 300,            // Resolution (higher = better quality)
  "margin_left": 1.0,    // Left margin in inches
  "margin_right": 1.0,   // Right margin in inches
  "margin_top": 1.5,     // Top margin in inches
  "margin_bottom": 1.5   // Bottom margin in inches
}
```

#### Colors

```json
"colors": {
  "background": "#FFFFFF",      // Background color
  "timeline_line": "#2C3E50",   // Main timeline line
  "above_items": "#3498DB",     // Color for items above the line
  "below_items": "#E74C3C",     // Color for items below the line
  "text": "#2C3E50",            // Event label text color
  "date_text": "#7F8C8D"        // Date text color
}
```

#### Fonts

```json
"fonts": {
  "family": "sans-serif",  // Font family
  "title_size": 16,        // Title font size
  "label_size": 10,        // Event label font size
  "date_size": 8           // Date font size
}
```

#### Visual Elements

```json
"visual": {
  "timeline_line_width": 2,      // Thickness of main timeline
  "marker_size": 10,             // Size of event markers
  "connector_line_width": 1,     // Line connecting marker to timeline
  "vertical_spacing": 0.8,       // Vertical distance from timeline
  "date_format_display": "%d.%m.%Y"  // Display format for dates
}
```

### Creating Custom Color Schemes

You can create multiple configuration files for different styles:

```bash
python timeline_generator.py events.csv timeline_blue.png config_blue.json
python timeline_generator.py events.csv timeline_dark.png config_dark.json
```

## Examples

### Generate Timeline from Example Data

```bash
python timeline_generator.py example_timeline.csv my_first_timeline.png
```

### Using Automatic Alternating Positions

Create a CSV with just `name` and `date` columns - positions will alternate automatically:

```csv
name,date
Event 1,01.01.2024
Event 2,15.01.2024
Event 3,01.02.2024
```

### Manual Position Control

Specify exactly where each event should appear:

```csv
name,date,position
Important Milestone,01.01.2024,above
Background Task,01.01.2024,below
Another Milestone,15.01.2024,above
```

## Troubleshooting

### Date Format Errors

Make sure your dates are in DD.MM.YYYY format:
- ✅ Correct: `15.03.2024`
- ❌ Wrong: `03/15/2024`, `2024-03-15`, `15-03-2024`

### Missing Columns Error

Ensure your CSV has at minimum `name` and `date` columns. Column names are case-sensitive.

### Color Not Working

Colors must be in hex format (e.g., `#FF0000` for red) or standard color names (e.g., `red`, `blue`).

## Dependencies

- **matplotlib** >= 3.7.0 - For plotting and rendering
- **pandas** >= 2.0.0 - For CSV data handling
- **Pillow** >= 10.0.0 - For PNG image processing

## License

MIT License - Feel free to use and modify as needed.

## Tips

1. **High-resolution output**: Increase the `dpi` value in config.json for print-quality images
2. **Long event names**: They will automatically wrap, but consider abbreviating for cleaner visuals
3. **Many events**: Increase the `width` dimension for crowded timelines
4. **Date spacing**: The tool automatically adds padding around your date range for better visibility

# Timeline Generator Web UI

A beautiful, interactive web interface for creating and customizing timeline visualizations.

## Features

- **Live Preview**: See your timeline update in real-time as you make changes
- **Event Editor**: Add, edit, and remove events with a simple interface
- **Configuration Panel**: Customize colors, fonts, dimensions, and visual properties
- **Auto-Save**: All changes are automatically saved to files
- **Multiple Export Formats**: Export as PNG, CSV, or JSON
- **Default Timeline**: Boots up with example_timeline.csv by default
- **European date format** support (DD.MM.YYYY)
- **Smart positioning**: Manual control via CSV or automatic alternating

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

1. Start the web application:
```bash
python app.py
```

2. Open your browser to: http://localhost:5000

3. The interface will load with the example_timeline.csv by default

## Interface Overview

### Events Tab
- View all timeline events in an editable list
- Each event has:
  - **Name**: Event title
  - **Date**: Date in DD.MM.YYYY format
  - **Position**: Above or below the timeline
- Click **+ Add Event** to add new events
- Click **×** on any event to remove it
- Changes are saved automatically and update the preview

### Configuration Tab
Organized into sections:

- **Dimensions**: Width, height, DPI, and margins
- **Colors**: Customize all colors (timeline, events, text, etc.)
- **Fonts**: Font family and sizes
- **Visual**: Line widths, marker sizes, spacing, etc.

All configuration changes are saved automatically to `config.json`

### Preview Panel
- Shows live preview of your timeline
- Click **Update Preview** to regenerate
- Export buttons:
  - **Export PNG**: Download high-resolution timeline image
  - **Export CSV**: Download event data
  - **Export JSON**: Download complete configuration and data

## File Structure

```
SwissGrants/
├── app.py                    # Flask web application
├── timeline_generator.py     # Core timeline generation logic
├── config.json              # Timeline configuration
├── example_timeline.csv     # Default timeline data
├── templates/
│   └── index.html          # Web UI
├── static/
│   └── preview.png         # Generated preview image
└── requirements.txt        # Python dependencies
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

## Command Line Usage

You can still use the original command-line interface:

### Basic Usage

```bash
python timeline_generator.py example_timeline.csv output.png
```

### With Custom Configuration

```bash
python timeline_generator.py my_events.csv my_timeline.png custom_config.json
```

## Tips

- Changes to events or configuration automatically trigger a preview update after saving
- Use DD.MM.YYYY format for dates (e.g., 15.03.2024)
- Color inputs support hex colors for precise color selection
- The application saves all changes to the actual config.json and CSV files
- Preview updates may take a moment to generate for complex timelines
- **High-resolution output**: Increase the `dpi` value in config.json for print-quality images
- **Long event names**: They will automatically wrap, but consider abbreviating for cleaner visuals
- **Many events**: Increase the `width` dimension for crowded timelines

## Troubleshooting

### Preview not updating?
- Ensure all events have valid names and dates in DD.MM.YYYY format
- Check the browser console for errors

### Can't see the preview?
- Click "Update Preview" button
- Make sure you have at least one valid event with a name and date

### Date Format Errors

Make sure your dates are in DD.MM.YYYY format:
- Correct: `15.03.2024`
- Wrong: `03/15/2024`, `2024-03-15`, `15-03-2024`

### Missing Columns Error

Ensure your CSV has at minimum `name` and `date` columns. Column names are case-sensitive.

### Color Not Working

Colors must be in hex format (e.g., `#FF0000` for red) or standard color names (e.g., `red`, `blue`).

## Dependencies

- **matplotlib** >= 3.7.0 - For plotting and rendering
- **pandas** >= 2.0.0 - For CSV data handling
- **Pillow** >= 10.0.0 - For PNG image processing
- **Flask** - For web interface

## License

MIT License - Feel free to use and modify as needed.

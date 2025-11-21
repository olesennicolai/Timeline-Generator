# Timeline Generator Web UI

A beautiful, interactive web interface for creating and customizing timeline visualizations.

## Features

- **Live Preview**: See your timeline update in real-time as you make changes
- **Event Editor**: Add, edit, and remove events with a simple interface
- **Configuration Panel**: Customize colors, fonts, dimensions, and visual properties
- **Auto-Save**: All changes are automatically saved to files
- **Multiple Export Formats**: Export as PNG, CSV, or JSON
- **Default Timeline**: Boots up with example_timeline.csv by default

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

## Tips

- Changes to events or configuration automatically trigger a preview update after saving
- Use DD.MM.YYYY format for dates (e.g., 15.03.2024)
- Color inputs support hex colors for precise color selection
- The application saves all changes to the actual config.json and CSV files
- Preview updates may take a moment to generate for complex timelines

## Troubleshooting

**Preview not updating?**
- Ensure all events have valid names and dates in DD.MM.YYYY format
- Check the browser console for errors

**Can't see the preview?**
- Click "Update Preview" button
- Make sure you have at least one valid event with a name and date

**Dates not working?**
- Use the European date format: DD.MM.YYYY (e.g., 01.04.2024)
- Make sure the day, month, and year are valid

## Command Line Usage

You can still use the original command-line interface:

```bash
python timeline_generator.py example_timeline.csv output.png
```

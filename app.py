#!/usr/bin/env python3
"""
Timeline Generator Web UI - Flask application for interactive timeline creation
"""

import os
import json
import io
import base64
from datetime import datetime
from pathlib import Path

from flask import Flask, render_template, request, jsonify, send_file
import pandas as pd

from timeline_generator import (
    load_config,
    load_timeline_data,
    create_timeline,
    parse_european_date
)

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Default paths
CONFIG_PATH = 'config.json'
DEFAULT_CSV = 'example_timeline.csv'
PREVIEW_PATH = 'static/preview.png'

# Ensure static directory exists
os.makedirs('static', exist_ok=True)


@app.route('/')
def index():
    """Main page"""
    return render_template('index.html')


@app.route('/api/config', methods=['GET'])
def get_config():
    """Get current configuration"""
    try:
        config = load_config(CONFIG_PATH)
        return jsonify({'success': True, 'config': config})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/config', methods=['POST'])
def update_config():
    """Update configuration and save to file"""
    try:
        config = request.json

        # Save to config.json
        with open(CONFIG_PATH, 'w') as f:
            json.dump(config, f, indent=2)

        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/csv', methods=['GET'])
def get_csv_data():
    """Get current CSV data"""
    try:
        csv_file = request.args.get('file', DEFAULT_CSV)

        if not os.path.exists(csv_file):
            return jsonify({'success': False, 'error': 'CSV file not found'}), 404

        df = pd.read_csv(csv_file)

        # Convert to list of dicts
        data = df.to_dict('records')

        return jsonify({'success': True, 'data': data, 'file': csv_file})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/csv', methods=['POST'])
def update_csv_data():
    """Update CSV data and save to file"""
    try:
        data = request.json.get('data', [])
        csv_file = request.json.get('file', DEFAULT_CSV)

        # Convert to DataFrame
        df = pd.DataFrame(data)

        # Ensure required columns
        if 'name' not in df.columns:
            df['name'] = ''
        if 'date' not in df.columns:
            df['date'] = ''
        if 'position' not in df.columns:
            df['position'] = ''

        # Save to CSV
        df.to_csv(csv_file, index=False)

        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/preview', methods=['POST'])
def generate_preview():
    """Generate timeline preview"""
    try:
        data = request.json.get('data', [])
        config = request.json.get('config')

        # Create temporary CSV from data
        temp_csv = 'temp_preview.csv'
        df = pd.DataFrame(data)

        # Ensure required columns
        if df.empty or 'name' not in df.columns or 'date' not in df.columns:
            return jsonify({
                'success': False,
                'error': 'Invalid data: must have name and date columns'
            }), 400

        # Filter out empty rows
        df = df[df['name'].notna() & (df['name'] != '') &
                df['date'].notna() & (df['date'] != '')]

        if df.empty:
            return jsonify({
                'success': False,
                'error': 'No valid events to display'
            }), 400

        df.to_csv(temp_csv, index=False)

        # Load the data properly
        df_loaded = load_timeline_data(temp_csv)

        # Generate timeline
        create_timeline(df_loaded, config, PREVIEW_PATH)

        # Clean up temp file
        if os.path.exists(temp_csv):
            os.remove(temp_csv)

        # Return success with timestamp to force reload
        return jsonify({
            'success': True,
            'preview_url': f'/static/preview.png?t={datetime.now().timestamp()}'
        })
    except Exception as e:
        # Clean up temp file on error
        if os.path.exists('temp_preview.csv'):
            os.remove('temp_preview.csv')
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/export/<format>', methods=['POST'])
def export_timeline(format):
    """Export timeline in various formats"""
    try:
        data = request.json.get('data', [])
        config = request.json.get('config')

        if format == 'png':
            # Create temporary CSV
            temp_csv = 'temp_export.csv'
            df = pd.DataFrame(data)

            # Filter out empty rows
            df = df[df['name'].notna() & (df['name'] != '') &
                    df['date'].notna() & (df['date'] != '')]

            df.to_csv(temp_csv, index=False)

            # Load and generate timeline
            df_loaded = load_timeline_data(temp_csv)
            output_path = 'static/export_timeline.png'
            create_timeline(df_loaded, config, output_path)

            # Clean up
            if os.path.exists(temp_csv):
                os.remove(temp_csv)

            return send_file(
                output_path,
                mimetype='image/png',
                as_attachment=True,
                download_name='timeline.png'
            )

        elif format == 'csv':
            # Export as CSV
            df = pd.DataFrame(data)
            output = io.StringIO()
            df.to_csv(output, index=False)
            output.seek(0)

            return send_file(
                io.BytesIO(output.getvalue().encode()),
                mimetype='text/csv',
                as_attachment=True,
                download_name='timeline_data.csv'
            )

        elif format == 'json':
            # Export config and data as JSON
            export_data = {
                'config': config,
                'events': data
            }

            return send_file(
                io.BytesIO(json.dumps(export_data, indent=2).encode()),
                mimetype='application/json',
                as_attachment=True,
                download_name='timeline_export.json'
            )

        else:
            return jsonify({'success': False, 'error': 'Unsupported format'}), 400

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/import/csv', methods=['POST'])
def import_csv():
    """Import a CSV file and return parsed event data"""
    try:
        if 'file' not in request.files:
            return jsonify({'success': False, 'error': 'No file provided'}), 400

        file = request.files['file']
        if file.filename == '':
            return jsonify({'success': False, 'error': 'No file selected'}), 400

        if not file.filename.lower().endswith('.csv'):
            return jsonify({'success': False, 'error': 'File must be a CSV'}), 400

        df = pd.read_csv(io.StringIO(file.stream.read().decode('utf-8')))

        if 'name' not in df.columns or 'date' not in df.columns:
            return jsonify({'success': False, 'error': 'CSV must have "name" and "date" columns'}), 400

        data = df.to_dict('records')
        return jsonify({'success': True, 'data': data})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/files', methods=['GET'])
def list_csv_files():
    """List available CSV files"""
    try:
        csv_files = [f for f in os.listdir('.') if f.endswith('.csv')]
        return jsonify({'success': True, 'files': csv_files})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


if __name__ == '__main__':
    print("Starting Timeline Generator Web UI...")
    print("Open your browser to: http://localhost:5001")
    app.run(debug=True, host='0.0.0.0', port=5001)

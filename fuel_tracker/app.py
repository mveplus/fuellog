import os
from flask import Flask, request, jsonify, render_template, send_file
import json
import csv
from datetime import datetime
import shutil

app = Flask(__name__)

# Set the base directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DATA_FILE = os.path.join(BASE_DIR, 'data.json')
BACKUP_FILE = os.path.join(BASE_DIR, 'backup.json')


def load_data():
    try:
        with open(DATA_FILE, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return []


def save_data(data, backup=True):
    if backup:
        shutil.copyfile(DATA_FILE, BACKUP_FILE)
    with open(DATA_FILE, 'w') as file:
        json.dump(data, file, indent=4)


def load_backup():
    try:
        with open(BACKUP_FILE, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return []


def calculate_mpg(last_entry, new_entry):
    distance = new_entry['odometer'] - last_entry['odometer']
    gallons = new_entry['fuel'] * 0.264172  # convert liters to gallons
    mpg = distance / gallons if gallons != 0 else 0
    return mpg


def calculate_total_fuel(data):
    return sum(entry['fuel'] for entry in data)


def calculate_predicted_mpg(data):
    if not data:
        return 0
    total_distance = 0
    total_gallons = 0
    for i in range(1, len(data)):
        distance = data[i]['odometer'] - data[i-1]['odometer']
        gallons = data[i]['fuel'] * 0.264172  # convert liters to gallons
        total_distance += distance
        total_gallons += gallons
    return total_distance / total_gallons if total_gallons != 0 else 0


@app.route('/')
def index():
    data = load_data()
    current_datetime = datetime.now().strftime('%Y-%m-%dT%H:%M')
    return render_template('index.html', current_datetime=current_datetime, entries=data)


@app.route('/add', methods=['POST'])
def add_entry():
    data = load_data()
    date = request.form.get('date')
    if not date:
        date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    else:
        date = datetime.strptime(date, '%Y-%m-%dT%H:%M').strftime('%Y-%m-%d %H:%M:%S')

    fuel_price = request.form['fuel_price']
    if '.' in fuel_price:
        fuel_price = float(fuel_price)
    else:
        fuel_price = int(fuel_price) / 1000  # Convert to decimal

    new_entry = {
        'date': date,
        'odometer': float(request.form['odometer']),
        'fuel_price': fuel_price,
        'fuel': float(request.form['fuel']),
        'total_fuel_price': round(fuel_price * float(request.form['fuel']), 2)
    }

    if data:
        last_entry = data[-1]
        new_entry['mpg'] = round(calculate_mpg(last_entry, new_entry), 2)
    else:
        new_entry['mpg'] = 0

    data.append(new_entry)
    total_fuel = calculate_total_fuel(data)
    predicted_mpg = round(calculate_predicted_mpg(data), 2)
    new_entry['total_fuel'] = total_fuel
    new_entry['predicted_mpg'] = predicted_mpg
    save_data(data)
    return jsonify(new_entry)


@app.route('/delete', methods=['POST'])
def delete_entries():
    data = load_data()
    indices = request.json.get('indices', [])
    if indices:
        for index in sorted(indices, reverse=True):
            if 0 <= index < len(data):
                del data[index]
        save_data(data)
        return jsonify({'success': True})
    return jsonify({'success': False}), 404


@app.route('/edit/<int:index>', methods=['POST'])
def edit_entry(index):
    data = load_data()
    if 0 <= index < len(data):
        entry = data[index]
        date = request.form.get('date')
        if not date:
            date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        else:
            date = datetime.strptime(date, '%Y-%m-%dT%H:%M').strftime('%Y-%m-%d %H:%M:%S')

        fuel_price = request.form['fuel_price']
        if '.' in fuel_price:
            fuel_price = float(fuel_price)
        else:
            fuel_price = int(fuel_price) / 1000  # Convert to decimal

        entry.update({
            'date': date,
            'odometer': float(request.form['odometer']),
            'fuel_price': fuel_price,
            'fuel': float(request.form['fuel']),
            'total_fuel_price': round(fuel_price * float(request.form['fuel']), 2)
        })

        if index > 0:
            last_entry = data[index - 1]
            entry['mpg'] = round(calculate_mpg(last_entry, entry), 2)
        else:
            entry['mpg'] = 0

        data[index] = entry
        total_fuel = calculate_total_fuel(data)
        predicted_mpg = round(calculate_predicted_mpg(data), 2)
        entry['total_fuel'] = total_fuel
        entry['predicted_mpg'] = predicted_mpg
        save_data(data)
        return jsonify({'success': True})
    return jsonify({'success': False}), 404


@app.route('/export')
def export_data():
    data = load_data()
    with open('data.csv', 'w', newline='') as csvfile:
        fieldnames = ['date', 'odometer', 'fuel_price', 'fuel', 'total_fuel_price']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        for entry in data:
            writer.writerow({
                'date': entry['date'],
                'odometer': entry['odometer'],
                'fuel_price': entry['fuel_price'],
                'fuel': entry['fuel'],
                'total_fuel_price': entry['total_fuel_price']
            })

    return send_file('data.csv', as_attachment=True)


@app.route('/import', methods=['POST'])
def import_data():
    file = request.files['file']
    if file:
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)  # Save the uploaded file to a secure location

        data = load_data()
        with open(filepath, newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                entry = {
                    'date': row['date'],
                    'odometer': float(row['odometer']),
                    'fuel_price': float(row['fuel_price']),
                    'fuel': float(row['fuel']),
                    'total_fuel_price': float(row['total_fuel_price'])
                }
                if data:
                    last_entry = data[-1]
                    entry['mpg'] = calculate_mpg(last_entry, entry)
                else:
                    entry['mpg'] = 0
                data.append(entry)

        total_fuel = calculate_total_fuel(data)
        predicted_mpg = calculate_predicted_mpg(data)
        for entry in data:
            entry['total_fuel'] = total_fuel
            entry['predicted_mpg'] = predicted_mpg

        save_data(data)
        return jsonify({'success': True})

    return jsonify({'success': False, 'error': 'Invalid file format or no file provided'})


@app.route('/restore')
def restore_data():
    backup_data = load_backup()
    save_data(backup_data, backup=False)
    return jsonify({'success': True, 'data': backup_data})


if __name__ == '__main__':
    app.run(debug=True)

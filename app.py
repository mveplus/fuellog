from flask import Flask, request, jsonify, render_template, send_file
import json
import csv
from datetime import datetime

app = Flask(__name__)

DATA_FILE = 'data.json'


def load_data():
    try:
        with open(DATA_FILE, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return []


def save_data(data):
    with open(DATA_FILE, 'w') as file:
        json.dump(data, file, indent=4)


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
    current_datetime = datetime.now().strftime('%Y-%m-%dT%H:%M')
    return render_template('index.html', current_datetime=current_datetime)


@app.route('/add', methods=['POST'])
def add_entry():
    data = load_data()
    date = request.form.get('date')
    if not date:
        date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    else:
        date = datetime.strptime(date, '%Y-%m-%dT%H:%M').strftime('%Y-%m-%d %H:%M:%S')
    
    new_entry = {
        'date': date,
        'odometer': float(request.form['odometer']),
        'fuel_price': float(request.form['fuel_price']),
        'fuel': float(request.form['fuel']),
        'total_fuel_price': float(request.form['fuel_price']) * float(request.form['fuel'])
    }

    if data:
        last_entry = data[-1]
        new_entry['mpg'] = calculate_mpg(last_entry, new_entry)
    else:
        new_entry['mpg'] = 0

    data.append(new_entry)
    total_fuel = calculate_total_fuel(data)
    predicted_mpg = calculate_predicted_mpg(data)
    new_entry['total_fuel'] = total_fuel
    new_entry['predicted_mpg'] = predicted_mpg
    save_data(data)
    return jsonify(new_entry)


@app.route('/export')
def export_data():
    data = load_data()
    with open('data.csv', 'w', newline='') as csvfile:
        fieldnames = ['date', 'odometer', 'fuel_price', 'fuel', 'total_fuel_price', 'mpg', 'total_fuel', 'predicted_mpg']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        for entry in data:
            writer.writerow(entry)

    return send_file('data.csv', as_attachment=True)


if __name__ == '__main__':
    app.run(debug=True)

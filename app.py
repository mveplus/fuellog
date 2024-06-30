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
        json.dump(data, file)


def calculate_mpg(last_entry, new_entry):
    distance = new_entry['odometer'] - last_entry['odometer']
    gallons = new_entry['fuel'] * 0.264172  # convert liters to gallons
    mpg = distance / gallons if gallons != 0 else 0
    return mpg


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/add', methods=['POST'])
def add_entry():
    data = load_data()
    new_entry = {
        'date': request.form.get('date', datetime.now().strftime('%Y-%m-%d %H:%M:%S')),
        'odometer': float(request.form['odometer']),
        'fuel_price': float(request.form['fuel_price']),
        'fuel': float(request.form['fuel'])
    }

    if data:
        last_entry = data[-1]
        new_entry['mpg'] = calculate_mpg(last_entry, new_entry)
    else:
        new_entry['mpg'] = 0

    data.append(new_entry)
    save_data(data)
    return jsonify(new_entry)


@app.route('/export')
def export_data():
    data = load_data()
    with open('data.csv', 'w', newline='') as csvfile:
        fieldnames = ['date', 'odometer', 'fuel_price', 'fuel', 'mpg']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        for entry in data:
            writer.writerow(entry)

    return send_file('data.csv', as_attachment=True)


if __name__ == '__main__':
    app.run(debug=True)

from flask import Flask, redirect, url_for, session, jsonify, render_template, request, send_file
from flask_dance.contrib.google import make_google_blueprint, google
from flask_dance.contrib.github import make_github_blueprint, github
from flask_dance.contrib.facebook import make_facebook_blueprint, facebook
import json
import csv
from datetime import datetime
import shutil
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Replace with your own secret key

# OAuth configuration for Google
google_bp = make_google_blueprint(client_id='YOUR_GOOGLE_CLIENT_ID',
                                  client_secret='YOUR_GOOGLE_CLIENT_SECRET',
                                  redirect_to='google_login')
app.register_blueprint(google_bp, url_prefix='/login')

# OAuth configuration for GitHub
github_bp = make_github_blueprint(client_id='YOUR_GITHUB_CLIENT_ID',
                                  client_secret='YOUR_GITHUB_CLIENT_SECRET',
                                  redirect_to='github_login')
app.register_blueprint(github_bp, url_prefix='/login')

# OAuth configuration for Facebook
facebook_bp = make_facebook_blueprint(client_id='YOUR_FACEBOOK_CLIENT_ID',
                                      client_secret='YOUR_FACEBOOK_CLIENT_SECRET',
                                      redirect_to='facebook_login')
app.register_blueprint(facebook_bp, url_prefix='/login')


DATA_FILE = 'data.json'
BACKUP_FILE = 'backup.json'

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
    if not google.authorized and not github.authorized and not facebook.authorized:
        return redirect(url_for('login'))

    data = load_data()
    current_datetime = datetime.now().strftime('%Y-%m-%dT%H:%M')
    return render_template('index.html', current_datetime=current_datetime, entries=data)

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/google')
def google_login():
    if not google.authorized:
        return redirect(url_for('google.login'))
    resp = google.get('/plus/v1/people/me')
    assert resp.ok, resp.text
    return redirect(url_for('index'))

@app.route('/github')
def github_login():
    if not github.authorized:
        return redirect(url_for('github.login'))
    resp = github.get('/user')
    assert resp.ok, resp.text
    return redirect(url_for('index'))

@app.route('/facebook')
def facebook_login():
    if not facebook.authorized:
        return redirect(url_for('facebook.login'))
    resp = facebook.get('/me')
    assert resp.ok, resp.text
    return redirect(url_for('index'))

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
        'total_fuel_price': fuel_price * float(request.form['fuel'])
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
            'total_fuel_price': fuel_price * float(request.form['fuel'])
        })

        if index > 0:
            last_entry = data[index - 1]
            entry['mpg'] = calculate_mpg(last_entry, entry)
        else:
            entry['mpg'] = 0

        data[index] = entry
        total_fuel = calculate_total_fuel(data)
        predicted_mpg = calculate_predicted_mpg(data)
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
    data = load_data()
    reader = csv.DictReader(file.read().decode('utf-8').splitlines())
    for row in reader:
        date = row['date']
        if '.' in row['fuel_price']:
            fuel_price = float(row['fuel_price'])
        else:
            fuel_price = int(row['fuel_price']) / 1000  # Convert to decimal

        new_entry = {
            'date': date,
            'odometer': float(row['odometer']),
            'fuel_price': fuel_price,
            'fuel': float(row['fuel']),
            'total_fuel_price': fuel_price * float(row['fuel'])
        }

        if data:
            last_entry = data[-1]
            new_entry['mpg'] = calculate_mpg(last_entry, new_entry)
        else:
            new_entry['mpg'] = 0

        data.append(new_entry)

    total_fuel = calculate_total_fuel(data)
    predicted_mpg = calculate_predicted_mpg(data)
    for entry in data:
        entry['total_fuel'] = total_fuel
        entry['predicted_mpg'] = predicted_mpg
    save_data(data)
    return jsonify({'success': True})

@app.route('/restore')
def restore_data():
    backup_data = load_backup()
    save_data(backup_data, backup=False)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)


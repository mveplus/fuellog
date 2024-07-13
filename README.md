# Fuel Tracker Web App: Keep Your Tank Full and Data Cool!

> [!IMPORTANT]
> The project state is alfa [unstable]!
> Many things could change and there are a lot of moving parts ;)

1. Flasky Goodness: Our backend’s running on Flask, the web framework for cool cats.
2. JSON Jive: Store your fuel data in a slick JSON file.
3. Responsive Vibes: Looks great on both your massive desktop and your tiny phone.
4. MPG Magic: Calculate fuel economy and total fuel cost with ease.
5. CSV Shuffle: Import/export your data like a pro.
6. Backup Buddy: Automatic backup before any major moves.
7. Tests & Tunes: Some unit tests to keep things in check.
8. Docker Delight: Option to run in Docker for ultimate container coolness.

Features Galore:

    Edit and delete entries with style.
    Confirm deletions (because we're cautious like that).
    Restore data from the last backup with a click.
    Responsive table with checkboxes for easy selection.
    Export and import data to/from CSV.
    Main page shows the input form and your fuel data table in all its glory.

Stay fueled up and on track with this awesome web app!


## Here's a simple project structure:
```bash
/fuel_tracker
|-- app.py
|-- static
|   |-- styles.css
|-- templates
|   |-- index.html
|-- data.json
|-- tests
|   |-- test_app.py
|-- requirements.txt
```

## Running the App and Tests

1. Install virtualenv (if not already installed): `pip install virtualenv`
2. Create a Virtual Environment: 
     ```bash
     cd /path/to/your/project
     virtualenv venv
     ```
3: Activate the Virtual Environment: `source venv/bin/activate` 
4. Install dependencies: `pip install -r requirements.txt`
5. Run the Flask app: `python /fuel_tracker/app.py`
6. Run the unit tests: `python -m unittest discover -s tests`

Once you’re done working in the virtual environment, you can deactivate it: `deactivate`

## MPG

Distance Traveled (miles)Fuel Used (gallons)MPG=Fuel Used (gallons from liters)Distance Traveled (miles)
The MPG is calculated as the distance traveled divided by the amount of fuel used in gallons. Here's the formula:
```
    Odometer reading difference = 1000 - 900 = 100 miles
    Fuel used = 40 liters, which needs to be converted to gallons (1 liter ≈ 0.264172 gallons).
    Fuel Used (gallons)=40×0.264172=10.56688Fuel Used (gallons)=40×0.264172=10.56688
    MPG=10010.56688≈9.4635MPG=10.56688100≈9.4635
```
The value 9.4635 is accurate, updated the test case to match this calculation.

# Build and Run the Docker Container

## Build the Docker image:

```bash
docker build -t fuel_tracker_app .
```

## Run the Docker container:

```bash
 docker run -p 5000:5000 fuel_tracker_app
```

Or with Docker Compose [ optional ]:

```bash
docker-compose up --build
```

## Docker app structure:

```bash

fuel_log_webapp/
├── fuel_tracker/
│   ├── __init__.py
│   ├── app.py
│   ├── templates/
│   │   ├── index.html
│   │   └── login.html
│   ├── static/
│   │   └── style.css
│   └── data.json
├── tests/
│   └── test_app.py
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── README.md

```
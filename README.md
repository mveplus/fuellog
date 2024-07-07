# Simple Fuel tracker Web App
## Project is alfa state.

1. Basic Flask app: Flask will serve as the web framework.
2. A JSON database: Store the data in a JSON file.
3. Responsive web for desktop and mobile, with HTML/CSS/JavaScript:  
4. Basic functions to calculate fuel economy to calculate MPG.
5. Functionality to export data to CSV
6. Auto-save for the JSON database: Save data automatically. 
7. Some unit tests for functions. 

## Here's a simple project structure:


-fuel_tracker
    - app.py
    - static
        - styles.css
    - templates
        - index.html
    - data.json
    - data.csv
    - backup.json
    - tests
       - test_app.py
    - requirements.txt


## Running the App and Tests

1. Install dependencies: pip install -r requirements.txt
2. Run the Flask app: python app.py
3. Run the unit tests: python -m unittest discover -s tests


This setup provides a simple, responsive web application for tracking car fuel consumption and price, calculating fuel economy in MPG, and exporting data to CSV. The application uses Flask for the backend, JSON for data storage, and basic HTML/CSS/JavaScript for the frontend.

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

## Other 
The main landing page displays both the input form and the table containing the fuel data. 
The table will be populated with data from the JSON file, and new entries can be added using the form.
The table will update and display the new data after a form submission.

The application supports editing and deleting entries, confirms deletion, backs up data before deletion or editing, and allows importing and exporting data to/from CSV. 
Additionally, it includes a restore button to revert to the last backup, and displays data in a responsive table with checkboxes for selection.
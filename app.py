# app.py
from flask import Flask, render_template, request, send_file
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import csv
import os

app = Flask(__name__)

# Define vaccination schedule based on weeks or months from DOB
SCHEDULE = [
    ("Hepatitis B", 0, "days"),
    ("Polio (O dose)", 0, "days"),
    ("BCG", 0, "days"),
    ("Polio + Rotavirus + Penta + PCV", 6, "weeks"),
    ("Polio + Rotavirus + Penta + PCV", 10, "weeks"),
    ("Polio + Rotavirus + Penta + PCV", 14, "weeks"),
    ("MR + JE + Vitamin A", 9, "months"),
    ("Vitamin A + DPT + Polio + PCV", 16, "months"),
    ("DPT + Polio booster", 5, "years"),
    ("Td", 10, "years"),
    ("Td", 16, "years")
]

def calculate_schedule(dob):
    today = datetime.today().date()
    result = []
    for vaccine, interval, unit in SCHEDULE:
        if unit == "days":
            due_date = dob
        elif unit == "weeks":
            due_date = dob + timedelta(weeks=interval)
        elif unit == "months":
            due_date = dob + relativedelta(months=interval)
        elif unit == "years":
            due_date = dob + relativedelta(years=interval)
        status = "Upcoming" if due_date > today else "Done"
        result.append({"vaccine": vaccine, "date": due_date.strftime('%d-%b-%Y'), "status": status})
    return result

@app.route('/', methods=['GET', 'POST'])
def index():
    schedule = []
    dob_input = ""
    if request.method == 'POST':
        dob_input = request.form['dob']
        try:
            dob = datetime.strptime(dob_input, '%Y-%m-%d').date()
            schedule = calculate_schedule(dob)
        except ValueError:
            pass
    return render_template('index.html', schedule=schedule, dob=dob_input)

@app.route('/download', methods=['POST'])
def download():
    dob_input = request.form['dob']
    try:
        dob = datetime.strptime(dob_input, '%Y-%m-%d').date()
        schedule = calculate_schedule(dob)
        filepath = 'vaccination_schedule.csv'
        with open(filepath, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['Vaccine', 'Scheduled Date', 'Status'])
            for item in schedule:
                writer.writerow([item['vaccine'], item['date'], item['status']])
        return send_file(filepath, as_attachment=True)
    except ValueError:
        return "Invalid Date Format", 400

if __name__ == '__main__':
    app.run()

# app.py
from flask import Flask , render_template, request, redirect, url_for,jsonify
import sqlite3
from datetime import datetime

app = Flask(__name__)

# Creatng file based database and table

def init_db():
    conn = sqlite3.connect('expenses.db')
    cur = conn.cursor()
    cur.execute('''CREATE TABLE IF NOT EXISTS expense_head
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  description TEXT not null,
                  category TEXT not null,
                  amount REAL not null,
                  date TEXT not null)
                ''')
    conn.commit()
    conn.close()

# show all records from table
@app.route('/')
def index():
    conn = sqlite3.connect('expenses.db')
    cur = conn.cursor()
    cur.execute("SELECT * FROM expense_head order by id asc")
    expenses = cur.fetchall()
    total = sum(expense[3] for expense in expenses)
    conn.close()
    return render_template('index.html', expenses=expenses , title="All Expenses", total=total)

# To add expenses into table
@app.route("/add", methods=["POST"])
def add():
    description = request.form.get("description")
    category = request.form.get("category")
    amount = request.form.get("amount")
    date = request.form.get("date") or datetime.now()

    if description and category and amount and date:
      conn = sqlite3.connect('expenses.db')
      cur = conn.cursor()
      cur.execute("INSERT INTO expense_head (description, category, amount, date) VALUES (?, ?, ?, ?)",
                (description, category, float(amount), date))
      conn.commit()
      conn.close()
    return redirect(url_for('index'))

# To delete expenses from table by expense id
@app.route("/delete/<int:expense_id>")
def delete(expense_id):
    conn = sqlite3.connect('expenses.db')
    cur = conn.cursor()
    cur.execute("DELETE FROM expense_head WHERE id=?", (expense_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

# Filter data by month , by year , by quarter and by custom range
@app.route("/filter", methods=["GET", "POST"])
def filter():
    conn = sqlite3.connect('expenses.db')
    cur = conn.cursor()

    filter_type = request.form.get("type")
    if filter_type == "day":
        today = datetime.now().strftime("%Y-%m-%d")
        cur.execute("SELECT * FROM expense_head WHERE date = ?", (today))
        title = f"Expense for Today: {today}"
    elif filter_type == "month":
        month = datetime.now().strftime("%Y-%m")
        cur.execute("SELECT * FROM expense_head WHERE strftime('%Y-%m', date) = ?", (month))
        title = f"Expense for Month: {month}"
    elif filter_type == "year":
        year = datetime.now().strftime("%Y")
        cur.execute("SELECT * FROM expense_head WHERE strftime('%Y', date) = ?", (year))
        title = f"Expense for Year: {year}"
    elif filter_type == "quarter":
        month = datetime.now().month
        year = datetime.now().strftime("%Y")
        if month in [1,3]:
            start , end = 1,3
            quarter = "Q1"
        elif month in [4,6]:
            start , end = 4,6
            quarter = "Q2"
        elif month in [7,9]:
            start , end = 7,9
            quarter = "Q3"
        else:
            start , end = 10,12
            quarter = "Q4"
        cur.execute("SELECT * FROM expense_head WHERE strftime('%Y', date) = ? AND CAST(strftime('%m', date) as INTEGER) BETWEEN ? AND ?",
                    (year, start, end))
        title = f"Expense for Quarter: Q{quarter} {datetime.now().year}"
# customized date range(from date , to date)
    elif request.method == "POST":
        from_date = request.form.get("from_date")
        to_date = request.form.get("to_date")

        if from_date and to_date:
         cur.execute("SELECT * FROM expense_head WHERE date BETWEEN ? AND ? order by date asc", (from_date, to_date))
         title = f"Expense from {from_date} to {to_date}"

    else:
        cur.execute("SELECT * FROM expense_head ORDER BY id asc")
        title = "All Expenses"
    expenses = cur.fetchall()
    total = sum([row[3] for row in expenses])
    conn.close()
    return render_template('index.html', expenses=expenses, title="title", total=total)

# ---------- Chart Data ----------
@app.route('/chart-data')
def chart_data():
    conn = sqlite3.connect("expenses.db")
    cur = conn.cursor()
    cur.execute("SELECT category, SUM(amount) FROM expense_head GROUP BY category")
    category_data = cur.fetchall()
    conn.close()

    labels = [row[0] for row in category_data]
    values = [row[1] for row in category_data]
    return jsonify({"labels": labels, "values": values})


# ---------- Run App ----------
if __name__ == "__main__":
    init_db()
    app.run(debug=True)

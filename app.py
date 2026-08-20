import os
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dhruvi-secret-key")

# Azure SQL Connection String Configuration
db_url = os.environ.get('DATABASE_URL')
if db_url and db_url.startswith("odbc:"):
    # Format ODBC string for SQLAlchemy
    from urllib.parse import quote_plus
    params = quote_plus(db_url.replace("odbc:", ""))
    app.config['SQLALCHEMY_DATABASE_URI'] = f"mssql+pyodbc:///?odbc_connect={params}"
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url or 'sqlite:///local_employee.db'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Employee Model
class Employee(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    department = db.Column(db.String(50), nullable=False)
    designation = db.Column(db.String(50), nullable=False)
    salary = db.Column(db.Float, nullable=False)

with app.app_context():
    db.create_all()

# READ & SEARCH
@app.route('/')
def index():
    search_query = request.args.get('search', '')
    if search_query:
        employees = Employee.query.filter(Employee.name.ilike(f"%{search_query}%")).all()
    else:
        employees = Employee.query.all()
    return render_template('index.html', employees=employees, search_query=search_query)

# CREATE
@app.route('/add', methods=['POST'])
def add_employee():
    try:
        new_emp = Employee(
            name=request.form['name'],
            email=request.form['email'],
            department=request.form['department'],
            designation=request.form['designation'],
            salary=float(request.form['salary'])
        )
        db.session.add(new_emp)
        db.session.commit()
        flash('Employee added successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error adding employee: {str(e)}', 'danger')
    return redirect(url_for('index'))

# UPDATE
@app.route('/update/<int:id>', methods=['POST'])
def update_employee(id):
    emp = Employee.query.get_or_404(id)
    try:
        emp.name = request.form['name']
        emp.email = request.form['email']
        emp.department = request.form['department']
        emp.designation = request.form['designation']
        emp.salary = float(request.form['salary'])
        db.session.commit()
        flash('Employee record updated successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error updating employee: {str(e)}', 'danger')
    return redirect(url_for('index'))

# DELETE
@app.route('/delete/<int:id>')
def delete_employee(id):
    emp = Employee.query.get_or_404(id)
    try:
        db.session.delete(emp)
        db.session.commit()
        flash('Employee deleted successfully!', 'warning')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting employee: {str(e)}', 'danger')
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
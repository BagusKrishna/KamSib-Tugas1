from flask import Flask, render_template, request, redirect, url_for, session, flash, abort
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
from functools import wraps
import sqlite3
from sqlalchemy.exc import SQLAlchemyError

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///students.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'admin' #Penambahan Secret Key
db = SQLAlchemy(app)


# Menambah logon required
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    grade = db.Column(db.String(10), nullable=False)

    def __repr__(self):
        return f'<Student {self.name}>'



#Penambahan Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        if username == 'admin' and password == 'admin':
            session['logged_in'] = True
            return redirect(url_for('index'))
        else:
            flash('Username atau password salah!')
            return redirect(url_for('login'))
    return render_template('login.html')

#Penambahan sebuah logout
@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('login'))

@app.route('/')
@login_required
def index():
    #students = db.session.execute(text('SELECT * FROM student')).fetchall()
    #return render_template('index.html', students=students)

    try:
        students = db.session.execute(text('SELECT * FROM student')).fetchall()
        return render_template('index.html', students=students)
    except Exception:
        return redirect(url_for('error', message="Error"))



@app.route('/add', methods=['POST'])
@login_required
def add_student():
    #name = request.form['name']
    #age = request.form['age']
    #grade = request.form['grade']
    
    #connection = sqlite3.connect('instance/students.db')
    #cursor = connection.cursor()
    #query = f"INSERT INTO student (name, age, grade) VALUES ('{name}', {age}, '{grade}')"
    #cursor.execute(query)
    #connection.commit()
    #connection.close()
    #return redirect(url_for('index'))

    name = request.form['name']
    age = request.form['age']
    grade = request.form['grade']
    
    try:
        connection = sqlite3.connect('instance/students.db')
        cursor = connection.cursor()
        query = f"INSERT INTO student (name, age, grade) VALUES ('{name}', {age}, '{grade}')"
        cursor.execute(query)
        connection.commit()
        connection.close()
        return redirect(url_for('index'))
    except Exception as e:
        return redirect(url_for('error', message="Error"))



@app.route('/delete/<string:id>')
@login_required
#def delete_student(id):
#    db.session.execute(text(f"DELETE FROM student WHERE id={id}"))
#    db.session.commit()
#    return redirect(url_for('index'))

def delete_student(id):
    if not id.isdigit():
        abort(400, "Invalid input") #validais inputan
    try:
        # untuk mencegah SQL Injection
        db.session.execute(text("DELETE FROM student WHERE id = :id"), {"id": id})
        db.session.commit()
        return redirect(url_for('index'))
    except SQLAlchemyError as e:
        db.session.rollback()  # jika error, dilakukan rollbavk
        abort(500, f"Database error: {str(e)}")

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_student(id):
    #if request.method == 'POST':
    #   name = request.form['name']
    #  age = request.form['age']
    #    grade = request.form['grade']
    #    
    #    db.session.execute(text(f"UPDATE student SET name='{name}', age={age}, grade='{grade}' WHERE id={id}"))
    #    db.session.commit()
    #    return redirect(url_for('index'))
    #else:
    #    student = db.session.execute(text(f"SELECT * FROM student WHERE id={id}")).fetchone()
    #    return render_template('edit.html', student=student)

    if request.method == 'POST':
        name = request.form['name']
        age = request.form['age']
        grade = request.form['grade']
        
        try:
            db.session.execute(text(f"UPDATE student SET name='{name}', age={age}, grade='{grade}' WHERE id={id}"))
            db.session.commit()
            return redirect(url_for('index'))
        except SQLAlchemyError as e:
            db.session.rollback()
            return redirect(url_for('error', message="Error"))
    else:
        student = db.session.execute(text(f"SELECT * FROM student WHERE id={id}")).fetchone()
        return render_template('edit.html', student=student)


@app.route('/error', methods=['GET'])
def error():
    message = request.args.get('message', 'An error occurred')
    return render_template('error.html', message=message)


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=5000, debug=True)
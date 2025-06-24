from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_mysqldb import MySQL
from flask_bcrypt import Bcrypt
import os
from werkzeug.security import check_password_hash
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY') or 'una-clave-secreta-muy-segura'

# Configuración de MySQL
# Cambia el host según el entorno: 'localhost' para desarrollo local, 'db' para Docker
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'upds'
app.config['MYSQL_PASSWORD'] = 'upds123'
app.config['MYSQL_DB'] = 'upds_practicas'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

mysql = MySQL(app)
bcrypt = Bcrypt(app)

@app.route('/')
def index():
    if 'loggedin' in session:
        if session['rol'] == 'admin':
            return redirect(url_for('admin'))
        return redirect(url_for('dashboard'))
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        cursor = mysql.connection.cursor()
        cursor.execute('SELECT * FROM usuarios WHERE email = %s', (email,))
        account = cursor.fetchone()
        cursor.close()
        
        if account and bcrypt.check_password_hash(account['password'], password):
            session['loggedin'] = True
            session['id'] = account['id']
            session['email'] = account['email']
            session['rol'] = account['rol']
            session['nombre'] = account['nombre']
            
            if account['rol'] == 'admin':
                return redirect(url_for('admin'))
            return redirect(url_for('dashboard'))
        else:
            flash('Correo electrónico o contraseña incorrectos', 'danger')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        # Usar bcrypt para generar el hash de la contraseña
        password = bcrypt.generate_password_hash(request.form['password']).decode('utf-8')
        nombre = request.form['nombre']
        apellido = request.form['apellido']
        telefono = request.form['telefono']
        carrera = request.form['carrera']
        
        cursor = mysql.connection.cursor()
        try:
            cursor.execute('''
                INSERT INTO usuarios 
                (email, password, nombre, apellido, telefono, carrera, rol) 
                VALUES (%s, %s, %s, %s, %s, %s, 'estudiante')
            ''', (email, password, nombre, apellido, telefono, carrera))
            mysql.connection.commit()
            flash('Registro exitoso. Por favor inicie sesión.', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            mysql.connection.rollback()
            flash('Error al registrar. El correo ya existe.', 'danger')
        finally:
            cursor.close()
    
    return render_template('register.html')

@app.route('/admin')
def admin():
    if 'loggedin' not in session or session['rol'] != 'admin':
        return redirect(url_for('login'))
    
    cursor = mysql.connection.cursor()
    cursor.execute('SELECT id, email, nombre, apellido, rol, carrera FROM usuarios')
    users = cursor.fetchall()
    cursor.close()
    
    return render_template('admin.html', users=users)

@app.route('/dashboard')
def dashboard():
    if 'loggedin' not in session:
        return redirect(url_for('login'))
    
    cursor = mysql.connection.cursor()
    cursor.execute('SELECT * FROM practicas')
    practicas = cursor.fetchall()
    cursor.close()
    
    return render_template('dashboard.html', 
                         nombre=session['nombre'],
                         rol=session['rol'],
                         practicas=practicas)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)

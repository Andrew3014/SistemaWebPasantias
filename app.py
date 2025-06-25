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
app.config['MYSQL_CHARSET'] = 'utf8mb4'  # Asegura la codificación correcta

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

@app.route('/admin/usuarios/edit/<int:user_id>', methods=['GET', 'POST'])
def edit_usuario(user_id):
    if 'loggedin' not in session or session['rol'] != 'admin':
        return redirect(url_for('login'))
    cursor = mysql.connection.cursor()
    if request.method == 'POST':
        nombre = request.form['nombre']
        apellido = request.form['apellido']
        email = request.form['email']
        telefono = request.form['telefono']
        carrera = request.form['carrera']
        rol = request.form['rol']
        try:
            cursor.execute('''
                UPDATE usuarios SET nombre=%s, apellido=%s, email=%s, telefono=%s, carrera=%s, rol=%s WHERE id=%s
            ''', (nombre, apellido, email, telefono, carrera, rol, user_id))
            mysql.connection.commit()
            flash('Usuario actualizado correctamente', 'success')
            return redirect(url_for('admin'))
        except Exception as e:
            mysql.connection.rollback()
            flash('Error al actualizar usuario', 'danger')
    cursor.execute('SELECT * FROM usuarios WHERE id = %s', (user_id,))
    user = cursor.fetchone()
    cursor.close()
    return render_template('edit_usuario.html', user=user)

@app.route('/admin/usuarios/delete/<int:user_id>', methods=['POST'])
def delete_usuario(user_id):
    if 'loggedin' not in session or session['rol'] != 'admin':
        return redirect(url_for('login'))
    cursor = mysql.connection.cursor()
    try:
        cursor.execute('DELETE FROM usuarios WHERE id = %s', (user_id,))
        mysql.connection.commit()
        flash('Usuario eliminado correctamente', 'success')
    except Exception as e:
        mysql.connection.rollback()
        flash('Error al eliminar usuario', 'danger')
    finally:
        cursor.close()
    return redirect(url_for('admin'))

@app.route('/admin/practicas/new', methods=['GET', 'POST'])
def nueva_practica():
    if 'loggedin' not in session or session['rol'] != 'admin':
        return redirect(url_for('login'))
    if request.method == 'POST':
        titulo = request.form['titulo']
        descripcion = request.form['descripcion']
        empresa = request.form['empresa']
        area = request.form['area']
        requisitos = request.form['requisitos']
        duracion = request.form['duracion']
        contacto = request.form['contacto']
        cursor = mysql.connection.cursor()
        try:
            cursor.execute('''
                INSERT INTO practicas (titulo, descripcion, empresa, area, requisitos, duracion, contacto)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            ''', (titulo, descripcion, empresa, area, requisitos, duracion, contacto))
            mysql.connection.commit()
            flash('Práctica creada correctamente', 'success')
            return redirect(url_for('admin'))
        except Exception as e:
            mysql.connection.rollback()
            flash('Error al crear la práctica', 'danger')
        finally:
            cursor.close()
    return render_template('nueva_practica.html')

@app.route('/admin/practicas/edit/<int:practica_id>', methods=['GET', 'POST'])
def editar_practica(practica_id):
    if 'loggedin' not in session or session['rol'] != 'admin':
        return redirect(url_for('login'))
    cursor = mysql.connection.cursor()
    if request.method == 'POST':
        titulo = request.form['titulo']
        descripcion = request.form['descripcion']
        empresa = request.form['empresa']
        area = request.form['area']
        requisitos = request.form['requisitos']
        duracion = request.form['duracion']
        contacto = request.form['contacto']
        try:
            cursor.execute('''
                UPDATE practicas SET titulo=%s, descripcion=%s, empresa=%s, area=%s, requisitos=%s, duracion=%s, contacto=%s WHERE id=%s
            ''', (titulo, descripcion, empresa, area, requisitos, duracion, contacto, practica_id))
            mysql.connection.commit()
            flash('Práctica actualizada correctamente', 'success')
            return redirect(url_for('admin'))
        except Exception as e:
            mysql.connection.rollback()
            flash('Error al actualizar la práctica', 'danger')
    cursor.execute('SELECT * FROM practicas WHERE id = %s', (practica_id,))
    practica = cursor.fetchone()
    cursor.close()
    return render_template('editar_practica.html', practica=practica)

@app.route('/admin/practicas/delete/<int:practica_id>', methods=['POST'])
def eliminar_practica(practica_id):
    if 'loggedin' not in session or session['rol'] != 'admin':
        return redirect(url_for('login'))
    cursor = mysql.connection.cursor()
    try:
        cursor.execute('DELETE FROM practicas WHERE id = %s', (practica_id,))
        mysql.connection.commit()
        flash('Práctica eliminada correctamente', 'success')
    except Exception as e:
        mysql.connection.rollback()
        flash('Error al eliminar la práctica', 'danger')
    finally:
        cursor.close()
    return redirect(url_for('admin'))

@app.route('/postular/<int:practica_id>', methods=['POST'])
def postular_practica(practica_id):
    if 'loggedin' not in session or session['rol'] != 'estudiante':
        return redirect(url_for('login'))
    usuario_id = session['id']
    cursor = mysql.connection.cursor()
    # Verificar si ya está postulado
    cursor.execute('SELECT * FROM postulaciones WHERE usuario_id=%s AND practica_id=%s', (usuario_id, practica_id))
    existe = cursor.fetchone()
    if existe:
        flash('Ya te has postulado a esta práctica.', 'warning')
        cursor.close()
        return redirect(url_for('dashboard'))
    try:
        cursor.execute('INSERT INTO postulaciones (usuario_id, practica_id) VALUES (%s, %s)', (usuario_id, practica_id))
        mysql.connection.commit()
        flash('¡Postulación realizada correctamente!', 'success')
    except Exception as e:
        mysql.connection.rollback()
        flash('Error al postularse.', 'danger')
    finally:
        cursor.close()
    return redirect(url_for('dashboard'))

@app.route('/mis-postulaciones')
def mis_postulaciones():
    if 'loggedin' not in session or session['rol'] != 'estudiante':
        return redirect(url_for('login'))
    usuario_id = session['id']
    cursor = mysql.connection.cursor()
    cursor.execute('''
        SELECT p.*, po.estado, po.fecha_postulacion
        FROM postulaciones po
        JOIN practicas p ON po.practica_id = p.id
        WHERE po.usuario_id = %s
        ORDER BY po.fecha_postulacion DESC
    ''', (usuario_id,))
    postulaciones = cursor.fetchall()
    cursor.close()
    return render_template('mis_postulaciones.html', postulaciones=postulaciones)

@app.context_processor
def inject_practicas_admin():
    if 'loggedin' in session and session['rol'] == 'admin':
        cursor = mysql.connection.cursor()
        cursor.execute('SELECT * FROM practicas')
        practicas = cursor.fetchall()
        cursor.close()
        return dict(users_practicas=practicas)
    return dict(users_practicas=[])

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)

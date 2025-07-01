
from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_bcrypt import Bcrypt
import os
from dotenv import load_dotenv
from models import (
    get_usuario_by_email, update_usuario, get_usuario_by_id, registrar_usuario, get_all_usuarios, delete_usuario,
    crear_practica, editar_practica, eliminar_practica, get_all_practicas, get_practica_by_id,
    postular_practica as model_postular_practica, existe_postulacion, get_postulaciones_usuario,
    get_all_postulaciones, actualizar_estado_postulacion
)




# Solo una inicialización de Flask y Bcrypt
load_dotenv()
app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY') or 'una-clave-secreta-muy-segura'
bcrypt = Bcrypt(app)

# Ruta para que el admin vea todas las postulaciones y pueda aceptar/rechazar
@app.route('/admin/postulaciones', methods=['GET', 'POST'])
def admin_postulaciones():
    if 'loggedin' not in session or session['rol'] != 'admin':
        return redirect(url_for('login'))
    if request.method == 'POST':
        postulacion_id = request.form.get('postulacion_id')
        accion = request.form.get('accion')
        if postulacion_id and accion in ['aceptada', 'rechazada']:
            actualizar_estado_postulacion(postulacion_id, accion)
            flash('Estado de postulación actualizado.', 'success')
        return redirect(url_for('admin_postulaciones'))
    postulaciones = get_all_postulaciones()
    return render_template('admin_postulaciones.html', postulaciones=postulaciones)

@app.route('/login', methods=['GET', 'POST'])
def login():
   
    # Login de usuario (admin o estudiante)
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        account = get_usuario_by_email(email)
        if account and bcrypt.check_password_hash(account['password'], password):
            session['loggedin'] = True
            session['id'] = account['id']
            session['email'] = account['email']
            session['rol'] = account['rol']
            session['nombre'] = account['nombre']
            
            # Redirigir según el rol
            if account['rol'] == 'admin':
                return redirect(url_for('admin'))
            else:
                return redirect(url_for('dashboard'))
        else:
            flash('Correo electrónico o contraseña incorrectos', 'danger')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    
    # Registro de usuario estudiante
    carreras = ['Ingeniería de Sistemas', 'Ingeniería Comercial', 'Derecho', 'Contaduría Pública', 'Administración de Empresas']
    if request.method == 'POST':
        email = request.form['email']
        password_raw = request.form['password']
        nombre = ' '.join([n.capitalize() for n in request.form['nombre'].strip().split()])
        apellido = ' '.join([a.capitalize() for a in request.form['apellido'].strip().split()])

        # Validación de longitud y caracteres de nombre y apellido
        if not (2 <= len(nombre) <= 30) or not nombre.replace(' ', '').isalpha():
            flash('El nombre debe tener entre 2 y 30 letras y solo puede contener letras y espacios.', 'danger')
            return render_template('register.html', carreras=carreras)
        if not (2 <= len(apellido) <= 30) or not apellido.replace(' ', '').isalpha():
            flash('El apellido debe tener entre 2 y 30 letras y solo puede contener letras y espacios.', 'danger')
            return render_template('register.html', carreras=carreras)

        # Validación de longitud de correo
        if len(email) > 60:
            flash('El correo es demasiado largo (máx. 60 caracteres).', 'danger')
            return render_template('register.html', carreras=carreras)

        # Validación de longitud de teléfono
        if not (7 <= len(telefono) <= 15):
            flash('El teléfono debe tener entre 7 y 15 dígitos.', 'danger')
            return render_template('register.html', carreras=carreras)
        telefono = request.form['telefono']
        carrera = request.form['carrera']
        
        # Validación de correo institucional
        if not email.endswith('@upds.edu.bo'):
            flash('Solo se permiten correos institucionales (@upds.edu.bo)', 'danger')
            return render_template('register.html', carreras=carreras)
        
        # Validación de teléfono solo números
        if not telefono.isdigit():
            flash('El teléfono solo debe contener números.', 'danger')
            return render_template('register.html', carreras=carreras)
        
        # Validación de longitud mínima de contraseña
        if len(password_raw) < 8:
            flash('La contraseña debe tener al menos 8 caracteres.', 'danger')
            return render_template('register.html', carreras=carreras)
        
        # Validación de combinación única nombre+apellido
        for u in get_all_usuarios():
            u_nombre = ' '.join([n.capitalize() for n in u['nombre'].strip().split()])
            u_apellido = ' '.join([a.capitalize() for a in u['apellido'].strip().split()])
            if u_nombre == nombre and u_apellido == apellido:
                flash('Ya existe un usuario con ese nombre y apellido.', 'danger')
                return render_template('register.html', carreras=carreras)
        
        # Usar bcrypt para generar el hash de la contraseña
        password = bcrypt.generate_password_hash(password_raw).decode('utf-8')
        try:
            registrar_usuario(email, password, nombre, apellido, telefono, carrera)
            flash('Registro exitoso. Por favor inicie sesión.', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            flash('Error al registrar. El correo ya existe.', 'danger')
    return render_template('register.html', carreras=carreras)

@app.route('/')
def index():
    if 'loggedin' in session:
        if session['rol'] == 'admin':
            return redirect(url_for('admin'))
        else:
            return redirect(url_for('dashboard'))
    return render_template('index.html')

@app.route('/admin')
def admin():

    # Panel de administración (usuarios y prácticas)
    if 'loggedin' not in session or session['rol'] != 'admin':
        return redirect(url_for('login'))
    users = get_all_usuarios()
    carreras = ['Ingeniería de Sistemas', 'Ingeniería Comercial', 'Derecho', 'Contaduría Pública', 'Administración de Empresas']
    return render_template('admin.html', users=users, carreras=carreras)

@app.route('/admin/usuarios/edit/<int:user_id>', methods=['GET', 'POST'])
def edit_usuario(user_id):
    
    # Edición de usuario por el admin
    if 'loggedin' not in session or session['rol'] != 'admin':
        return redirect(url_for('login'))
    carreras = ['Ingeniería de Sistemas', 'Ingeniería Comercial', 'Derecho', 'Contaduría Pública', 'Administración de Empresas']
    if request.method == 'POST':
        nombre = ' '.join([n.capitalize() for n in request.form['nombre'].strip().split()])
        apellido = ' '.join([a.capitalize() for a in request.form['apellido'].strip().split()])

        # Validación de longitud y caracteres de nombre y apellido
        if not (2 <= len(nombre) <= 30) or not nombre.replace(' ', '').isalpha():
            flash('El nombre debe tener entre 2 y 30 letras y solo puede contener letras y espacios.', 'danger')
            user = get_usuario_by_id(user_id)
            return render_template('edit_usuario.html', user=user, carreras=carreras)
        if not (2 <= len(apellido) <= 30) or not apellido.replace(' ', '').isalpha():
            flash('El apellido debe tener entre 2 y 30 letras y solo puede contener letras y espacios.', 'danger')
            user = get_usuario_by_id(user_id)
            return render_template('edit_usuario.html', user=user, carreras=carreras)

        # Validación de longitud de correo
        if len(email) > 60:
            flash('El correo es demasiado largo (máx. 60 caracteres).', 'danger')
            user = get_usuario_by_id(user_id)
            return render_template('edit_usuario.html', user=user, carreras=carreras)

        # Validación de longitud de teléfono
        if not (7 <= len(telefono) <= 15):
            flash('El teléfono debe tener entre 7 y 15 dígitos.', 'danger')
            user = get_usuario_by_id(user_id)
            return render_template('edit_usuario.html', user=user, carreras=carreras)
        email = request.form['email']
        telefono = request.form['telefono']
        carrera = request.form['carrera']
        nueva_contrasena = request.form.get('nueva_contrasena', '').strip()
        try:
            if nueva_contrasena:
                if len(nueva_contrasena) < 8:
                    flash('La nueva contraseña debe tener al menos 8 caracteres.', 'danger')
                    user = get_usuario_by_id(user_id)
                    return render_template('edit_usuario.html', user=user, carreras=carreras)
                hashed = bcrypt.generate_password_hash(nueva_contrasena).decode('utf-8')
                
                # Actualiza también la contraseña
                from db import get_db_connection
                conn = get_db_connection()
                cursor = conn.cursor()
                cursor.execute('''
                    UPDATE usuarios SET nombre=%s, apellido=%s, email=%s, telefono=%s, carrera=%s, password=%s WHERE id=%s
                ''', (nombre, apellido, email, telefono, carrera, hashed, user_id))
                conn.commit()
                cursor.close()
            else:
                update_usuario(user_id, nombre, apellido, email, telefono, carrera)
            flash('Usuario actualizado correctamente', 'success')
            return redirect(url_for('admin'))
        except Exception as e:
            flash('Error al actualizar usuario', 'danger')
    user = get_usuario_by_id(user_id)
    return render_template('edit_usuario.html', user=user, carreras=carreras)

@app.route('/admin/practicas/new', methods=['GET', 'POST'])
def nueva_practica():

    # Crear nueva práctica profesional (admin)
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
        import re
        email_regex = r"^[\w\.-]+@([\w\-]+\.)+[A-Za-z]{2,}$"
        telefono_regex = r"^\d{7,15}$"
        if not (re.match(email_regex, contacto) or re.match(telefono_regex, contacto)):
            flash('El contacto debe ser un correo válido o un número de teléfono válido.', 'danger')
            return render_template('nueva_practica.html')
        try:
            crear_practica(titulo, descripcion, empresa, area, requisitos, duracion, contacto)
            flash('Práctica creada correctamente', 'success')
            return redirect(url_for('admin'))
        except Exception as e:
            flash('Error al crear la práctica', 'danger')
    return render_template('nueva_practica.html')

@app.route('/admin/practicas/edit/<int:practica_id>', methods=['GET', 'POST'])
def editar_practica(practica_id):

    # Editar práctica profesional (admin)
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
        try:
            editar_practica(practica_id, titulo, descripcion, empresa, area, requisitos, duracion, contacto)
            flash('Práctica actualizada correctamente', 'success')
            return redirect(url_for('admin'))
        except Exception as e:
            flash('Error al actualizar la práctica', 'danger')
    practica = get_practica_by_id(practica_id)
    return render_template('editar_practica.html', practica=practica)

@app.route('/admin/practicas/delete/<int:practica_id>', methods=['POST'])
def eliminar_practica(practica_id):

    # Eliminar práctica profesional (admin)
    if 'loggedin' not in session or session['rol'] != 'admin':
        return redirect(url_for('login'))
    try:
        eliminar_practica(practica_id)
        flash('Práctica eliminada correctamente', 'success')
    except Exception as e:
        flash('Error al eliminar la práctica', 'danger')
    return redirect(url_for('admin'))

@app.route('/postular/<int:practica_id>', methods=['POST'])
def postular_practica(practica_id):

    # Postularse a una práctica (estudiante)
    if 'loggedin' not in session or session['rol'] != 'estudiante':
        return redirect(url_for('login'))
    usuario_id = session['id']
    if existe_postulacion(usuario_id, practica_id):
        flash('Ya te has postulado a esta práctica.', 'warning')
        return redirect(url_for('dashboard'))
    try:
        model_postular_practica(usuario_id, practica_id)
        flash('¡Postulación realizada correctamente!', 'success')
    except Exception as e:
        flash('Error al postularse.', 'danger')
    return redirect(url_for('dashboard'))

@app.route('/mis-postulaciones')
def mis_postulaciones():

    # Ver postulaciones del estudiante
    if 'loggedin' not in session or session['rol'] != 'estudiante':
        return redirect(url_for('login'))
    usuario_id = session['id']
    postulaciones = get_postulaciones_usuario(usuario_id)
    return render_template('mis_postulaciones.html', postulaciones=postulaciones)

@app.route('/dashboard')
def dashboard():

    # Panel de usuario (estudiante o admin)
    if 'loggedin' not in session:
        return redirect(url_for('login'))
    practicas = get_all_practicas()
    return render_template('dashboard.html', 
                         nombre=session['nombre'],
                         rol=session['rol'],
                         practicas=practicas)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.context_processor
def inject_practicas_admin():

    # Inyecta prácticas para el panel admin
    if 'loggedin' in session and session['rol'] == 'admin':
        practicas = get_all_practicas()
        return dict(users_practicas=practicas)
    return dict(users_practicas=[])

@app.route('/admin/usuarios/delete/<int:user_id>', methods=['POST'])
def delete_usuario(user_id):

    # Eliminar usuario (admin)
    if 'loggedin' not in session or session['rol'] != 'admin':
        return redirect(url_for('login'))
    try:
        delete_usuario(user_id)
        flash('Usuario eliminado correctamente', 'success')
    except Exception as e:
        flash('Error al eliminar usuario', 'danger')
    return redirect(url_for('admin'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)

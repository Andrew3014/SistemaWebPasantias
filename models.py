# Obtener todas las postulaciones con datos de usuario y práctica (para admin)
def get_all_postulaciones():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('''
        SELECT po.id, po.estado, po.fecha_postulacion, u.nombre, u.apellido, u.email, u.carrera, p.titulo, p.empresa, p.area
        FROM postulaciones po
        JOIN usuarios u ON po.usuario_id = u.id
        JOIN practicas p ON po.practica_id = p.id
        ORDER BY po.fecha_postulacion DESC
    ''')
    postulaciones = cursor.fetchall()
    cursor.close()
    return postulaciones

# Cambiar estado de una postulación (aceptar/rechazar)
def actualizar_estado_postulacion(postulacion_id, nuevo_estado):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('UPDATE postulaciones SET estado=%s WHERE id=%s', (nuevo_estado, postulacion_id))
    conn.commit()
    cursor.close()

# models.py
# Funciones de acceso a la base de datos usando SingletonDB (Modelo)
from db import get_db_connection

# -------- USUARIOS --------

# Obtener usuario por email (para login)
def get_usuario_by_email(email):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT * FROM usuarios WHERE email = %s', (email,))
    user = cursor.fetchone()
    cursor.close()
    return user

# Actualizar datos de usuario (admin)
def update_usuario(user_id, nombre, apellido, email, telefono, carrera):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE usuarios SET nombre=%s, apellido=%s, email=%s, telefono=%s, carrera=%s WHERE id=%s
    ''', (nombre, apellido, email, telefono, carrera, user_id))
    conn.commit()
    cursor.close()

# Obtener usuario por ID
def get_usuario_by_id(user_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT * FROM usuarios WHERE id = %s', (user_id,))
    user = cursor.fetchone()
    cursor.close()
    return user

# Registrar nuevo usuario
def registrar_usuario(email, password, nombre, apellido, telefono, carrera):
    '''Registra un nuevo usuario estudiante.'''
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO usuarios (email, password, nombre, apellido, telefono, carrera, rol)
        VALUES (%s, %s, %s, %s, %s, %s, 'estudiante')
    ''', (email, password, nombre, apellido, telefono, carrera))
    conn.commit()
    cursor.close()

# Obtener todos los usuarios (admin)
def get_all_usuarios():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT id, email, nombre, apellido, rol, carrera FROM usuarios')
    users = cursor.fetchall()
    cursor.close()
    return users

# Eliminar usuario por ID (admin)
def delete_usuario(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM usuarios WHERE id = %s', (user_id,))
    conn.commit()
    cursor.close()


# ------------ PRACTICAS o PASANTIAS-------------

# Crear nueva práctica
def crear_practica(titulo, descripcion, empresa, area, requisitos, duracion, contacto):
    '''Crea una nueva práctica profesional.'''
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO practicas (titulo, descripcion, empresa, area, requisitos, duracion, contacto)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    ''', (titulo, descripcion, empresa, area, requisitos, duracion, contacto))
    conn.commit()
    cursor.close()

# Editar práctica existente
def editar_practica(practica_id, titulo, descripcion, empresa, area, requisitos, duracion, contacto):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE practicas SET titulo=%s, descripcion=%s, empresa=%s, area=%s, requisitos=%s, duracion=%s, contacto=%s WHERE id=%s
    ''', (titulo, descripcion, empresa, area, requisitos, duracion, contacto, practica_id))
    conn.commit()
    cursor.close()

# Eliminar práctica
def eliminar_practica(practica_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM practicas WHERE id = %s', (practica_id,))
    conn.commit()
    cursor.close()

# Obtener todas las prácticas
def get_all_practicas():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT * FROM practicas')
    practicas = cursor.fetchall()
    cursor.close()
    return practicas

# Obtener práctica por ID
def get_practica_by_id(practica_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT * FROM practicas WHERE id = %s', (practica_id,))
    practica = cursor.fetchone()
    cursor.close()
    return practica


# -------- POSTULACIONES --------

# Postular a una práctica
def postular_practica(usuario_id, practica_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('INSERT INTO postulaciones (usuario_id, practica_id) VALUES (%s, %s)', (usuario_id, practica_id))
    conn.commit()
    cursor.close()

# Verificar si ya está postulado
def existe_postulacion(usuario_id, practica_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT * FROM postulaciones WHERE usuario_id=%s AND practica_id=%s', (usuario_id, practica_id))
    existe = cursor.fetchone()
    cursor.close()
    return existe

# Obtener postulaciones de un usuario
def get_postulaciones_usuario(usuario_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('''
        SELECT p.*, po.estado, po.fecha_postulacion
        FROM postulaciones po
        JOIN practicas p ON po.practica_id = p.id
        WHERE po.usuario_id = %s
        ORDER BY po.fecha_postulacion DESC
    ''', (usuario_id,))
    postulaciones = cursor.fetchall()
    cursor.close()
    return postulaciones

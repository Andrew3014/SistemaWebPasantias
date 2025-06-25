# Sistema Web de Gestión de Prácticas Pre-Profesionales (UPDS)

**Objetivo Principal:**
Automatizar el proceso de postulación y seguimiento de prácticas profesionales para estudiantes, docentes y empresas, reemplazando el sistema manual basado en Google Drive y correos electrónicos.

**Tecnologías utilizadas:**
- Flask (backend)
- MySQL (base de datos)
- Podman (contenedorización)
- Bootstrap (frontend)

---

# Sistema de Prácticas Profesionales UPDS

Este proyecto es un sistema web para la gestión de prácticas profesionales de la Universidad Privada Domingo Savio, desarrollado con Flask, MySQL y Podman.

## Estructura del Proyecto

```
/practicas-upds
│
├── app.py                  # Aplicación principal Flask
├── requirements.txt        # Dependencias de Python
├── Dockerfile              # Configuración del contenedor
├── docker-compose.yml      # Configuración de Docker
├── /static
│   ├── css                 # Archivos CSS
│   └── images              # Imágenes
├── /templates
│   ├── base.html           # Plantilla base
│   ├── login.html          # Página de login
│   ├── register.html       # Página de registro
│   ├── admin.html          # Panel de administración
│   └── dashboard.html      # Dashboard de usuario
└── /sql
    ├── schema.sql          # Esquema de la base de datos
    └── data.sql            # Datos de prueba
```

## Instalación y Uso

### Opción 1: Usando Docker (recomendado)

1. Instala Docker y Docker Compose.
2. En la raíz del proyecto, ejecuta:
   ```powershell
   docker-compose up -d --build
   ```
3. Accede a la aplicación en [http://localhost:5000](http://localhost:5000)

### Opción 2: Entorno local (Windows)

1. Instala Python 3.11+ y MySQL Server.
2. Crea y activa un entorno virtual:
   ```powershell
   python -m venv venv
   .\venv\Scripts\Activate
   ```
3. Instala las dependencias:
   ```powershell
   pip install -r requirements.txt
   ```
4. Crea la base de datos y carga el esquema y los datos:
   - Abre MySQL Workbench y ejecuta los scripts `sql/schema.sql` y luego `sql/data.sql` sobre la base de datos `upds_practicas`.
5. Edita `app.py` y asegúrate que la línea:
   ```python
   app.config['MYSQL_HOST'] = 'localhost'
   ```
   esté activa para desarrollo local.
6. Ejecuta la app:
   ```powershell
   python app.py
   ```
7. Accede a la aplicación en [http://localhost:5000](http://localhost:5000)

## Importante para pruebas y desarrollo

- Asegúrate de ejecutar **todo el script `sql/schema.sql`** para crear todas las tablas necesarias, incluyendo `postulaciones`.
- Puedes cargar datos de ejemplo ejecutando también `sql/data.sql` en la base de datos `upds_practicas`.
- El usuario administrador por defecto es:
  - Usuario: `admin@upds.edu.bo`
  - Contraseña: `admin123`
- Rutas principales:
  - `/admin` — Panel de administración (solo admin)
  - `/dashboard` — Dashboard de usuario
  - `/mis-postulaciones` — Postulaciones del usuario

## Pruebas automáticas

Si deseas automatizar pruebas (por ejemplo, con Robot Framework), asegúrate de que la base de datos esté limpia y con datos de prueba antes de cada test.

## Comandos útiles con Docker

- Construir y levantar los contenedores:
  ```powershell
  docker-compose up -d --build
  ```
- Detener los contenedores:
  ```powershell
  docker-compose down
  ```
- Ver logs:
  ```powershell
  docker-compose logs -f
  ```
- Acceder a la base de datos MySQL:
  ```powershell
  docker exec -it <nombre_contenedor_db> mysql -u upds -pupds123 upds_practicas
  ```

## Características
- Login y registro de usuarios
- Panel de administración
- Dashboard de usuario
- Base de datos MySQL
- Contenedores gestionados con Docker

## Notas y solución de problemas
- Si corres la app localmente y ves un error de conexión a MySQL, asegúrate de que `MYSQL_HOST` sea `localhost` y que el servidor MySQL esté corriendo.
- Si necesitas cambiar la contraseña del admin, genera un hash bcrypt con Flask-Bcrypt y actualízalo en la base de datos.
- Modifica la variable `SECRET_KEY` en el archivo `.env` para mayor seguridad en producción.

## Optimización para Docker en Windows/WSL2
- Se recomienda usar WSL2 para un mejor rendimiento de Docker en Windows.
- Asegúrate de que los volúmenes estén en el sistema de archivos de WSL2 para evitar problemas de rendimiento.
- Si usas Docker Desktop, habilita la integración con WSL2 y comparte la carpeta del proyecto.
- Para limpiar recursos:
  ```powershell
  docker system prune -a
  ```

---
Desarrollado para la Universidad Privada Domingo Savio.

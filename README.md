# PROY3BD1

Milton Giovanni Polanco Serrano (23471) - Diagrama ER, Scripts SQL y ayuda en reportes.

Olivier Viau Seifert - Entorno de la interfaz y reportes iniciales.

Adrián Ricardo González Muralles (23152) - Ayuda en reportes y ordenamiento del repositorio.


# Sistema Integrado de Reportes

**Descripción:**  
Aplicación de escritorio desarrollada en Python con Tkinter para la generación de reportes, visualización de gráficos y ejecución de consultas SQL sobre el sistema de reservas de canchas deportivas.

---

## 1. Requisitos

- **Python**: versión 3.8 o superior.  
- **PostgreSQL**: sistema funncional con la base de datos configurada con los .sql que se brindan en el repositorio.


## 2. Instalación y Entorno

### 2.1 Instalar dependencias
pip install tk psycopg2-binary tkcalendar matplotlib fpdf, etc.

## 3. Configuración de la conexión
Edite el bloque de conexión en el archivo admin.py con sus parámetros de PostgreSQL:

self.conn = psycopg2.connect(
    dbname="negroshima",
    user="postgres",
    password="0512",
    host="localhost",
    options='-c client_encoding=UTF8'
)
Ajuste los valores de dbname, user, password y host según su entorno.

## 4. Ejecución
Para iniciar la aplicación, ejecute:

python admin.py

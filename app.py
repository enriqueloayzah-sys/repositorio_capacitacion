import sqlite3
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)
DB_NAME = 'bd_instituto.db'

def obtener_db():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row  # Permite acceder a los campos por nombre de columna
    return conn


def preparar_tablas():
    conn = obtener_db()
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS cursos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            docente TEXT NOT NULL,
            duracion TEXT NOT NULL
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS estudiantes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            ci TEXT NOT NULL,
            email TEXT NOT NULL
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS inscripciones (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            curso_id INTEGER NOT NULL,
            estudiante_id INTEGER NOT NULL,
            fecha TEXT NOT NULL,
            FOREIGN KEY (curso_id) REFERENCES cursos (id),
            FOREIGN KEY (estudiante_id) REFERENCES estudiantes (id)
        )
    ''')
    
    conn.commit()
    conn.close()


@app.route('/')
def inicio():
    return redirect(url_for('listar_cursos'))

@app.route('/cursos')
def listar_cursos():
    conn = obtener_db()
    cursos = conn.execute('SELECT * FROM cursos').fetchall()
    conn.close()
    return render_template('cursos.html', cursos=cursos)

@app.route('/cursos/nuevo', methods=['GET', 'POST'])
def nuevo_curso():
    if request.method == 'POST':
        nombre = request.form['nombre']
        docente = request.form['docente']
        duracion = request.form['duracion']
        
        conn = obtener_db()
        conn.execute('INSERT INTO cursos (nombre, docente, duracion) VALUES (?, ?, ?)',
                     (nombre, docente, duracion))
        conn.commit()
        conn.close()
        return redirect(url_for('listar_cursos'))
        
    return render_template('form_curso.html')

@app.route('/estudiantes')
def listar_estudiantes():
    conn = obtener_db()
    estudiantes = conn.execute('SELECT * FROM estudiantes').fetchall()
    conn.close()
    return render_template('estudiantes.html', estudiantes=estudiantes)

@app.route('/estudiantes/nuevo', methods=['GET', 'POST'])
def nuevo_estudiante():
    if request.method == 'POST':
        nombre = request.form['nombre']
        ci = request.form['ci']
        email = request.form['email']
        
        conn = obtener_db()
        conn.execute('INSERT INTO estudiantes (nombre, ci, email) VALUES (?, ?, ?)',
                     (nombre, ci, email))
        conn.commit()
        conn.close()
        return redirect(url_for('listar_estudiantes'))
        
    return render_template('form_estudiante.html')


@app.route('/inscripciones')
def listar_inscripciones():
    conn = obtener_db()

    sql = '''
        SELECT i.id, c.nombre AS curso, e.nombre AS estudiante, i.fecha
        FROM inscripciones i
        JOIN cursos c ON i.curso_id = c.id
        JOIN estudiantes e ON i.estudiante_id = e.id
    '''
    inscripciones = conn.execute(sql).fetchall()
    conn.close()
    return render_template('inscripciones.html', inscripciones=inscripciones)

@app.route('/inscripciones/nueva', methods=['GET', 'POST'])
def nueva_inscripcion():
    conn = obtener_db()
    
    if request.method == 'POST':
        curso_id = request.form['curso_id']
        estudiante_id = request.form['estudiante_id']
        fecha = request.form['fecha']
        
        conn.execute('INSERT INTO inscripciones (curso_id, estudiante_id, fecha) VALUES (?, ?, ?)',
                     (curso_id, estudiante_id, fecha))
        conn.commit()
        conn.close()
        return redirect(url_for('listar_inscripciones'))
    
    cursos = conn.execute('SELECT * FROM cursos').fetchall()
    estudiantes = conn.execute('SELECT * FROM estudiantes').fetchall()
    conn.close()
    
    return render_template('form_inscripcion.html', cursos=cursos, estudiantes=estudiantes)


if __name__ == '__main__':
    preparar_tablas()
    app.run(debug=True)
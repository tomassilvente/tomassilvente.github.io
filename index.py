from django.shortcuts import render
from flask import Flask, render_template, request,flash, redirect, url_for, send_from_directory   
from flask_login import LoginManager, login_user, logout_user, login_required
from flask_mysqldb import MySQL
from flask_wtf.csrf import CSRFProtect
from importlib_metadata import files
from models.ModelUser import ModelUser
from models.entities.User import User
import os


#Conexion con Base de Datos

global num_recibo 
num_recibo = 0

app = Flask(__name__)
app.config['MYSQL_HOST'] = '127.0.0.1'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PORT'] = 3307
app.config['MYSQL_PASSWORD '] = 'tomassilvente10'
app.config['MYSQL_DB'] = 'inmobiliaria'

CARPETA = os.path.join('uploads')
app.config['CARPETA']=CARPETA

mysql = MySQL(app)
app.secret_key = 'mysecretkey'
csrf = CSRFProtect()

login_manager_app = LoginManager(app)
@login_manager_app.user_loader
def load_user(id):
    return ModelUser.get_by_id(mysql, id) 


#Rutas a pagina para publico
#
#
#Rutas en el NAVBAR

@app.route('/')
def home():
    cur = mysql.connection.cursor()
    cur.execute('SELECT * FROM casas WHERE estado = "alquiler"')
    dataAlq = cur.fetchall()
    cur.execute('SELECT * FROM casas WHERE estado = "venta"')
    dataVent = cur.fetchall()
    return render_template('index.html', casasAlq = dataAlq, casasVent = dataVent)

@app.route('/casaAlquiler')
def casaAlquiler():
    cur = mysql.connection.cursor()
    cur.execute('SELECT * FROM casas WHERE estado = "alquiler"')
    data = cur.fetchall()
    return render_template('casaAlquiler.html', casas = data)

@app.route('/casaVenta')
def casaVenta():
    cur = mysql.connection.cursor()
    cur.execute('SELECT * FROM casas WHERE estado = "venta"')
    data = cur.fetchall()
    return render_template('casaVenta.html', casas = data)

@app.route('/about')
def about():
    return render_template('about.html')


#Detalles de casas
#
@app.route('/detalles/<id>')
def detalles(id):
    cur = mysql.connection.cursor()
    cur.execute(f"SELECT * FROM casas WHERE id = {id}")
    data = cur.fetchall()
    return render_template('detalles.html', casa = data[0])



#Metodos de filtrado de busqueda
#
#
@app.route('/filtrar', methods=['POST'])
def filtrar():
    cur = mysql.connection.cursor()
    if request.method == 'POST':
        tipo = request.form['tipo']
        metros = request.form['metros']
        habitaciones = request.form['habitaciones']
        banos = request.form['banos']
        ambientes = request.form['ambientes']        
        if metros:
            if tipo:
                cur.execute(f'SELECT * FROM casas WHERE metros >= {metros} AND habitaciones >= {habitaciones} AND banos >= {banos} AND ambientes >= {ambientes} AND inmueble = "{tipo}" AND estado = "alquiler"')
                data = cur.fetchall()
                return render_template('casaAlquiler.html', casas = data)
            else:
                cur.execute(f'SELECT * FROM casas WHERE metros >= {metros} AND habitaciones >= {habitaciones} AND banos >= {banos} AND ambientes >= {ambientes} AND estado = "alquiler"')
                data = cur.fetchall()
                return render_template('casaAlquiler.html', casas = data)
        else:
            if tipo:
                cur.execute(f'SELECT * FROM casas WHERE  habitaciones >= {habitaciones} AND banos >= {banos} AND ambientes >= {ambientes} AND inmueble = "{tipo}" AND estado = "alquiler"')
                data = cur.fetchall()
                return render_template('casaAlquiler.html', casas = data)
            else:
                cur.execute(f'SELECT * FROM casas WHERE habitaciones >= {habitaciones} AND banos >= {banos} AND ambientes >= {ambientes} AND estado = "alquiler"')
                data = cur.fetchall()
                return render_template('casaAlquiler.html', casas = data)
            
@app.route('/filtrarVenta', methods=['POST'])
def filtrarVenta():
    cur = mysql.connection.cursor()
    if request.method == 'POST':
        tipo = request.form['tipo']
        metros = request.form['metros']
        habitaciones = request.form['habitaciones']
        banos = request.form['banos']
        ambientes = request.form['ambientes']        
        if metros:
            cur.execute(f'SELECT * FROM casas WHERE metros >= {metros} AND habitaciones >= {habitaciones} AND banos >= {banos} AND ambientes = {ambientes} AND inmueble = "{tipo}" AND estado = "venta"')
            data = cur.fetchall()
            return render_template('casaVenta.html', casas = data)
        else:
            cur.execute(f'SELECT * FROM casas WHERE habitaciones >= {habitaciones} AND banos >= {banos} AND ambientes >= {ambientes}  AND inmueble = "{tipo}" AND estado = "venta"')
            data = cur.fetchall()
            return render_template('casaVenta.html', casas = data)





#Metodos en la base de datos para la pagina de inicio
#
#
@app.route('/add_cliente_index', methods=['POST'])
def add_cliente():
     if request.method == 'POST':
        coment = request.form['coment']
        nombre = request.form['nombre']
        tel = request.form['tel']
        email = request.form['email']
        cur = mysql.connection.cursor()
        if not tel or not email or not nombre:
            flash("DATOS  FALTANTES.","danger")
            return redirect(url_for('home'))
        cur.execute('SELECT * FROM clientes')
        data = cur.fetchall()
        if coment:
            cur.execute("INSERT INTO mensajes (nombre, email, telefono, mensaje) VALUES (%s, %s, %s, %s)",
            (nombre, email, tel, coment))
            mysql.connection.commit()
        for cliente in data:
            if cliente[1] == nombre and cliente[3] == email:
                flash("Usuario ya existente!","danger")
                return redirect(url_for('home'))
        cur.execute('INSERT INTO clientes (nombre, tel, email) VALUES (%s, %s, %s)',
        (nombre, tel, email))
        mysql.connection.commit()
        flash("Gracias por su interes! Nos contactaremos en la brevedad.", "success")
        return redirect(url_for('home'))

@app.route('/add_cliente_detalles', methods=['POST','GET'])
def add_cliente_detalles():
     if request.method == 'POST':
        id = request.form['id']
        nombre = request.form['nombre']
        tel = request.form['tel']
        email = request.form['email']
        cur = mysql.connection.cursor()
        if not tel or not email or not nombre:
            flash("DATOS  FALTANTES.","danger")
            cur.execute(f'SELECT * FROM casas WHERE id = {id}')
            data = cur.fetchall()
            return render_template('detalles.html', casa = data[0])
        cur.execute('SELECT * FROM clientes')
        data = cur.fetchall()
        for cliente in data:
            if cliente[1] == nombre and cliente[3] == email:
                flash("Usuario ya existente!","danger")
                cur.execute(f'SELECT * FROM casas WHERE id = {id}')
                data = cur.fetchall()
                return render_template('detalles.html', casa = data[0])
        cur.execute('INSERT INTO clientes (nombre, tel, email) VALUES (%s, %s, %s)',
        (nombre, tel, email))
        mysql.connection.commit()
        flash('Datos enviados!')
        cur.execute(f'SELECT * FROM casas WHERE id = {id}')
        data = cur.fetchall()
        return render_template('detalles.html', casa = data[0])

#Pagina administrativa
#Rutas de las paginas
@app.route('/admin')
def admin():
    return redirect(url_for('login'))



@app.route('/recibo', methods=['POST','GET'])
@login_required
def recibo():
    cur = mysql.connection.cursor()
    cur.execute("SELECT nombre, MAX(id) AS id FROM recibos")
    data = cur.fetchone()
    num = data[1]
    newnum = num + 1
    nombre = "nombre "
    cur.execute(f'INSERT INTO recibos (nombre) VALUES ({nombre})')
    mysql.connection.commit()
    return render_template('recibo.html', recibo = newnum )

@app.route('/introAdmin')
@login_required
def introAdmin():
    return render_template('introAdmin.html')


@app.route('/crearCasa')
@login_required
def crearCasa():
    return render_template('crearCasa.html')

@app.route('/listadoCasas')
@login_required
def listadoCasas():
    cur = mysql.connection.cursor()
    cur.execute('SELECT * FROM casas ORDER BY direccion ASC ')
    data = cur.fetchall()
    return render_template('listadoCasas.html', casas = data)

@app.route('/filtrarCasa', methods=['POST'])
def filtrarCasas():
        nombre = request.form['casa']
        if nombre != "":
            cur = mysql.connection.cursor()
            cur.execute(f'SELECT * FROM casas WHERE direccion LIKE "%{nombre}%" ORDER BY direccion ASC')
            data = cur.fetchall()
            return render_template('listadoCasas.html', casas = data)
        else:
            return redirect(url_for('listadoCasas'))

@app.route('/mensajes')
@login_required
def mensajes():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM mensajes ORDER BY id DESC")
    data = cur.fetchall()
    return render_template('mensaje.html', mensajes=data)

@app.route('/adminAlq')
@login_required
def adminAlq():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM alquileres")
    data = cur.fetchall()
    return render_template('adminAlq.html', alquileres = data)

@app.route('/crearCliente')
@login_required
def crearCliente():
    return render_template('crearCliente.html')

@app.route('/listadoClientes')
@login_required
def listadoClientes():
    cur = mysql.connection.cursor()
    cur.execute('SELECT * FROM clientes ORDER BY nombre ASC')
    data = cur.fetchall()
    return render_template('listadoClientes.html', clientes = data)

@app.route('/filtrarCliente', methods=['POST'])
def filtrarCliente():
        nombre = request.form['nombre']
        if nombre != "":
            cur = mysql.connection.cursor()
            cur.execute(f'SELECT * FROM clientes WHERE nombre LIKE "%{nombre}%" ORDER BY nombre ASC')
            data = cur.fetchall()
            return render_template('listadoClientes.html', clientes = data)
        else:
            return redirect(url_for('listadoClientes'))

#METODOS PARA LOGGEO Y ERRORES DE LOGGEO A ADMINISTRACION
#
#
@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        user = User(0, request.form['user'], request.form['password'])
        logged_user = ModelUser.login(mysql, user)
        if logged_user != None:
            if logged_user.password:
                flash(f'BIENVENID@!',"success") 
                login_user(logged_user)
                return redirect('/introAdmin')
            else:
                flash("Contraseña incorrecta","danger")
                return render_template('login.html')
        else:
            flash("Usuario vacío o incorrecto","danger")
            return render_template('login.html')
    else:
        
        return render_template('login.html')

@app.route('/logout')
def logout():
    logout_user()
    flash("Sesion cerrada.","danger")
    return redirect(url_for('login'))

def status_401(error):
    return redirect(url_for('login'))

def status_404(error):
    return "<h1> Pagina no encontrada </h1>"

#METODOS PARA LA BASE DE DATOS
#
#
#Metodos para Creacion/ Edicion/ Eliminacion de casas
@app.route('/uploads/<nombreFoto>')
@login_required
def uploads(nombreFoto):
    return send_from_directory(app.config['CARPETA'], nombreFoto)

@app.route('/addCasa', methods=['POST'])
@login_required
def addCasa ():
    if request.method == 'POST':
        image_url = request.files['image_url']
        descrip = request.form['descrip']
        direccion = request.form['direccion']
        inmueble = request.form['inmueble']
        metros = request.form['metros']
        habitaciones = request.form['habitaciones']
        banos = request.form['banos']
        ambientes = request.form['ambientes']
        cochera = request.form['cochera']
        metros_cubiertos = request.form['metros_cubiertos']
        metros_patio = request.form['metros_patio']
        estado = request.form['estado']
        precio = request.form['precio']
        moneda = request.form['moneda']
        cur = mysql.connection.cursor()    
        if not image_url or not descrip or not direccion or not inmueble or not metros or not metros_cubiertos or not metros_patio or not banos or not habitaciones or not ambientes or not cochera or not estado or not precio or not moneda: 
            flash("DATOS FALTANTES!", "danger")
            return render_template('crearCasa.html')
        cur.execute('SELECT * FROM casas')
        data = cur.fetchall()
        for casa in data:
            if casa[2] == direccion:
                flash("PROPIEDAD YA EXISTENTE!","danger")
                return render_template('crearCasa.html')
        cur.execute('INSERT INTO casas (image_url, direccion, inmueble, metros, habitaciones, banos, ambientes, cochera, metros_cubiertos, metros_patio, descrip, estado, precio, moneda) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,%s, %s, %s)',
        (image_url.filename, direccion, inmueble, metros, habitaciones, banos, ambientes, cochera, metros_cubiertos, metros_patio, descrip, estado, precio, moneda))
                #for a in range(len(request.files['image_url'])):
                #name = request.files["image_url"].filename
                #image_url.save("uploads/"+name)
                #cur.execute(f'INSERT INTO imagenes (img{a+1}) = {name}')
        mysql.connection.commit()
        flash("INMUEBLE GUARDADO EXITOSAMENTE!", "success")
        return render_template('crearCasa.html')
            
        
@app.route('/deleteCasa/<string:id>')
@login_required
def deleteCasa(id):
    cur = mysql.connection.cursor()
    cur.execute('DELETE FROM casas WHERE id={0}'.format(id))
    mysql.connection.commit()
    flash("CASA ELIMINADA!","danger")
    return redirect(url_for('listadoCasas'))       

@app.route('/editCasa/<id>')
@login_required
def editCasa(id):
    cur = mysql.connection.cursor()
    cur.execute(f"SELECT * FROM casas WHERE id = {id}")
    data = cur.fetchall()
    return render_template('editCasa.html', casa = data[0])

@app.route('/update/<id>', methods = ['POST'])
@login_required
def updateCasa(id):
    if request.method == 'POST':        
        cur = mysql.connection.cursor()
        id = request.form['id']
        direccion = request.form['direccion']
        inmueble = request.form['inmueble']
        metros = request.form['metros']
        habitaciones = request.form['habitaciones']
        banos = request.form['banos']
        ambientes = request.form['ambientes']
        cochera = request.form['cochera']
        metros_cubiertos = request.form['metros_cubiertos']
        metros_patio = request.form['metros_patio']
        descrip = request.form['descrip']
        estado = request.form['estado']
        precio = request.form['precio']
        moneda = request.form['moneda']
        if not descrip or not direccion or not inmueble or not metros or not metros_cubiertos or not metros_patio or not banos or not habitaciones or not ambientes or not cochera or not estado or not precio or not moneda: 
            flash("DATOS FALTANTES!", "danger")
            cur.execute(f'SELECT * FROM casas WHERE id = {id}')
            data = cur.fetchall()
            return render_template('editcasa.html', casa = data[0])
        cur.execute('SELECT * FROM casas')
        data = cur.fetchall()
        cur.execute("""
            UPDATE casas
            SET
                direccion = %s,
                inmueble = %s,
                metros = %s,
                habitaciones = %s,
                banos = %s,
                ambientes = %s,
                cochera = %s,
                metros_cubiertos = %s,
                metros_patio = %s,
                descrip = %s,
                estado = %s,
                precio = %s,
                moneda = %s
            WHERE id = %s
        """,(direccion, inmueble, metros, habitaciones, banos, ambientes, cochera, metros_cubiertos, metros_patio, descrip, estado, precio, moneda, id))
        mysql.connection.commit()
        flash("Propiedad modificada satisfactoriamente!","success")
        return redirect(url_for('listadoCasas'))





#Metodos para Contactos
#
#
#
@app.route('/addCliente', methods=['POST'])
@login_required
def addCliente():
     if request.method == 'POST':
        nombre = request.form['nombre']
        tel = request.form['tel']
        email = request.form['email']
        direccion = request.form['direccion']
        fecha_nac = request.form['fecha_nac']
        cur = mysql.connection.cursor()
        if not tel or not email or not nombre:
            flash("DATOS  FALTANTES.","danger")
            return redirect(url_for('crearCliente'))
        cur.execute('SELECT * FROM clientes')
        data = cur.fetchall()
        for cliente in data:
            if cliente[1] == nombre and cliente[3] == email:
                flash("Usuario ya existente!","danger")
                return redirect(url_for('crearCliente'))
        cur.execute('INSERT INTO clientes (nombre, tel, email, direccion, fecha_nac) VALUES (%s, %s, %s, %s, %s)',
        (nombre, tel, email, direccion, fecha_nac))
        mysql.connection.commit()
        flash("Cliente creado satisfactoriamente!","success")
        return redirect(url_for('crearCliente'))

@app.route('/editCliente/<id>')
@login_required
def editCliente(id):
    cur = mysql.connection.cursor()
    cur.execute(f"SELECT * FROM clientes WHERE id = {id}")
    data = cur.fetchall()
    return render_template('editCliente.html', cliente = data[0])

@app.route('/updateCliente/<id>', methods = ['POST'])
@login_required
def update_cliente(id):
    if request.method == 'POST':
        id = request.form['id']
        nombre = request.form['nombre']
        tel = request.form['tel']
        email = request.form['email']
        fecha_nac = request.form['fecha_nac']
        direccion = request.form['direccion']
        cur = mysql.connection.cursor()
        if not tel or not email or not nombre:
            flash("DATOS  FALTANTES.","danger")
            cur.execute(f'SELECT * FROM clientes WHERE id = {id}')
            data = cur.fetchall()
            return render_template('editCliente.html', cliente= data[0])
        cur.execute("""
            UPDATE clientes
            SET nombre = %s,
                tel = %s,
                email = %s,
                fecha_nac = %s,
                direccion = %s
            WHERE id = %s
        """,(nombre, tel, email, fecha_nac, direccion, id))
        mysql.connection.commit()
        flash("Cliente modificado satisfactoriamente!","success")
        return redirect(url_for('listadoClientes'))

@app.route('/deleteCliente/<string:id>')
@login_required
def deleteCliente(id):
    cur = mysql.connection.cursor()
    cur.execute('DELETE FROM clientes WHERE id={0}'.format(id))
    mysql.connection.commit()
    flash("Cliente eliminado!","danger")
    return redirect(url_for('listadoClientes'))


#METODOS PARA MANEJO DE ALQUILERES
#
#
@app.route('/agregarAlquiler')
@login_required
def agregarAlquiler():
    cur = mysql.connection.cursor()
    cur.execute('SELECT * FROM clientes')
    clientess = cur.fetchall()
    cur.execute('SELECT  * FROM casas')
    casass = cur.fetchall()
    
    return render_template('agregarAlquiler.html', clientes = clientess, casas = casass)

@app.route('/addAlquiler', methods=['POST'])
@login_required
def addAlquiler():
    if request.method == 'POST':
        locador = request.form['dueno']
        locatorio = request.form['inquilino']
        precio = request.form['precio']
        dia_pago = request.form['dia']
        casa = request.form['casa']
        cur = mysql.connection.cursor()
        if not locador or not locatorio or not casa:
            flash("DATOS FALTANTES!", "danger")
            return redirect(url_for('agregarAlquiler'))
        if locador == locatorio:
            flash("Una persona no puede alquilarse a si misma!", "danger")
            return redirect(url_for('agregarAlquiler'))
        cur.execute('SELECT * FROM alquileres')
        data = cur.fetchall()
        for casas in data:
            if casas[0] == casa:
                flash("PROPIEDAD YA ALQUILADA!","danger")
                return redirect(url_for('agregarAlquiler'))
        cur.execute('INSERT INTO alquileres (propiedad, dueno, inquilino, precio, dia_pago) VALUES(%s, %s, %s, %s, %s)',
        (casa, locador, locatorio, precio, dia_pago))
        mysql.connection.commit()
        flash("Alquiler Agregado!","success")
        return redirect(url_for('adminAlq'))

@app.route('/deleteAlquiler/<string:propiedad>')
@login_required
def deleteAlquiler(propiedad):
    cur = mysql.connection.cursor()
    cur.execute(f'DELETE FROM alquileres WHERE propiedad = "{propiedad}"'.format(propiedad))
    mysql.connection.commit()
    flash("Alquiler eliminado!","danger")
    return redirect(url_for('adminAlq'))



@app.route('/actualizarPago/<propiedad>', methods=['GET','POST'])
@login_required
def actualizarPago(propiedad):
    if request.method == 'POST':
        pago = request.form['pago']
        liquidacion = request.form['liq']
        cur = mysql.connection.cursor()
        cur.execute('UPDATE alquileres SET pago = %s, liquidacion = %s WHERE propiedad = %s',(pago, liquidacion, propiedad))
        mysql.connection.commit()
        flash("Actualizado!","success")
        return redirect(url_for('adminAlq'))

#Mensaje Borrar
@app.route('/deleteMensaje/<string:id>')
@login_required
def deleteMensaje(id):
    cur = mysql.connection.cursor()
    cur.execute(f'DELETE FROM mensajes WHERE id = "{id}"'.format(id))
    mysql.connection.commit()
    flash("Mensaje eliminado!","danger")
    return redirect(url_for('mensajes'))


#Iniciador de la aplicacion Web
#
#
if __name__ == '__main__':
    
    app.register_error_handler(401,status_401)
    app.register_error_handler(404,status_404)
    app.run(debug=True)
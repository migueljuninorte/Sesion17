import os

import yagmail as yagmail
from flask import Flask, render_template, flash, request, redirect, url_for, jsonify
import utils
from db import get_db, close_db
from formularios import Contactenos
from message import mensajes
from sqlite3 import Error

app = Flask( __name__ )
app.secret_key = os.urandom( 24 )


@app.route( '/' )
def index():
    return render_template( 'login.html' )


@app.route( '/register', methods=('GET', 'POST') )
def register():
    try:
        if request.method == 'POST':
            username = request.form['usuario']
            password = request.form['password']
            email = request.form['email']
            error = None
            db = get_db() #Conectarse a la base de datos

            if not utils.isUsernameValid( username ):
                error = "El usuario debe ser alfanumerico o incluir solo '.','_','-'"
                flash( error )
                return render_template( 'register.html' )

            if not utils.isPasswordValid( password ):
                error = 'La contraseña debe contenir al menos una minúscula, una mayúscula, un número y 8 caracteres'
                flash( error )
                return render_template( 'register.html' )

            if not utils.isEmailValid( email ):
                error = 'Correo invalido'
                flash( error )
                return render_template( 'register.html' )

            #Preguntar si el correo no ha sido registrado anteriormente
            if db.execute( 'SELECT id FROM usuarios WHERE correo = ?', (email,) ).fetchone() is not None:
                error = 'El correo ya existe'.format( email )
                flash( error )
                return render_template( 'register.html' )

            db.execute(
                'INSERT INTO usuarios (usuario, correo, contraseña) VALUES (?,?,?)',
                (username, email, password)
            )
            db.commit()
            close_db()
            # yag = yagmail.SMTP('micuenta@gmail.com', 'clave') #modificar con tu informacion personal
            # yag.send(to=email, subject='Activa tu cuenta',
            #        contents='Bienvenido, usa este link para activar tu cuenta ')
            flash( 'Revisa tu correo para activar tu cuenta' )
            return render_template( 'login.html', user_created="El usuario ha sido creado" )
        return render_template( 'register.html' )
    except:
        return render_template( 'register.html' )


@app.route( '/login', methods=('GET', 'POST') )
def login():
    try:
        if request.method == 'POST':
            db = get_db()
            error = None
            username = request.form['usuario']
            password = request.form['password']

            if not username:
                error = 'Debes ingresar el usuario'
                flash( error )
                return render_template( 'login.html' )

            if not password:
                error = 'Contraseña requerida'
                flash( error )
                return render_template( 'login.html' )

            user = db.execute(
                'SELECT * FROM usuario WHERE usuario = ? AND contraseña = ?', (username, password)
            ).fetchone()

            if user is None:
                error = 'Usuario o contraseña inválidos'
            else:
                return redirect( 'mensajes' )
            flash( error )
        return render_template( 'login.html' )
    except:
        return render_template( 'login.html' )


@app.route( '/contactUs', methods=('GET', 'POST') )
def contactUs():
    form = Contactenos()
    return render_template( 'contactus.html', titulo='Contactenos', form=form )

@app.route('/mensajes')
def mensajes():
    try:
        db = get_db()
        resultado = db.execute("SELECT message_id AS 'Codigo Mensaje', from_id AS 'Código Remitente', u1.usuario AS 'Usuario Remitente', " +
                                    " to_id AS 'Código destinatario', u2.usuario AS 'Usuario Destinatario', asunto AS 'Asunto', " +
                                    " mensaje AS 'Mensaje' " +
                                " FROM usuarios u1, usuarios u2, mensajes " +
                                " WHERE from_id = u1.id AND to_id = u2.id;").fetchall()
        close_db()
        return render_template('mensajes.html',titulo="Mensajes", data = resultado)
    except Error as e:    
        return render_template('error.html', error=e)

@app.route( '/message', methods=('GET', 'POST') )
def message():
    print( "Retrieving info" )
    return jsonify( {'mensajes': mensajes} )


if __name__ == '__main__':
    app.run(debug=True, port=80)

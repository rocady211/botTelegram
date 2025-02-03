from flask import Blueprint, jsonify, request
from ..models.configDb import User, db
from flask_bcrypt import Bcrypt
from datetime import datetime
from flask_jwt_extended import create_access_token
from flask_jwt_extended import get_jwt_identity
from flask_jwt_extended import jwt_required


def auth_bluePrint():
    from app import app

    app.config["JWT_SECRET_KEY"] = "super-secret"  # Change this!

    auth_page = Blueprint('auth_page', __name__, template_folder='templates')

    bcrypt = Bcrypt(app)

    @auth_page.route('/login', methods= ["POST"])
    def login():
        data = request.json

        if('correo' not in data or 'contraseña' not in data):
            return jsonify({'ok': False, 'message': 'Por favor ingrese correctamente los datos: correo, contraseña'}),400

        userExist = User.query.filter_by(correo=data['correo']).first()

        if(not userExist):
            return jsonify({'ok': False, 'message': 'No existe ningun usuario con ese correo'})
        
        if userExist and not bcrypt.check_password_hash(userExist.contraseña, data['contraseña']):
            return jsonify({'ok': False, 'message': 'Contraseña incorrecta'}), 400

        access_token = create_access_token(identity = data['correo'])

        user_data = userExist.__dict__.copy() 
        user_data.pop('_sa_instance_state', None) 
        user_data.pop('contraseña', None) 

        return jsonify({'ok': True, "token" : access_token, 'data': user_data})

    @auth_page.route('/register', methods= ["POST"])
    def register():
        data = request.json

        if('correo' not in data or 'contraseña' not in data or 'nombre' not in data or 'photo' not in data):
            return jsonify({'ok': False, 'message': 'Por favor ingrese correctamente los datos: correo, contraseña, nombre, photo'}),400
         
        existUserName = User.query.filter_by(correo = data['correo']).first()
        
        if(existUserName) :
            return jsonify({"ok":False, "message": "Error, ya existe un usuario con ese correo"})
        
        pw_hash = bcrypt.generate_password_hash(data['contraseña'])

        newUser = User(
            contraseña=pw_hash,
            correo= data['correo'],
            nombre= data['nombre'],
            photo= data['photo'],
            createdAt= datetime.now()
        )

        db.session.add(newUser)
        db.session.commit()

        return jsonify({"ok":True, "message": "Usuario creado exitosamente"})

    @auth_page.route('/getUserInfo', methods=['GET'])
    @jwt_required()
    def getUserInfo():
        currentUser = get_jwt_identity()

        userExist = User.query.filter_by(correo = currentUser).first()

        user_data = userExist.__dict__.copy() 
        user_data.pop('_sa_instance_state', None) 
        user_data.pop('contraseña', None) 

        return jsonify({'ok': True, 'data': user_data})

    return auth_page
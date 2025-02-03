from flask import Blueprint, jsonify
from ..models.configDb import UserTelegram

def userTelegram_bp():
    
    userTelegram_bp = Blueprint('userTelegram_bp', __name__, template_folder='templates')


    @userTelegram_bp.route('/predict', methods = ['POST'])
    def create(userInfo):
        return jsonify({"ok":True})
    
    return userTelegram_bp

def guardar_usuario_telegram(userData, chatData):
    from app import db

    findUser = UserTelegram.query.filter_by(userId = userData.id).first()
    if(findUser) :
        return 'Por favor espere a recibir nuestras predicciones!'
    else:
        userNew = UserTelegram(
            nombre= userData.first_name + " " + userData.last_name,
            chat_id= chatData.id,
            suscribed= False,
            userId= userData.id,
        )
        db.session.add(userNew)
        db.session.commit()
        return 'Ya hemos enviado tu solicitud para recibir predicciones, le informaremos a la brevedad'
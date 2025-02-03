from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import BigInteger
db = SQLAlchemy()
from datetime import datetime
from enum import Enum

class UserTelegram(db.Model): 
    id = db.Column(db.Integer, primary_key=True)
    userId = db.Column(BigInteger, nullable = False)
    nombre = db.Column(db.String(70), nullable = False)
    suscribed = db.Column(db.Boolean, default = True)
    chat_id = db.Column(BigInteger, nullable = False)
    
    def __init__(self, nombre, suscribed, chat_id, userId):
        self.nombre = nombre
        self.suscribed = suscribed
        self.chat_id = chat_id
        self.userId = userId


    def serialize(self):
        return {
        "id":self.id,
        "nombre":self.nombre,
        "suscribed": self.suscribed,
        "chat_id": self.chat_id,
        "userId": self.userId
        }
    
class User(db.Model): 

    id = db.Column(db.Integer, primary_key=True)
    photo = db.Column(db.String(70), nullable = True)
    nombre = db.Column(db.String(70), nullable = False)
    correo = db.Column(db.String(100), nullable = False)
    contraseña = db.Column(db.String(500), nullable = False)
    createdAt = db.Column(db.Date(), default = datetime.now())

    def __init__(self,nombre,photo, correo, contraseña, createdAt):
        self.nombre = nombre
        self.photo = photo
        self.correo = correo
        self.contraseña = contraseña
        self.createdAt = createdAt

    def serialize(self):
        return {
        "id":self.id,
        "photo":self.photo,
        "nombre":self.nombre ,
        "correo":self.correo ,
        "contraseña":self.contraseña ,
        "createdAt":self.createdAt ,
        }

class ResultadoEnum(Enum):
    GANA_A = 1
    GANA_B = 0
    EMPATE = 2  

class Team_Prediction(db.Model):
    __tablename__ = 'team_prediction'

    id = db.Column(db.Integer, primary_key=True,)
    name = db.Column(db.String(100), nullable=False)
    id_infoApi = db.Column(db.String(100), nullable=False)

    def __init__(self,id,name,id_infoApi) :
        self.id = id
        self.name = name
        self.id_infoApi = id_infoApi
    
    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "id_infoApi": self.id_infoApi
        }

class Prediction_Bot(db.Model): 
    id = db.Column(db.Integer, primary_key=True)
    teamA_id = db.Column(db.Integer, db.ForeignKey('team_prediction.id'), nullable=False)
    teamB_id = db.Column(db.Integer, db.ForeignKey('team_prediction.id'), nullable=False)
    league_id = db.Column(db.Integer, nullable=False)
    tiros = db.Column(db.Integer, nullable=False)
    es_local_A = db.Column(db.Boolean, nullable=False, default=True)  
    goles_A = db.Column(db.Integer, nullable=False)
    goles_B = db.Column(db.Integer, nullable=False)
    corners = db.Column(db.Integer, nullable=False)
    posesion = db.Column(db.Integer, nullable=False)
    precision = db.Column(db.Integer, nullable=False)
    resultado = db.Column(db.Integer, nullable=False)
    clima = db.Column(db.Integer, nullable=False)
    fecha = db.Column(db.Date(), nullable = False, default = datetime.now())

    teamA = db.relationship("Team_Prediction", foreign_keys=[teamA_id], backref='teamA_prediction', lazy='joined')
    teamB = db.relationship("Team_Prediction", foreign_keys=[teamB_id], backref='teamB_prediction', lazy='joined')
    
    def __init__(self, teamA, teamB, tiros, goles_A, goles_B, corners, posesion, precision, clima, fecha):
        self.teamA = teamA
        self.teamB = teamB
        self.tiros = tiros
        self.goles_A = goles_A
        self.goles_B = goles_B
        self.corners = corners
        self.posesion = posesion
        self.precision = precision
        self.clima = clima
        self.es_local_A = True  
        self.resultado = self.calcular_resultado()  
        self.fecha = self.fecha()  

    def calcular_resultado(self):
        if self.goles_A > self.goles_B:
            return ResultadoEnum.GANA_A.value
        elif self.goles_A < self.goles_B:
            return ResultadoEnum.GANA_B.value
        else:
            return ResultadoEnum.EMPATE.value 

    def serialize(self):
        return {
            "id": self.id,
            "teamA": self.teamA,
            "teamB": self.teamB,
            "tiros": self.tiros,
            "goles_A": self.goles_A,
            "goles_B": self.goles_B,
            "corners": self.corners,
            "posesion": self.posesion,
            "precision": self.precision,
            "clima": self.clima,
            "resultado": self.serialize_resultado(),
            "fecha": self.fecha
        }

    def serialize_resultado(self):
        if self.resultado == ResultadoEnum.GANA_A.value:
            return "Gana Equipo A"
        elif self.resultado == ResultadoEnum.GANA_B.value:
            return "Gana Equipo B"
        else:
            return "Empate"  



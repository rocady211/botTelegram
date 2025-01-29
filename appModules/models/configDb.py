from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class User(db.Model): 

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(70), nullable = False)
    tel = db.Column(db.Integer, nullable = False)

    def __init__(self,nombre,tel):
        self.nombre = nombre
        self.tel = tel

    def serialize(self):
        return {
        "id":self.id,
        "nombre":self.nombre,
        "tel":self.tel ,
        }
    

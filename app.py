from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_apscheduler import APScheduler
from flask_cors import CORS
import time
import telebot
from appModules.function_routes.test import simple_page
from appModules.function_routes.auth import auth_bluePrint
from appModules.function_routes.userTelegram import userTelegram_bp, guardar_usuario_telegram
from appModules.function_routes.predict import predict_bluePrint
import threading
from appModules.models.configDb import db
from flask import request
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error
from sklearn.linear_model import LogisticRegression
import joblib
from sklearn.metrics import accuracy_score
from leagues.utils import get_famous_matches, get_info_last_5_match, get_famous_matches_with_statistics
from flask_jwt_extended import JWTManager
from leagues.getRandomGames import getRandomsGames
API_TOKEN = '7888643022:AAE8QsTx3I-7xXTGYVYHKeFQg84ycQ_65JA'

app = Flask(__name__)  

CORS(app)
jwt = JWTManager(app)
# config db
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://rodrigo:oliverman12@localhost/botTelegram"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config['SECRET_KEY'] = 'secret!'

db.init_app(app)
migrate = Migrate(app, db)

scheduler = APScheduler()

bot = telebot.TeleBot(API_TOKEN)

webhook_url = 'https://9740-2800-a4-c0e2-1c00-c51-51f2-666d-6062.ngrok-free.app/webhook'

bot.remove_webhook() 

time.sleep(1)  
bot.set_webhook(url=webhook_url) 

auth = auth_bluePrint()
predict = predict_bluePrint()
userTelegram = userTelegram_bp()

app.register_blueprint(auth)
app.register_blueprint(simple_page)
app.register_blueprint(userTelegram)
app.register_blueprint(predict)


@app.route('/webhook', methods=['POST'])
def webhook():
    print("xdxd")
    json_str = request.get_data().decode('UTF-8')  
    update = telebot.types.Update.de_json(json_str)  # Convertir el JSON en un objeto Update
    bot.process_new_updates([update])  # Procesar la actualización

    return "OK"

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    with app.app_context():
        messsage_response = guardar_usuario_telegram(message.from_user, message.chat)
        bot.reply_to(message, messsage_response)

# data = pd.DataFrame({
#     "ultimos_5_victorias_A": [3, 2, 4, 1, 2, 5, 1, 2, 3, 0],
#     "tiros": [10, 8, 12, 6, 9, 14, 7, 8, 11, 5],
#     "posesion": [48, 45, 50, 42, 47, 52, 44, 46, 49, 40],
#     "ultimos_5_victorias_B": [2, 1, 3, 0, 1, 4, 0, 1, 2, 0],
#     "es_local_A": [1, 0, 1, 0, 1, 0, 1, 0, 1, 0],  # 1 = local, 0 = visitante
#     "clima": [0, 1, 0, 1, 0, 1, 0, 1, 0, 1],  # 0 = soleado, 1 = lluvioso , 2 = nublado, 3 = nevando
#     "goles_A": [2, 1, 3, 0, 2, 4, 1, 1, 3, 0],  # Goles en el partido de A
#     "goles_B": [2, 1, 3, 0, 2, 4, 1, 1, 3, 0],  # Goles en el partido de B
#     "corners": [5, 3, 7, 2, 4, 8, 3, 4, 6, 2],  # Corners en el partido
#     "precision": [45, 40, 50, 35, 42, 55, 38, 41, 48, 33],  # Precisión de tiros
#     "resultado": [1, 0, 1, 0, 1, 1, 0, 0, 1, 0]  # 1 = gana Equipo A, 0 = gana Equipo B
# })

# Ruta para entrenar el modelo
@app.route("/train", methods=["POST"])
def train():

    # Separar características (X) y etiquetas (y)
    X = data.drop(columns=["goles", "corners", "precision", "resultado"])
    y_goles = data["goles"]
    y_corners = data["corners"]
    y_precision = data["precision"]
    y_resultado = data["resultado"]

    # Dividir los datos en conjuntos de entrenamiento y prueba
    X_train, X_test, y_train_goles, y_test_goles = train_test_split(X, y_goles, test_size=0.2, random_state=42)
    _, _, y_train_corners, y_test_corners = train_test_split(X, y_corners, test_size=0.2, random_state=42)
    _, _, y_train_precision, y_test_precision = train_test_split(X, y_precision, test_size=0.2, random_state=42)
    _, _, y_train_resultado, y_test_resultado = train_test_split(X, y_resultado, test_size=0.2, random_state=42)

    # Entrenar modelo para predecir goles
    model_goles = LinearRegression()
    model_goles.fit(X_train, y_train_goles)
    y_pred_goles = model_goles.predict(X_test)
    print("MSE Goles:", mean_squared_error(y_test_goles, y_pred_goles))

    # Entrenar modelo para predecir corners
    model_corners = LinearRegression()
    model_corners.fit(X_train, y_train_corners)
    y_pred_corners = model_corners.predict(X_test)
    print("MSE Corners:", mean_squared_error(y_test_corners, y_pred_corners))

    # Entrenar modelo para predecir precisión
    model_precision = LinearRegression()
    model_precision.fit(X_train, y_train_precision)
    y_pred_precision = model_precision.predict(X_test)
    print("MSE Precisión:", mean_squared_error(y_test_precision, y_pred_precision))

    # Entrenar modelo para predecir resultado
    model_resultado = LogisticRegression()
    model_resultado.fit(X_train, y_train_resultado)
    y_pred_resultado = model_resultado.predict(X_test)
    print("Accuracy Resultado:", accuracy_score(y_test_resultado, y_pred_resultado))

    # Guardar los modelos entrenados
    joblib.dump(model_goles, 'modelo_goles.pkl')
    joblib.dump(model_corners, 'modelo_corners.pkl')
    joblib.dump(model_precision, 'modelo_precision.pkl')
    joblib.dump(model_resultado, 'modelo_resultado.pkl')

    return jsonify({"message": "Modelos entrenados y guardados correctamente"})

@app.route("/predict", methods=["POST"])
def predictCoso():

    # Crear el registro del enfrentamiento
    enfrentamiento = pd.DataFrame({
        "ultimos_5_victorias_A": [3, 2, 4, 1, 2, 5, 1, 2, 3, 0],
        "tiros": [10, 8, 12, 6, 9, 14, 7, 8, 11, 5],
        "posesion": [48, 45, 50, 42, 47, 52, 44, 46, 49, 40],
        "ultimos_5_victorias_B": [2, 1, 3, 0, 1, 4, 0, 1, 2, 0],
        "es_local_A": [1, 0, 1, 0, 1, 0, 1, 0, 1, 0],  # 1 = local, 0 = visitante
        "clima": [0, 1, 0, 1, 0, 1, 0, 1, 0, 1],  # 0 = soleado, 1 = lluvioso , 2 = nublado, 3 = nevando
        "goles": [2, 1, 3, 0, 2, 4, 1, 1, 3, 0],  # Goles en el partido
        "corners": [5, 3, 7, 2, 4, 8, 3, 4, 6, 2],  # Corners en el partido
        "precision": [45, 40, 50, 35, 42, 55, 38, 41, 48, 33],  # Precisión de tiros
        "resultado": [1, 0, 1, 0, 1, 1, 0, 0, 1, 0]  # 1 = gana Equipo A, 0 = gana Equipo B
    })

    # Cargar los modelos entrenados
    model_goles = joblib.load('modelo_goles.pkl')
    model_corners = joblib.load('modelo_corners.pkl')
    model_precision = joblib.load('modelo_precision.pkl')
    model_resultado = joblib.load('modelo_resultado.pkl')

    # Hacer predicciones para el enfrentamiento
    pred_goles_A = model_goles.predict(enfrentamiento)[0]
    pred_goles_B = model_goles.predict(enfrentamiento)[0]
    pred_corners = model_corners.predict(enfrentamiento)[0]
    pred_precision = model_precision.predict(enfrentamiento)[0]
    pred_resultado = model_resultado.predict(enfrentamiento)[0]

    # Devolver las predicciones
    return jsonify({
        "goles_equipo_A": float(pred_goles_A),
        "goles_equipo_B": float(pred_goles_B),
        "corners": float(pred_corners),
        "precision": float(pred_precision),
        "resultado": int(pred_resultado)  # 1 = gana Equipo A, 0 = gana Equipo B
    })

@app.route("/famous_matches", methods=["GET"])
def famous_matches():
    date_str = request.args.get("date")
    matches_response = get_famous_matches(date_str)  
    matches = matches_response.get_json() 
    print('los matchs son', matches)
    
    random_games = getRandomsGames(2, matches) 
    return jsonify(random_games) 

@app.route("/famous_matches_with_statics", methods=["GET"])
def famous_matches_statics():
    date_str = request.args.get("date")
    matches = get_famous_matches_with_statistics(date_str)

    return matches

if __name__ == '__main__':
    app.run(debug=True, port=8000, host='0.0.0.0')
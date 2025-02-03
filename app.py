from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_apscheduler import APScheduler
from flask_cors import CORS
import telebot
from appModules.function_routes.test import simple_page
from appModules.models.configDb import db
from flask import request
# learn
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error
from sklearn.linear_model import LogisticRegression
import joblib
from sklearn.metrics import accuracy_score
from leagues.utils import get_famous_matches, get_info_last_5_match

API_TOKEN = '7888643022:AAE8QsTx3I-7xXTGYVYHKeFQg84ycQ_65JA'

app = Flask(__name__)  

CORS(app)

# config db
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://rodri:oliverman12@localhost:3306/bot_telegram"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config['SECRET_KEY'] = 'secret!'

db.init_app(app)
migrate = Migrate(app, db)

scheduler = APScheduler()

bot = telebot.TeleBot(API_TOKEN)
WEBHOOK_URL = 'https://4d0a-2800-a4-c146-fe00-7c85-d483-1900-e18a.ngrok-free.app/handleMessage'

bot.remove_webhook()
bot.set_webhook(url=WEBHOOK_URL)

app.register_blueprint(simple_page)

@app.route('/handleMessage', methods=['POST'])
def home():
    data = request.get_json()
    print('xdddddd', data)
    print('llego el message')
    return 'xd'


@app.route("/predict", methods=["POST"])
def predictCoso():

    data = pd.DataFrame({
        "goles_prom": [1.8, 1.2, 2.0, 0.9, 1.5, 2.2, 1.1, 1.4, 1.9, 0.8],
        "tiros_prom": [14, 10, 16, 8, 12, 18, 9, 11, 15, 7],
        "posesion_prom": [55, 48, 60, 45, 50, 58, 47, 52, 57, 43],
        "ultimos_5_victorias": [3, 2, 4, 1, 2, 5, 1, 2, 3, 0],
        "resultado": [1, 0, 1, 0, 1, 1, 0, 0, 1, 0]  # 1 = ganó, 0 = perdió
    })


    X = data.drop(columns=["resultado"]) 
    y = data["resultado"]

    # x train e y train son los valorss en este caso tiros, posesion que usara para encontrar una ecuacion que llegue a los resulttados

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.5, random_state=42)

    model = LogisticRegression()
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)

    # compara y_test( los resultados reales de ese 20%) con y pred, a ver si acerto o no 
    accuracy = accuracy_score(y_test, y_pred)

    print(accuracy)
    print("Predicciones:", y_pred)
    print("Resultados reales:", y_test)


    joblib.dump(model, 'modelo_entrenado.pkl')


@app.route("/predictPartido", methods=["POST"])
def predict():
    model = joblib.load('modelo_entrenado.pkl')

    input_data = request.get_json()
    
    tiros = input_data["tiros"]
    posesion = input_data["posesión"]
    
    X_new = np.array([[tiros, posesion]])
    
    prediction = model.predict(X_new)[0]

    return jsonify({"predicción": int(prediction)})

@app.route("/famous_matches", methods=["GET"])
def famous_matches():
    date_str = request.args.get("date")
    matches = get_famous_matches(date_str)

    return matches


@app.route("/get_last_5_matches", methods=["GET"])
def last_five_matches():
    matches = get_info_last_5_match()

    return matches

if __name__ == '__main__':
    app.run(debug=True, port=8000, host='0.0.0.0')
from flask import Blueprint, jsonify
from ..models.configDb import Prediction_Bot, Team_Prediction
     
def predict_bluePrint():
    
    predict_bluePrint = Blueprint('predict_bluePrint', __name__, template_folder='templates')


    @predict_bluePrint.route('/predict', methods = ['POST'])
    def create():
        return jsonify({"ok":True})
    
    @predict_bluePrint.route('/predict/<int:id_predict>', methods = ['GET'])
    def find(id_predict):
        return jsonify({"ok":True})
    
    @predict_bluePrint.route('/predict', methods = ['GET'])
    def findAll():
        return jsonify({"ok":True})
    
    @predict_bluePrint.route('/predict', methods = ['POST'])
    def delete():
        return jsonify({"ok":True})

    return predict_bluePrint

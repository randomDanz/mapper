from flask import Flask, request, render_template, Response, url_for
from flask import jsonify
from flask_sqlalchemy import SQLAlchemy
# from flask_cors import CORS
import json
import requests
import numpy as np
import math as m
import matplotlib.pyplot as plt
import io
import base64
import re
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure


app = Flask(__name__)

# CORS(app)                               use this for cross site access
# cors = CORS(app, resources = {
#     r"/*" : {
#         "origins":"*"
#     }
# })

ENV = 'prod'

if ENV == 'dev':
    #local db
    app.debug = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:swathcompony@localhost/mapper'
else:
    #production db
    app.debug = False
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://yvgkihlbkpsmst:53d47ddb62fcb990fe995629e36f7fe6e44082cb2810db9d4ffb05aeeb7e6b66@ec2-18-206-84-251.compute-1.amazonaws.com:5432/d22v96fhiuv3n5'
     
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class dbModel(db.Model):
    __tablename__ = 'mapperData'
    id = db.Column(db.Integer, primary_key=True)
    angle = db.Column(db.Integer)
    distance = db.Column(db.Float)
    mapNumber = db.Column(db.Integer)
    timeStamp = db.Column(db.Integer)

    def __init__(self, angle, distance, mapNumber, timeStamp):
        self.angle = angle
        self.distance = distance
        self.mapNumber = mapNumber
        self.timeStamp = timeStamp


@app.route('/', methods=['GET'])
def index():
    x = 'No'
    
    return render_template('index.html', x = x)

@app.route('/api/storeData', methods=['POST'])
def store():
    content = json.loads(request.data)
    for i in content['coordinates']:
        angl = i['angle']
        dist = i['dist']
        mapNum = i['map_no']
        timeSt = i['time_stamp']
        data = dbModel(angl, dist, mapNum, timeSt)
        db.session.add(data)
        db.session.commit()
    return 'SUCCESS'

@app.route('/api/getData', methods=['GET'])
def getData():
    print(request.data)
    content = json.loads(request.data)
    returnData = dbModel.query.filter_by(mapNumber=content).all()
    a = []
    var = ['angle','dist','map_no','time_stamp']
    for i in range(0,len(returnData)):
        b = {}
        b[var[0]] = returnData[i].angle
        b[var[1]] = returnData[i].distance
        b[var[2]] = returnData[i].mapNumber
        b[var[3]] = returnData[i].timeStamp
        a.append(b)
    print(json.dumps(a))
    resp = jsonify(a)
    resp.status_code = 200
    #resp = Response(js, status=200, mimetype='application/json')
    return resp

def createMap(data):
    d = {}
    d['coordinates'] = data
    angle=[]
    dist=[]
    for i in d['coordinates']:
        phi=i['angle']
        rho=i['dist']
        x=np.deg2rad(phi)
        angle.append(x)
        dist.append(rho)
    plt.polar(angle,dist)#Figure1
    #Figure2
    fig = plt.figure(frameon=False)
    ax = fig.add_subplot(111, polar=True)
    c = ax.plot(angle, dist, color='r', linewidth=3)
    ax.set_thetamin(0)
    ax.set_thetamax(180)
    ax.set_theta_offset(2*np.pi)
    ax.axis('off')
    # Display the Polar plot
    # plt.show()

    # Convert plot to PNG image
    pngImage = io.BytesIO()
    FigureCanvas(fig).print_png(pngImage)
    
    # Encode PNG image to base64 string
    pngImageB64String = "data:image/png;base64,"
    pngImageB64String += base64.b64encode(pngImage.getvalue()).decode('utf8')
    
    return pngImageB64String

@app.route('/search', methods=['POST'])
def search():
    x = 1
    if request.method == 'POST':
        print(request.form['search'])
        data = re.search(r'[0-9]+',request.form['search'])
        if data != None:
            x = 0
            url = 'https://mapper-api.herokuapp.com/api/getData'
            # url = 'http://127.0.0.1:5000/api/getData'
            x = requests.get(url,data=request.form['search'])
            print(x.text)
            image = createMap(json.loads(x.text))
            return render_template('index.html',  x = 0, data=json.loads(x.text) , image = image)
        return render_template('index.html', x = x)


if __name__ == '__main__':
    app.run()
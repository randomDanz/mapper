from flask import Flask, request
from flask import jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

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
    angle = db.Column(db.Float)
    distance = db.Column(db.Integer)
    mapNumber = db.Column(db.Integer)
    timeStamp = db.Column(db.Integer)

    def __init__(self, angle, distance, mapNumber, timeStamp):
        self.angle = angle
        self.distance = distance
        self.mapNumber = mapNumber
        self.timeStamp = timeStamp

@app.route('/')
def index():
    return 'Hello!'

@app.route('/api/storeData', methods=['POST'])
def store():
    if request.method == 'POST':
        angl = request.form['angle']
        dist = request.form['dist']
        mapNum = request.form['map_no']
        timeSt = request.form['time_stamp']
    print(angl, dist, mapNum, timeSt)
    data = dbModel(angl, dist, mapNum, timeSt)
    db.session.add(data)
    db.session.commit()
    return 'Success'
    #return 'SUCCESS'

@app.route('/api/getData', methods=['GET'])
def getData():
    returnData = dbModel.query.all()
    print(returnData)
    return jsonify(returnData)

if __name__ == '__main__':
    app.run()
from flask import Flask,jsonify,request
import decodehex2
import re
import os
from dotenv import load_dotenv
load_dotenv('.env')

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'Optional default value')


@app.route('/', methods=['GET'])
def jsonhex():
    content = request.get_json()
    hexcode = content.get('hexcode')
    try:
        beacon = decodehex2.Beacon(hexcode)
    except decodehex2.HexError as err:
        return jsonify(error=[err.value,err.message])
    return jsonify(mid=beacon.get_mid(),country=beacon.get_country(),msgtype=beacon.type,tac=beacon.gettac(), beacontype=beacon.btype(),protocol=beacon.protocoltype())



@app.route('/decode/<hexcode>',methods=['GET'])
def api(hexcode):
    try:
        beacon = decodehex2.Beacon(hexcode)
    except decodehex2.HexError as err:
        return jsonify(error=[err.value,err.message])
    return jsonify(mid=beacon.get_mid(),country=beacon.get_country(),msgtype=beacon.type,tac=beacon.gettac(), beacontype=beacon.btype(),protocol=beacon.protocoltype())




if __name__ == '__main__':
    app.secret_key = 'my secret'
    app.run(debug=False)

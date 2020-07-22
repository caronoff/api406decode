from flask import Flask,jsonify,request
import decodehex2
import boto3
import os
from dotenv import load_dotenv
load_dotenv('.env')

USERS_TABLE = os.environ['USERS_TABLE']
client = boto3.client('dynamodb')

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'Optional default value')


@app.route('/json', methods=['POST'])
def jsonhex():
    req_data = request.get_json()
    hexcode = req_data['hexcode']
    try:
        beacon = decodehex2.Beacon(hexcode)
    except decodehex2.HexError as err:
        return jsonify(error=[err.value,err.message])
    return jsonify(mid=beacon.get_mid(),country=beacon.get_country(),msgtype=beacon.type,tac=beacon.gettac(), beacontype=beacon.btype(),protocol=beacon.protocoltype())



@app.route('/decode/<hexcode>',methods=['GET'])
def decode(hexcode):
    try:
        beacon = decodehex2.Beacon(hexcode)
    except decodehex2.HexError as err:
        return jsonify(error=[err.value,err.message])
    return jsonify(mid=beacon.get_mid(),country=beacon.get_country(),msgtype=beacon.type,tac=beacon.gettac(), beacontype=beacon.btype(),protocol=beacon.protocoltype())

@app.route('/',methods=['GET'])
def api():
    msg='hello world 4'
    return jsonify(msg=msg)


@app.route("/users/<string:user_id>")
def get_user(user_id):
    resp = client.get_item(
        TableName=USERS_TABLE,
        Key={
            'userId': { 'S': user_id }
        }
    )
    item = resp.get('Item')
    if not item:
        return jsonify({'error': 'User does not exist'}), 404

    return jsonify({
        'userId': item.get('userId').get('S'),
        'name': item.get('name').get('S')
    })


@app.route("/users", methods=["POST"])
def create_user():
    user_id = request.json.get('userId')
    name = request.json.get('name')
    if not user_id or not name:
        return jsonify({'error': 'Please provide userId and name'}), 400

    resp = client.put_item(
        TableName=USERS_TABLE,
        Item={
            'userId': {'S': user_id },
            'name': {'S': name }
        }
    )

    return jsonify({
        'userId': user_id,
        'name': name
    })





if __name__ == '__main__':
    app.secret_key = 'my secret'
    app.run(debug=False)

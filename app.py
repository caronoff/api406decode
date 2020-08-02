from flask import Flask,jsonify,request
import decodehex2
import boto3
import os
from dotenv import load_dotenv
load_dotenv('.env')
app = Flask(__name__)



app.secret_key = os.getenv('SECRET_KEY', 'Optional default value')

dynamodb = boto3.resource('dynamodb')
db = dynamodb.Table('myservice-dev')
hextable = dynamodb.Table('hexcode')

@app.route('/counter', methods=['GET'])
def counter_get():
    res = db.get_item(Key={'id': 'counter'})
    return jsonify({'counter': str(res['Item']['counter_value'])})

@app.route('/counter/increase', methods=['POST'])
def counter_increase():
    res = db.get_item(Key={'id': 'counter'})
    value = res['Item']['counter_value'] + 1
    res = db.update_item(    Key={'id': 'counter'},    UpdateExpression='set counter_value=:value',    ExpressionAttributeValues={':value': value},  )
    return jsonify({'counter': str(value)})


@app.route('/json', methods=['PUT'])
def jsonhex():
    req_data = request.get_json()
    hexcode = req_data['hexcode']
    try:
        beacon = decodehex2.Beacon(hexcode)
        res = db.get_item(Key={'id': 'counter'})
        value = res['Item']['counter_value'] + 1
        res = db.update_item(Key={'id': 'counter'}, UpdateExpression='set counter_value=:value',
                             ExpressionAttributeValues={':value': value}, )
        hextable.put_item(Item = { 'entry_id': str(value), 'hexcode': hexcode,}  )
    except decodehex2.HexError as err:
        return jsonify(error=[err.value,err.message])
    return jsonify(mid=beacon.get_mid(),country=beacon.get_country(),msgtype=beacon.type,tac=beacon.gettac(), beacontype=beacon.btype(),first_or_second_gen=beacon.gentype)



@app.route('/decode/<hexcode>',methods=['GET'])
def decode(hexcode):
    try:
        beacon = decodehex2.Beacon(hexcode)
        res = db.get_item(Key={'id': 'counter'})
        value = res['Item']['counter_value'] + 1
        res = db.update_item(Key={'id': 'counter'}, UpdateExpression='set counter_value=:value',
                             ExpressionAttributeValues={':value': value}, )
        mid=beacon.get_mid()
        country=beacon.get_country()
        ipaddress = str(request.environ.get('HTTP_X_FORWARDED_FOR', request.remote_addr))
        hextable.put_item(Item={'entry_id': str(value), 'hexcode': hexcode, 'mid': mid,'country':country, 'ipaddress':ipaddress, })
    except decodehex2.HexError as err:
        return jsonify(error=[err.value,err.message])


    return jsonify(mid=mid,country=country,msgtype=beacon.type,tac=beacon.gettac(), beacontype=beacon.btype(), first_or_second_gen=beacon.gentype, errors=beacon.errors)

@app.route('/',methods=['GET'])
def api():
    msg='hello world 4'
    return jsonify(msg=msg)





if __name__ == '__main__':
    app.secret_key = 'my secret'
    app.run(debug=False)

from flask import Flask,jsonify,request
import decodehex2
import re
import os
from dotenv import load_dotenv
load_dotenv('.env')

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'Optional default value')


COUNTRIES=[]
country=open('countries2.csv')
for line in country.readlines():
    COUNTRIES.append(line)
COUNTRIES.sort()

@app.route('/validatehex', methods=['GET'])
def validatehex():
    ret_data =  str(request.args.get('hexcode')).strip()
    vlengths=request.args.getlist('lenval[]')
    hexaPattern = re.findall(r'([A-F0-9])', ret_data,re.M|re.I)
    statuscheck='length'
    message = 'Enter a valid beacon hex message'
    new_data=ret_data.upper()
    if len(ret_data) > 0:
        if len(hexaPattern)==len(ret_data):
            message='Valid hexadecimal message.'
            if str(len(ret_data)) in vlengths:
                statuscheck = 'valid'
            else:
                message = 'Bad length '+str(len(ret_data)) + ' Valid lengths: {}'.format(','.join(vlengths))
        else:
            statuscheck='not valid'
            new_data=re.sub(r'[^.a-fA-F0-9]', "", ret_data)
            message='Invalid hexadecimal character (A-F-0-9)'
            new_data=new_data.upper()
    return jsonify(echostatus=statuscheck, message=message,newdata=new_data)

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

from flask import Flask,jsonify,request
import decodehex2
import boto3
import os
import timeit
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

def decoded_beacon(hexcode,fieldlst=[]):
    try:
        beacon = decodehex2.Beacon(hexcode)
        res = db.get_item(Key={'id': 'counter'})
        value = res['Item']['counter_value'] + 1
        res = db.update_item(Key={'id': 'counter'}, UpdateExpression='set counter_value=:value',
                             ExpressionAttributeValues={':value': value}, )
        hextable.put_item(Item={'entry_id': str(value), 'hexcode': hexcode, })
    except decodehex2.HexError as err:
        return {'error':[err.value, err.message]}
    if beacon.errors:
        has_errors=True
    else:
        has_errors=False

    decodedic={    'country':beacon.get_country()
                }


    dispatch = {'hexcode':hexcode,
                'has_errors':has_errors,
                'msgtype':beacon.type,
                'tac':beacon.gettac(),
                'beacontype':beacon.btype(),
                'first_or_second_gen':beacon.gentype,
                'errors' : beacon.errors,
                'mid':beacon.get_mid(),
                'msg_note':beacon.genmsg,
                'loc_prot_fixed_bits':beacon.fbits(),
                'protocol_type':beacon.loctype(),
                'uin':beacon.hexuin()
            }
    for fld in fieldlst:
        if dispatch.__contains__(fld):
            decodedic[fld]=dispatch[fld]
        else:
            decodedic[fld] = '{} not a valid field'.format(fld)

    return decodedic

def dispatch_list(fieldlst):
    decodedic = {'country': beacon.get_country()
                 }
    dispatch = {'hexcode': hexcode,
                'has_errors': has_errors,
                'msgtype': beacon.type,
                'tac': beacon.gettac(),
                'beacontype': beacon.btype(),
                'first_or_second_gen': beacon.gentype,
                'errors': beacon.errors,
                'mid': beacon.get_mid(),
                'msg_note': beacon.genmsg,
                'loc_prot_fixed_bits': beacon.fbits(),
                'protocol_type': beacon.loctype(),
                'uin': beacon.hexuin()
                }
    for fld in fieldlst:
        if dispatch.__contains__(fld):
            decodedic[fld]=dispatch[fld]
        else:
            decodedic[fld] = '{} not a valid field'.format(fld)
    return decodedic


@app.route('/json', methods=['PUT'])
def jsonhex():
    start = timeit.timeit()
    decodedic = {}
    fieldlst= []
    req_data = request.get_json()
    if type(req_data)== list:
        hexcode = req_data
    elif type(req_data) == dict:
        try:
            hexcode = req_data['hexcode']
        except KeyError:
            return jsonify(error=['bad json header request', 'hexcode key not found'])
        try:
            fieldlst= req_data['decode_flds']
            if type(fieldlst)==str:
                fieldlst =[req_data['decode_flds']]

        except KeyError:
            pass

    else:
        return jsonify(error=['bad json header request','hexcode key not found'])

    if type(hexcode)==str:
        decodedic[hexcode]=decoded_beacon(hexcode,fieldlst)

    elif type(hexcode)==list:
        i=0
        for h in hexcode:
            #print(h)
            i+=1
            try:
                decodedic[h['hexcode']] = decoded_beacon(h['hexcode'],fieldlst)
                #print(i)
            except TypeError:
                decodedic[str(h)] = decoded_beacon(str(h),fieldlst)
            except KeyError:
                decodedic[str(i)] = {'error':['bad json header request', 'hexcode key not found at item {}'.format(i)]}
    end = timeit.timeit()
    print(start,end,end - start)

    return jsonify(decodedic)





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

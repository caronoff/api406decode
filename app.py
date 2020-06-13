from flask import Flask,flash,jsonify,request,render_template,redirect,url_for
import decodehex2
import re
import os
from decodefunctions import is_number
from dotenv import load_dotenv
load_dotenv('.env')

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'Optional default value')
gmap_key = os.getenv('GMAP_KEY', 'Optional default value')
print(gmap_key)
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


@app.route("/decoded/<hexcode>",methods=['GET','POST'])
def decoded(hexcode):
    geocoord = (0, 0)
    locationcheck = False
    try:
        beacon = decodehex2.Beacon(hexcode)
        error=''
        if len(beacon.errors)>0 :
            error = ', '.join(beacon.errors)


        if beacon.has_loc() and is_number(beacon.location[0]) and is_number(beacon.location[1]):
            geocoord = (float(beacon.location[0]),float(beacon.location[1]))
            locationcheck=True

        return render_template('output.html', hexcode=hexcode.upper(),
                               decoded=beacon.tablebin,
                               locationcheck=locationcheck,
                               geocoord=geocoord,
                               genmsg=beacon.genmsg,
                               uin = beacon.hexuin(),
                               gmap_key=gmap_key)
    except decodehex2.HexError as err:
        print(err.value,err.message)
        return render_template('badhex.html',errortype=err.value,errormsg=err.message)

@app.route("/",methods=['GET','POST'])
def decode():
    if request.method == 'POST':
        hexcode = str(request.form['hexcode']).strip()
        return redirect(url_for('decoded',hexcode=hexcode))
    return render_template('decodehex.html', title='Home')



if __name__ == '__main__':
    app.secret_key = 'my secret'
    app.run(debug=True)

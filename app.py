from flask import Flask,flash,request,render_template,redirect,url_for
import decodehex2
from decodefunctions import is_number
from dotenv import load_dotenv
load_dotenv('.env')

app = Flask(__name__)

@app.route("/decoded/<hexcode>")
def decoded(hexcode):

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
    app.run()

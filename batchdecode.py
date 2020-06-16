import requests
import time
from requests.exceptions import HTTPError
import decodehex2



def decode(hexcode):
    result={}
    try:
        beacon = decodehex2.Beacon(hexcode)
        result={'mid': beacon.get_mid(),
                'country': beacon.get_country(),
                'msgtype': beacon.type,
                 'tac':beacon.gettac(),
                'beacontype': beacon.btype() ,
                'protocol': beacon.protocoltype()}

    except decodehex2.HexError as err:
        result = {'error': [err.value,err.message]}
    return result

def decodehex(apiurl,hex):
    try:
        api='{}/{}'.format(apiurl,str(hex))
        response = requests.get(api)
        response.raise_for_status()
        # access JSOn content
        jsonResponse = response.json()
        return jsonResponse

    except HTTPError as http_err:
        error=f'HTTP error occurred: {http_err}'
    except Exception as err:
        error=f'Other error occurred: {err}'
    return error

def decodefile(inputfilename,outputfilename,apilink,a):

    output = open(outputfilename, 'w')
    with open(inputfilename, 'r') as fp:
        #lines = fp.readlines()
        cnt=0
        tic = time.perf_counter()

        while True and cnt < a:
            line = fp.readline()
            if not line:
                break

            hex = line.strip()
            if apilink=='':
                result=decode(hex)
            else:
                result = (decodehex(apilink, hex))
            lstdecode = [hex]
            if 'error' in result:
                for e in result['error']:
                    lstdecode.append(e)

            else:
                for fld in ('beacontype', 'mid', 'country', 'tac', 'protocol'):
                    lstdecode.append(str(result[fld]))

            decodeline = ','.join(lstdecode) + '\n'

            output.write(decodeline)
            cnt+=1

    toc = time.perf_counter()
    output.close()
    print(f"execution in {toc - tic:0.4f} seconds")



if __name__ == '__main__':
    apiurl='https://406decode.org/api'
    localurl='http://127.0.0.1:5000/api'
    ibrdfile='ibrd-16June2020.txt'
    ticketfile='hexticket.txt'
    decodefile(ibrdfile,'hexfromibrd.csv','',5000)


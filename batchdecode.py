import requests
import time
from requests.exceptions import HTTPError
import decodehex2
import os
from chardet import detect

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
    readfile(inputfilename)
    output = open(outputfilename, 'w',encoding='utf-8')
    with open(inputfilename, encoding='utf-8') as fp:
        #lines = fp.readlines()
        cnt=0
        tic = time.perf_counter()

        while True and cnt < a:

            try:
                line = fp.readline()
                line = line.strip().strip('"')
                if len(line)>0:
                    hex=[]
                    if ',' in line:
                        hex= line.split(',')
                    else:
                        hex.append(line)
                    for hexcode in hex:
                        hexcode=hexcode.strip().strip('"')
                        if apilink=='':
                            result=decode(hexcode)
                        else:
                            result = (decodehex(apilink, hexcode))
                        lstdecode = [hexcode]

                        if 'error' in result:
                            for e in result['error']:
                                lstdecode.append(e)
                        else:
                            for fld in ('beacontype', 'mid', 'country', 'tac', 'protocol'):
                                lstdecode.append(str(result[fld]))

                        decodeline = ','.join(lstdecode) + '\n'
                        output.write(decodeline)
            except UnicodeDecodeError:
                output.write(hex+' Unicode Character decode error\n')
                pass


            cnt+=1

    toc = time.perf_counter()
    output.close()
    print(f"execution in {toc - tic:0.4f} seconds")


def readfile(srcfile):
    trgfile='newfile.txt'
    from_codec = get_encoding_type(srcfile)
    print(from_codec)

    # add try: except block for reliability
    try:
        with open(srcfile, 'r', encoding=from_codec) as f, open(trgfile, 'w', encoding='utf-8') as e:
            text = f.read()  # for small files, for big use chunks
            e.write(text)


        os.remove(srcfile)  # remove old encoding file
        os.rename(trgfile, srcfile)  # rename new encoding
    except UnicodeDecodeError:
        print('Decode Error')

    except UnicodeEncodeError:
        print('Encode Error')


# get file encoding type
def get_encoding_type(file):
    with open(file, 'rb') as f:
        rawdata = f.read()
    return detect(rawdata)['encoding']


if __name__ == '__main__':

    ibrdfile='ibrd-16June2020.txt'
    ticketfile='Hexcleaned.txt'

    methods=['https://406decode.org/api','http://127.0.0.1:5000/api','']

    decodefile('hexcleaned.txt','hexfromticket.csv',methods[0],100)


    #readfile(ticketfile)



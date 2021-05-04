import bch1correct as bch1
import bch2correct as bch2
import decodefunctions as Fcn


def bch_check(inputhex):
    errors = [inputhex]
    preamble =''
    if len(inputhex)==36:
        strhex = inputhex[6:]
        preamble = inputhex[:6]
    elif len(inputhex)==30:
        strhex = inputhex
        preamble =''
    else:
        return False
    ## Error correction attempt for when BCH portion does not match recomputed
    try:
        _pdf1 = (Fcn.hextobin(strhex))[:61]
        _bch1 = (Fcn.hextobin(strhex))[61:82]
        bitflips1, newpdf1, newbch1 = bch1.pdf1_to_bch1(_pdf1, _bch1)
        _pdf2 = (Fcn.hextobin(strhex))[82:108]
        _bch2 = (Fcn.hextobin(strhex))[108:]
        bitflips2, newpdf2, newbch2 = bch2.pdf2_to_bch2(_pdf2, _bch2)
        if bitflips1 == -1 or bitflips2 == -1:
            errors.append('Too many bit errors to correct')
        elif bitflips1 > 0 or bitflips2 > 0:
            _newbin = newpdf1 + newbch1 + newpdf2 + newbch2
            fixhex= preamble+ Fcn.bin2hex(_newbin)
            errors.append(fixhex)
            errors.append(' {} bad pdf1 bit and {} bad pdf2 bit'.format(bitflips1, bitflips2))
            errors.append('Corrected Message: {} '.format(fixhex))
    except:
        return False


    return errors


if __name__ == "__main__":
    strhex = input("30 character Hex message: ")
    #raise HexError('FormatError', 'Not a valid hex message')
    errors=[]
    errors = bch_check(strhex)

    if errors:
        print(errors)
    

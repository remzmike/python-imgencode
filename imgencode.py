from __future__ import division
from PIL import Image
import random

def bitstring_to_byte(bitstring):
    assert len(bitstring) == 8
    return int(bitstring, 2)

def bitstring_to_string(bitstring):
    assert len(bitstring) % 8 == 0
    s = ''
    for i in range(len(bitstring) // 8):
        block = bitstring[i*8:i*8+8]
        c = chr(bitstring_to_byte(block))
        s += c
    return s

def get_bits(s):
    result = []
    for c in s:
        for i in reversed(range(8)):
            bit = (ord(c) >> i) & 1
            result.append(bit)
    return result

def test():
    result = ''
    for bit in get_bits('a'):
        result += str(bit)
    assert int(result, 2) == 97

def can_fit_message(img, msg):
    # 3 bits per pixel
    pxcount = img.size[0] * img.size[1]
    bitcount = len(msg) * 8
    return pxcount > bitcount / 3

def encode_into_image(img, msg):
    
    img = img.convert("RGBA")
    
    if not can_fit_message(img, msg):
        raise Exception("message too large to be encoded in this image")

    data = img.getdata()
    
    newdata = list()
    bits = get_bits(msg)
    bitcount = 0
    
    for px in data:
        for idx, val in enumerate(px):
            if idx == 3: continue # skip alpha
            if bitcount < len(bits):
                bit = bits[bitcount]
                bitcount += 1
            else:
                bit = None

            if bit == 1:
                newval = val + random.choice([-1,1])
                if newval > 255:
                    newval = 254
                elif newval < 0:
                    newval = 1
                px = list(px)
                px[idx] = newval
                px = tuple(px)

        newdata.append(px)

    img.putdata(newdata)
    return img
    
def decode_from_image(orig, new):
    orig = orig.convert("RGBA")
    origdata = orig.getdata()
    
    new = new.convert("RGBA")
    newdata = new.getdata()
    
    assert len(origdata) == len(newdata)
    
    diff = ''
    null_encountered = False
    for i,px in enumerate(origdata):
        newpx = newdata[i]        
        for j in range(4):
            if j == 3: continue # skip alpha
            if px[j] == newpx[j]:
                diff += '0'
            else:
                delta = px[j] - newpx[j]
                delta = abs(delta)
                assert delta < 2
                diff += '1'
            # break on null byte
            if len(diff) % 8 == 0:
                if diff[-8:] == '0'*8:
                    null_encountered = True
                    break                
        if null_encountered:
            diff = diff[:-8]
            break
    result = bitstring_to_string(diff)
    return result    

if __name__ == '__main__':
    test()

    # encode
    
    source = Image.open('input.png')
        
    msg = 'hello'*6125 # 6125 is max, 6126 is too many
    #msg = 'hl'*2 # l ends in 2 0s, h ends in 3 0s
    result = encode_into_image(source, msg)
    result.save("output.png", "PNG")
        
    # decode

    input = Image.open('input.png')
    output = Image.open('output.png')
    decoded = decode_from_image(input, output)    
    print decoded
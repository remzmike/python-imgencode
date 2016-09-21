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
    bits.extend([0]*8) # delimit with null byte
    bitcount = 0
    
    for px in data:
        for idx, val in enumerate(px):
            if idx == 3: continue # skip alpha
            if bitcount < len(bits):
                bit = bits[bitcount]
                bitcount += 1
            else:
                bit = None

            if bit != None:
                rand = random.choice([-1,1])
                newval = val
                if bit == 1 and val % 2 == 0 \
                or bit == 0 and val % 2 == 1:
                    newval += rand

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
 
def decode_from_image(img):
    img = img.convert("RGBA")
    imgdata = img.getdata()
    
    diff = ''
    null_encountered = False
    for i,px in enumerate(imgdata):    
        for j in range(4):
            if j == 3: continue # skip alpha
            bit = str(px[j] % 2)
            diff += bit
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
    result.save("output2.png", "PNG")
        
    # decode

    output = Image.open('output2.png')
    decoded = decode_from_image(output)    
    print decoded
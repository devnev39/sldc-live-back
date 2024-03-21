# Copyright (c) 2024 github.com/devnev39

# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:

# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
# LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
# OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
# WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

# This script will download the latest image from sldc report site
# and convert that image to computer readable format of json data.
# The json data is in the from of tables and fields.

import resource
from urllib.request import urlopen
import cv2
import numpy as np
import json
import os
import textwrap

os.environ['KMP_DUPLICATE_LIB_OK'] = "TRUE"

SAVE_INNER_STATE = False

import easyocr

reader = easyocr.Reader(['en'], model_storage_directory="./model")

sharp_kernel = np.array([[0, -1, 0],
[-1, 5, -1],
[0, -1, 0]])

req = urlopen('https://mahasldc.in/wp-content/reports/sldc/report2.jpg')
arr = np.asarray(bytearray(req.read()), dtype=np.uint8)
img = cv2.imdecode(arr, -1)

# cv2.imwrite('download.png', img)

def show(image):
    cv2.imshow('image', image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

def getValue(image, box: list):
    x,y,w,h = box
    crop_img = image[y:y+h, x:x+w]
    n_h = 150
    n_w = 200

    # resize -> grey -> threshold -> denoise -> result
    if SAVE_INNER_STATE:
        cv2.imwrite(f'test/{x}_{y}_before.png', crop_img)

    # Sharpening default image

    # cv2.imwrite(f'test/{x}_{y}_after_sharp.png', crop_img)
    
    # Resizing the sharpened image
    crop_img = cv2.resize(crop_img, (n_w, n_h), interpolation=cv2.INTER_AREA)
    # cv2.imwrite(f'test/{x}_{y}_after_resize.png', crop_img)

    result = reader.readtext(crop_img, allowlist="0123456789.-") 

    # Convert to gray
    crop_img = cv2.cvtColor(crop_img, cv2.COLOR_BGR2GRAY)
    # cv2.imwrite(f'test/{x}_{y}_after_grey.png', crop_img)
    
    # crop_img = cv2.bilateralFiltering(crop_img, 9, 75, 75)
    # crop_img = cv2.fastNlMeansDenoising(crop_img, None, 10, 7, 21)

    res = reader.readtext(crop_img, allowlist="0123456789.-")

    # Check if the new result has high confidence

    if len(result) and len(res):
        result = result if result[0][2] > res[0][2] else res
    elif len(res):
        result = res

    # Apply Threshold
    ret, crop_img = cv2.threshold(crop_img, 60, 255, cv2.THRESH_BINARY_INV)    
    # crop_img = cv2.filter2D(crop_img, -1, sharp_kernel)
    
    if SAVE_INNER_STATE:
        cv2.imwrite(f'test/{x}_{y}_after_thresh.png', crop_img)

    res = reader.readtext(crop_img, allowlist="0123456789.-")

    if len(result) and len(res):
        result = result if result[0][2] > res[0][2] else res
    elif len(res):
        result = res

    if len(result):
        return result[0][1] if len(result) else ''
    return ''

def getState() -> dict:
    # print(f"Memory used before running the script: {resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024**2} MiB")
    # prev = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024**2
    with open('schema.json', 'r') as file:
        st = json.loads(file.read())

    stats = st['stats']
    fields = st['fields']
    tables = st['tables']

    for f in fields:
        value = getValue(img, fields[f])
        fields[f] = value

    fields['date'] = fields['date'].replace('.','')
    fields['date'] = '/'.join(textwrap.wrap(fields['date'],2))

    fields['time'] = fields['time'].replace('.','').replace(':', '')
    fields['time'] = ':'.join(textwrap.wrap(fields['time'],2))

    for s in stats:
        value = getValue(img, s['value'])
        value = value.replace('\n','')
        s['value'] = value

    for tbl in tables:
        rows = tbl['rows']
        for r in rows:
            for idx,r_c in enumerate(r[1:]):
                val = getValue(img, r_c)
                val = val.replace('\n','')
                if(val == ''):
                    val = 'NAN'
                r[idx+1] = val

    for tbl in tables:
        for idx,row in enumerate(tbl['rows']):
            obj = {}
            for item in row:
                obj[tbl['columns'][row.index(item)]] = item
            tbl['rows'][idx] = obj
    t = resource.getrusage(resource.RUSAGE_SELF).ru_utime + resource.getrusage(resource.RUSAGE_SELF).ru_stime
    print(f"CPU time used during script execution: {t} seconds")
    stats = {
        "time": t,
        "memory": 0
    }
    return (st, stats)
    
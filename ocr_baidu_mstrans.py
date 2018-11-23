# -*- coding: utf-8 -*-

from PIL import Image,ImageDraw,ImageFont
import httplib, urllib, base64, json
import cv2
import re
import sys
import md5
import random
import requests
import numpy as np
from mstranslator import Translator

reload(sys)
sys.setdefaultencoding('utf8')


def print_word(json_data): # fron ms ocr result, get detected words
    g = open('result/word.txt', 'w')
    result = json.loads(json_data)
    for l in result['regions']:
        for w in l['lines']:
            line = []
            for r in w['words']:
                line.append(r['text'])
            # print ' '.join(line) ###########detected korean
            g.write(''.join(line))
            g.write('\n')
    g.close()
    return


def print_box(json_data): # fron ms ocr result, get words' positions
    f = open('result/box.txt', 'w')
    result = json.loads(json_data)
    line = []
    for l in result['regions']:
        for w in l['lines']:
            line.append(w['boundingBox'])

    # print '\n'.join(line) ###########detected text box position
    f.write(str('\n'.join(line)))

    f.close()
    return


def join_all(): # join boxes and words which in the same bubble
    f = open('result/word.txt', 'r')
    g = open('result/box.txt', 'r')
    fjb = open('result/join_box.txt', 'w')
    fjw = open('result/join_word.txt', 'w')

    word = f.readline()
    pos = g.readline()

    pos = re.split(",|\n", pos)
    x = int(pos[0])
    y = int(pos[1])
    w = int(pos[2])
    d = int(pos[3])
    # print pos,x,y,w,d

    while 1:
        word2 = f.readline()
        pos2 = g.readline()
        if not word2:
            fjw.write(word)
            fjb.write(str(x))
            fjb.write(',')
            fjb.write(str(y))
            fjb.write(',')
            fjb.write(str(w))
            fjb.write(',')
            fjb.write(str(d))
            fjb.write('\n')
            # print str(x), y, w, d
            break

        pos2 = re.split(",|\n", pos2)
        x2 = int(pos2[0])
        y2 = int(pos2[1])
        w2 = int(pos2[2])
        d2 = int(pos2[3])

        if (y+d+d2/2)>y2 and x+w >x2: # if in the same bubble, join it
            print('yes')
            word = word.strip('\n')
            j_w = word+word2
            j_b = np.zeros(4)
            j_b[0] = x if x<x2 else x2
            j_b[1] = y
            j_b[2] = w if w>w2 else w2
            j_b[3] = y2+d2-y

            word=j_w
            x=int(j_b[0])
            y=int(j_b[1])
            w=int(j_b[2])
            d=int(j_b[3])

        else:
            print('no')
            fjw.write(word)
            fjb.write(str(x))
            fjb.write(',')
            fjb.write(str(y))
            fjb.write(',')
            fjb.write(str(w))
            fjb.write(',')
            fjb.write(str(d))
            fjb.write('\n')
            # print str(x), y, w, d

            word = word2
            x = x2
            y = y2
            w = w2
            d = d2


def baidu_trans(word,fromLang='en',toLang='zh'): # get baidu translate api translation result
    trans_data=''
    appid = '20171023000090333'
    secretKey = 'fdLhj0EY0uo2wPIBRWlC'
    httpClient = None
    myurl = '/api/trans/vip/translate'
    q = word
    salt = random.randint(32768, 65536)
    sign = appid+q+str(salt)+secretKey
    m1 = md5.new()
    m1.update(sign)
    sign = m1.hexdigest()
    myurl = myurl+'?appid='+appid+'&q='+urllib.quote(q)+'&from='+fromLang+'&to='+toLang+'&salt='+str(salt)+'&sign='+sign

    try:
        httpClient = httplib.HTTPConnection('api.fanyi.baidu.com')
        httpClient.request('GET', myurl)
        #response是HTTPResponse对象
        response = httpClient.getresponse()
        r=response.read()
        # print result
        result=json.loads(r)
        for w in result['trans_result']:
            data=w['dst']
            # print w['dst']

    except Exception, e:
        print e
    finally:
        if httpClient:
            httpClient.close()
    return w['dst']


def ms_trans(word,fromLang='en',toLang='zh'): # get MS translate api translation result
    translator = Translator('e778944ec635414d9bd196aa544db6bd')
    result=translator.translate(word, lang_from=fromLang, lang_to=toLang)
    return result


if __name__ == '__main__':
    headers = {
        # Request headers
        'Content-Type': 'application/octet-stream',
        'Ocp-Apim-Subscription-Key': '1791b966e9b3488f9e54d05e58e0f705',
    }
    params = urllib.urlencode({
        # Request parameters
        'language': 'unk',   #korean 'ko'
        'detectOrientation ': 'ture',
    })
    # name = str(sys.argv[1])
    url = 'https://eastasia.api.cognitive.microsoft.com/vision/v1.0/ocr'
    name='2.png' #'c5.png'
    data = open('images/'+name, 'rb').read()

    try:
        response = requests.post(
            url,
            headers=headers,
            params=params,
            data=data
        )

        print (response.text)  # get ms ocr result

        print_word(response.text) # save the word in word.txt
        print_box(response.text) # save the position in box.txt
        join_all() # save the joined word and position in join_word.txt and join_box.txt

        image_file ='images/'+name

        original = cv2.imread(image_file,cv2.IMREAD_COLOR)
        original2=cv2.imread(image_file,cv2.IMREAD_COLOR)
        # cv2.imshow('original ', original)

        f = open('result/box.txt')
        txt = f.read()
        t = re.split(",|\n", txt)
        # print t
        for i in range(0, len(t), 4): # draw detected position and remove word
            # print t[i], t[i + 1], t[i + 2], t[i + 3]
            cv2.rectangle(original, (int(t[i])-3,int(t[i + 1])-3), (int(t[i])+int(t[i + 2])+3,int(t[i + 1])+int(t[i + 3])+3), (255,255,255),-1,1,0)
            cv2.rectangle(original2, (int(t[i])-3,int(t[i + 1])-3), (int(t[i])+int(t[i + 2])+3,int(t[i + 1])+int(t[i + 3])+3), (255,0,255),1,1,0)

        cv2.imshow('detect',original2)
        cv2.imwrite('result/detect_' + name, original2)  # save word removed image
        cv2.imshow('remove', original)
        cv2.imwrite('result/remove_'+name,original) # save word removed image
        cv2.waitKey(0)
        cv2.destroyAllWindows()
        cv2.waitKey(0)

        f1 = open('result/join_word.txt','r')
        f2 = open('result/join_box.txt','r')
        fb = open('result/trans_b.txt', 'w')
        fm = open('result/trans_m.txt', 'w')

        while 1:
            word =f1.readline()
            pos=f2.readline()

            if not word:
                break

            pos=re.split(",|\n", pos)
            x=int(pos[0])
            y=int(pos[1])
            # print pos,x,y

            # print("word:"+word)
            data_b=baidu_trans(word,'zh','kor') # get baidu translate api translation result
            data_m=ms_trans(word,'zh','ko') # get MS translate api translation result

            print("text:" + word)

            print ("baidu_trans:"+ data_b)
            fb.write(data_b) # save the translation result
            fb.write('\n')

            data_m = re.sub('\n', '', str(data_m))
            print ("ms_trans:" + data_m)
            fm.write(data_m)  # save the translation result
            fm.write('\n')
        print('done')

    except Exception as e:
        print(e)
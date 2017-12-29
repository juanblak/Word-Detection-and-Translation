# -*- coding: utf-8 -*-

# OCR - Project Oxford by MS

from PIL import Image,ImageDraw,ImageFont
import httplib, urllib, base64, json
import cv2
import re
import sys
import md5
import random


reload(sys)
sys.setdefaultencoding('utf8')

def print_text(json_data):
    g = open('word.txt', 'w')
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

def print_box(json_data):
    f = open('box.txt', 'w')
    result = json.loads(json_data)
    line = []
    for l in result['regions']:
        for w in l['lines']:
            line.append(w['boundingBox'])

    # print '\n'.join(line) ###########detected text box position
    f.write(str('\n'.join(line)))

    f.close()
    return


def ocr_project_oxford(headers, params, data):
    conn = httplib.HTTPSConnection('westcentralus.api.cognitive.microsoft.com')
    conn.request("POST", "/vision/v1.0/ocr?%s" % params, data, headers=headers)
    response = conn.getresponse()
    data = response.read()
    # print data + "\n"
    #
    # parsed = json.loads(data)
    # print (json.dumps(parsed, sort_keys=True, indent=2))

    print_text(data) # print recognized words
    print_box(data) # print text box
    conn.close()
    return

def trans(word,fromLang='en',toLang='zh'):
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



if __name__ == '__main__':
    headers = {
        # Request headers
        'Content-Type': 'application/octet-stream',
        'Ocp-Apim-Subscription-Key': '8abe147864ef4bebba4969a03264303f',
    }
    params = urllib.urlencode({
        # Request parameters
        'language': 'unk',   #korean
        'detectOrientation ': 'ture',
    })
    # name = str(sys.argv[1])
    name='c5.png'
    data = open('images/'+name, 'rb').read()

    try:
        image_file ='images/'+name
        # im = Image.open(image_file)
        #im.show()
        ocr_project_oxford(headers, params, data)

        original = cv2.imread(image_file,cv2.IMREAD_COLOR)
        original2=cv2.imread(image_file,cv2.IMREAD_COLOR)
        # cv2.imshow('original ', original)

        f = open('box.txt')
        txt = f.read()
        t = re.split(",|\n", txt)
        #print t

        for i in range(0, len(t), 4):
            # print t[i], t[i + 1], t[i + 2], t[i + 3]
            cv2.rectangle(original, (int(t[i]),int(t[i + 1])), (int(t[i])+int(t[i + 2]),int(t[i + 1])+int(t[i + 3])), (255,255,255),-1,1,0)
            cv2.rectangle(original2, (int(t[i]),int(t[i + 1])), (int(t[i])+int(t[i + 2]),int(t[i + 1])+int(t[i + 3])), (255,0,255),1,1,0)

        cv2.imshow('detect',original2)
        cv2.imshow('remove', original)
        cv2.imwrite('result_'+name,original)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
        cv2.waitKey(0)

        f1 = open('word.txt')
        f2 = open('box.txt')
        # imgtrans = cv2.imread('result_' + name, cv2.CV_LOAD_IMAGE_COLOR)
        imageFile='result_' + name
        imgtrans=Image.open(imageFile)
        while 1:
            word =f1.readline()
            pos=f2.readline()

            if not word:
                break

            pos=re.split(",|\n", pos)
            x=int(pos[0])
            y=int(pos[1])
            print pos,x,y

            print("word:"+word)
            data=trans(word,'zh','kor')
            print ("data:"+ data)

            # #putText only write ASCII
            # font = cv2.FONT_HERSHEY_TRIPLEX
            # cv2.putText(imgtrans, data, (x,y), font, 0.8 ,(0,0,0),1)

            fontk = ImageFont.truetype("ARIALUNI.ttf", 30) #korean font
            # fontc = ImageFont.truetype('simsun.ttc', 24) #Chinese font
            draw = ImageDraw.Draw(imgtrans)
            draw.text((x, y), data, (0, 0, 0), font=fontk)

        imgtrans.save('translate_'+name)

        # cv2.imshow('translate', imgtrans)
        # cv2.imwrite('translate' + name, imgtrans)
        # cv2.waitKey(0)

    except Exception as e:
        print(e)
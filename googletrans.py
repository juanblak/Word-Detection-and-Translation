#-*- coding:utf-8 -*-

from googletrans import Translator
translator = Translator()
result=translator.translate('안녕하세요.',dest='zh-cn').text
print(result)

fjw = open('result/join_word.txt', 'r',encoding='UTF8') #except English use encoding='UTF8'
fg = open('result/trans_go.txt', 'w',encoding='UTF8') ##except English use encoding='UTF8'

while 1:
    word = fjw.readline()

    if not word:
        break

    #dest='zh-cn' 'en' 'ko' 'ja'
    result = translator.translate(word, dest='ko').text
    fg.write(result)
    fg.write('\n')

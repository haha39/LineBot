import random
import pymysql

import jsonify

#ReconCoin
import cv2
import numpy as np

from django.shortcuts import render

# Create your views here.

import string

from django.shortcuts import render
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings

from linebot import LineBotApi, WebhookParser
from linebot.exceptions import InvalidSignatureError, LineBotApiError
from linebot.models import MessageEvent, TextSendMessage

line_bot_api = LineBotApi(settings.LINE_CHANNEL_ACCESS_TOKEN)
parser = WebhookParser(settings.LINE_CHANNEL_SECRET)


@csrf_exempt
def callback(request):
    if request.method == 'POST':
        signature = request.META['HTTP_X_LINE_SIGNATURE']
        body = request.body.decode('utf-8')

        try:
            events = parser.parse(body, signature)  # 傳入的事件
        except InvalidSignatureError:
            return HttpResponseForbidden()
        except LineBotApiError:
            return HttpResponseBadRequest()
        for event in events:
            if event.message.type == 'text':  # 如果有訊息事件
                print("receive text\n")
                if(event.message.text == "?"):
                    money = searchdb()
                    line_bot_api.reply_message(  # 回復傳入的訊息文字
                        event.reply_token,
                        TextSendMessage(text=money)
                    )
                else:
                    line_bot_api.reply_message(  # 回復傳入的訊息文字
                        event.reply_token,
                        TextSendMessage(text=event.message.text)
                    )
            elif event.message.type == 'image':
                image_name = ''.join(random.choice(string.ascii_letters + string.digits) for x in range(4))
                image_content = line_bot_api.get_message_content(event.message.id)
                image_name = image_name.upper() + '.png'
                path = './static/' + image_name
                with open(path, 'wb') as fd:
                    for chunk in image_content.iter_content():
                        fd.write(chunk)
                print("jojo")
                total = ReconCoin(path)
                print("yaya\n")
                print(total)
                line_bot_api.reply_message(  # 回復傳入的訊息文字
                    event.reply_token,
                    TextSendMessage(text=total)
                )
        return HttpResponse()
    else:
        return HttpResponseBadRequest()

def ReconCoin(path):
    img = cv2.imread(path)
    # img_old = cv2.imread(path)
    # # 裁切區域的 x 與 y 座標（左上角）
    # x = 500
    # y = 0
    #
    # # 裁切區域的長度與寬度
    # w = 1000
    # h = 700
    # img = img_old[y:y+h, x:x+w]
    #
    h, w, ch = img.shape

    img = cv2.resize(img, (w//5, h//5),
                     interpolation=cv2.INTER_NEAREST)  # important

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)  # 灰階化
    ret, gray = cv2.threshold(gray, 110, 255, cv2.THRESH_BINARY)  # 二值化

    # 侵蝕，裡面矩陣與 iterations 細調
    gray = cv2.erode(gray, np.ones((2, 2)), iterations=2)
    # 膨脹，裡面矩陣與 iterations 細調
    gray = cv2.dilate(gray, np.ones((2, 2)), iterations=1)

    num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(
      gray, connectivity=8)
    #print(stats)  # 檢查所有區塊
    print("num_labels: ", num_labels)
    print("labels: ", labels)
    print("state (x座標、y座標、長、寬、面積): ")
    #for it in stats:
     #   print(it)
    #print("centroids: ", centroids)

    ans = 0

    for it in stats:
      itX = it[0]+it[2]  # 寬度
      itY = it[1]+it[3]  # 高度
      if(it[2]>70):
        print(it)

      if((it[2] < (it[3]+5) and (it[3]-5) < it[2]) and (it[2]>70)):  # is a circle
        cv2.rectangle(img, (it[0], it[1]), (itX, itY), (0, 0, 255), 2)  # BGR
        print("it size: ", it[2])
        if(it[2] > 155 and it[2] < 165):
            ans += 50
        if(it[2] >= 135 and it[2] <= 155):
            ans += 10
        if(it[2] >= 125 and it[2] < 135):
            ans += 5
        if (it[2] >= 110 and it[2] < 125):
            ans += 1

    # cv2.imshow("gray", gray)
    print(ans, "元")
    # cv2.imshow("img", img)
    cv2.imwrite('ans.jpg', img)
    cv2.imwrite('gray.jpg', gray)
    # cv2.waitKey(0)
    lastmoney = searchdb()
    if(ans == 0):
        insertdb(0, lastmoney)
        print("not money QQ\n")
        print(lastmoney)
    else:
        lastmoney += ans
        insertdb(1, lastmoney)
        print("new money YAYA\n")
        print(lastmoney)
    return ans

def searchdb():
    # 打开数据库连接
    db = pymysql.connect(host='localhost',
                         user='test123',
                         password='test123',
                         database='aiotdb')

    # 使用cursor()方法获取操作游标
    cursor = db.cursor()

    # SQL 查询语句
    sql = "SELECT * FROM sensors "
    try:
        # 执行SQL语句
        cursor.execute(sql)
        # 获取最新的记录列表
        results = cursor.fetchall()
        lastmoney = 0

        for money in results:
            lastmoney = money[2]
        # 打印结果
        print("total=%s," %(lastmoney))
    except:
        print("Error: unable to fetch data")

    # 关闭数据库连接
    db.close()
    return lastmoney

def insertdb(status, total):
    db = pymysql.connect(host='localhost',
                         user='test123',
                         password='test123',
                         database='aiotdb')
    cursor = db.cursor()
    sql = """INSERT INTO sensors(id,
             time, value, temp, humi, status)
             VALUES (0, 0, '%s', 0, 0, '%s')"""
    try:
        cursor.execute(sql%(str(total), str(status)))
        db.commit()
    except:
        db.rollback()
    db.close()










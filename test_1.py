import cv2
import numpy as np


def ReconCoin():
    img_old = cv2.imread("static/newT1.jpg")
    # 裁切區域的 x 與 y 座標（左上角）
    x = 500
    y = 0

    # 裁切區域的長度與寬度
    w = 1000
    h = 700
    img = img_old[y:y+h, x:x+w]

    h, w, ch = img.shape

    img = cv2.resize(img, (w//5, h//5),
                     interpolation=cv2.INTER_NEAREST)  # important

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)  # 灰階化
    ret, gray = cv2.threshold(gray, 100, 255, cv2.THRESH_BINARY)  # 二值化

    # 侵蝕，裡面矩陣與 iterations 細調
    gray = cv2.erode(gray, np.ones((2, 2)), iterations=2)
    # 膨脹，裡面矩陣與 iterations 細調
    gray = cv2.dilate(gray, np.ones((2, 2)), iterations=1)

    num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(
      gray, connectivity=8)
    print(stats)  # 檢查所有區塊
    print("num_labels: ", num_labels)
    print("labels: ", labels)
    print("state (x座標、y座標、長、寬、面積): ")
    for it in stats:
        print(it)
    print("centroids: ", centroids)

    ans = 0

    for it in stats:
      itX = it[0]+it[2]  # 寬度
      itY = it[1]+it[3]  # 高度
      if(it[2] < (it[3]+3) or it[3] < (it[2]+3)):  # 1 dallars
        cv2.rectangle(img, (it[0], it[1]), (itX, itY), (0, 0, 255), 2)  # BGR
        print("it size: ", it[2])
        if(it[2] >= 126 and it[2] < 135):
            ans += 50
        if(it[2] >= 115 and it[2] < 125):
            ans += 10
        if(it[2] >= 100 and it[2] < 105):
            ans += 5

    # cv2.imshow("gray", gray)
    print(ans, "元")
    cv2.imshow("img", img)
    cv2.imwrite('ans.jpg', img)
    cv2.imwrite('gray.jpg', gray)
    cv2.waitKey(0)


ReconCoin()

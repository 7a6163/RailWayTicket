# encoding: utf-8
from PIL import Image, ImageEnhance
import cv2
import matplotlib
matplotlib.use('Qt4Agg')
import matplotlib.pyplot as plt
from matplotlib import gridspec
from matplotlib.font_manager import FontProperties
import collections
import os, random, sys
import numpy as np

reload(sys)
sys.setdefaultencoding("utf-8")

class Image:

    #  傳入圖片所在目錄和檔名
    def __init__(self, Path,ImgName):
        #  設置matplotlib中文字體
        self.font = FontProperties(fname=r"c:\windows\fonts\SimSun.ttc", size=14)
        #  儲存檔名
        self.imageName = ImgName
        #  儲存路徑
        self.Path = Path
        #  用來儲放分割後的圖片邊緣坐標(x,y,w,h)
        self.arr = []
        #  將每個階段做的圖存起來 用來debug
        self.dicImg = collections.OrderedDict()
        #  將圖片做灰階
        self.im = cv2.imread(Path + "\\" + ImgName)
        self.dicImg.update({"原始驗證碼": self.im.copy()})


    #  閾值化
    def threshold(self):
        # 115 是 threshold，越高濾掉越多
        # 255 是當你將 method 設為 THRESH_BINARY_INV 後，高於 threshold 要設定的顏色
        # 反轉黑白 以利輪廓識別
        self.retval, self.im = cv2.threshold(self.im, 70, 255, cv2.THRESH_BINARY_INV)
        # 存檔
        #cv2.imwrite("D:\\CaptchaRaw\\" + self.imageName + 'Threshold.png', self.im)
        self.dicImg.update({"閾值化": self.im.copy()})

    #  去噪
    def removeNoise(self):
        for i in xrange(len(self.im)):
            for j in xrange(len(self.im[i])):
                if self.im[i][j] == 255:
                    count = 0
                    for k in range(-2, 3):
                        for l in range(-2, 3):
                            try:
                                if self.im[i + k][j + l] == 255:
                                    count += 1
                            except IndexError:
                                pass
                    # 這裡 threshold 設 4，當週遭小於 4 個點的話視為雜點
                    if count <= 3:
                        self.im[i][j] = 0

        self.im = cv2.dilate(self.im, (2, 2), iterations=1)
        self.dicImg.update({"去噪": self.im.copy()})

    #  色調分離
    def posterization(self,levels=3):
        n = levels  # Number of levels of quantization

        indices = np.arange(0, 256)  # List of all colors

        divider = np.linspace(0, 255, n + 1)[1]  # we get a divider

        quantiz = np.int0(np.linspace(0, 255, n))  # we get quantization colors

        color_levels = np.clip(np.int0(indices / divider), 0, n - 1)  # color levels 0,1,2..

        palette = quantiz[color_levels]  # Creating the palette

        im2 = palette[self.im]  # Applying palette on image

        self.im = cv2.convertScaleAbs(im2)  # Converting image back to uint8
        #  存檔
        #cv2.imwrite("D:\\CaptchaRaw\\" + self.imageName + '.png', self.im)
        self.dicImg.update({"色調分離": self.im.copy()})

    #  干擾線檢測
    def removeLines(self):
        chop = 4  #  線段長度大於chop 才判斷為干擾線
        lineColor = 255  #  將線段設定為黑或白色 255:白 0:黑
        (height, width,_) = self.im.shape
        #  loop 每一個pixel
        for i in xrange(height):
            for j in xrange(width):
                #  如果是黑色點 開始計算線段長度
                if self.CheckPixelIsBlack(self.im[i][j]):
                    countWidth = 0
                    #  移除橫線 在每個像素找尋橫向的像素 如果<threshold 就count+1
                    for c in range(j, width):
                        if self.CheckPixelIsBlack(self.im[i][c]):
                            countWidth += 1
                        else:
                            break
                    #  如果大於指定長度 代表是線段
                    if countWidth >= chop:
                        for c in range(countWidth):
                            try:
                                #  如果此點的上下兩個點是白的 代表不在數字裡 可以移除
                                if self.CheckPixelIsWhite(self.im[i+1, j+c]) and self.CheckPixelIsWhite(self.im[i-1, j+c]):
                                    self.im[i, j+c] = lineColor
                                # # #  判斷是不是兩條干擾線重疊在一起 搜尋此點的下面的點的右邊 判斷下面的點是不是也是橫向線段
                                # elif self.im[i+1, j+c] < threshold:
                                #     count = 0
                                #     for x in range(j, width):
                                #         if self.im[i+1][x] < threshold:
                                #             count += 1
                                #         else:
                                #             break
                                #     if count >= chop:
                                #         self.im[i, j + c] = lineColor
                                # elif self.im[i-1, j+c] < threshold:
                                #     count = 0
                                #     for x in range(j, width):
                                #         if self.im[i-1][x] < threshold:
                                #             count += 1
                                #         else:
                                #             break
                                #     if count >= chop:
                                #         self.im[i, j + c] = lineColor

                            except IndexError:
                                self.im[i, j + c] = lineColor

                    j += countWidth
        #  loop 每一個pixel
        for j in xrange(width):
            for i in xrange(height):
                #  如果是黑色點 開始計算線段長度
                if self.CheckPixelIsBlack(self.im[i][j]):
                    countHeight = 0
                    #  移除橫線
                    for c in range(i, height):
                        if self.CheckPixelIsBlack(self.im[c][j]):
                            countHeight += 1
                        else:
                            break
                    if countHeight >= chop:
                        for c in range(countHeight):
                            try:
                                if self.CheckPixelIsWhite(self.im[i + c, j + 1]) and self.CheckPixelIsWhite(self.im[i + c, j - 1]):
                                    self.im[i + c, j] = lineColor
                            except IndexError:
                                    self.im[i + c, j] = lineColor
                                    pass

                    i += countHeight
        # 存檔
        # cv2.imwrite("D:\\CaptchaRaw\\" + self.imageName + '.png', self.im)
        self.dicImg.update({"干擾線檢測": self.im.copy()})

    #  傳入RGB的pixel 判斷是否是黑點
    def CheckPixelIsBlack(self, pixel, min= 70,max= 180):
        return self.CheckPixelColor(pixel,min,max)
    #  傳入RGB的pixel 判斷是否是白點
    def CheckPixelIsWhite(self, pixel, min= 160,max= 255):
        return self.CheckPixelColor(pixel, min, max)

    def CheckPixelColor(self,pixel, min ,max ):
        if  min< pixel[0] < max and min< pixel[1] < max and min < pixel[2] < max:
            return True
        else:
            return False

    def medianBlur(self):
        self.im = cv2.medianBlur(self.im, 3)
        self.dicImg.update({"中值模糊": self.im})


    #  切割圖片
    def splitImg(self):
        self.im = cv2.cvtColor(self.im , cv2.COLOR_BGR2GRAY)
        contours, hierarchy = cv2.findContours(self.im.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        #  按照X軸位置對圖片進行排序 確保我們從左到右讀取數字
        cnts = sorted([(c, cv2.boundingRect(c)[0]) for c in contours], key=lambda x: x[1])

        for index, (c, _) in enumerate(cnts):
            (x, y, w, h) = cv2.boundingRect(c)

            try:
                # 只將寬高大於 8 視為數字留存
                if w > 8 and h > 8:
                    add = True
                    for i in range(0, len(self.arr)):
                        # 這邊是要防止如 0、9 等，可能會偵測出兩個點，當兩點過於接近需忽略
                        if abs(cnts[index][1] - self.arr[i][0]) <= 3:
                            add = False
                            break
                    if add:
                        self.arr.append((x, y, w, h))

            except IndexError:
                pass
        Imgarr = [self.im[y: y + h, x: x + w] for x, y, w, h in self.arr]
        self.dicImg.update({"分割圖片": Imgarr})
        # self.showImgArray(Imgarr)


    #  圖片轉正
    def positiveImg(self):

        imgarr = []
        for index, (x, y, w, h) in enumerate(self.arr):
            roi = self.im[y: y + h, x: x + w]
            thresh = roi.copy()

            angle = 0
            smallest = 999
            row, col = thresh.shape

            for ang in range(-60, 61):
                M = cv2.getRotationMatrix2D((col / 2, row / 2), ang, 1)
                t = cv2.warpAffine(thresh.copy(), M, (col, row))

                r, c = t.shape
                right = 0
                left = 999

                for i in xrange(r):
                    for j in xrange(c):
                        if t[i][j] == 255 and left > j:
                            left = j
                        if t[i][j] == 255 and right < j:
                            right = j

                if abs(right - left) <= smallest:
                    smallest = abs(right - left)
                    angle = ang

            M = cv2.getRotationMatrix2D((col / 2, row / 2), angle, 1)
            thresh = cv2.warpAffine(thresh, M, (col, row))
            # resize 成相同大小以利後續辨識
            thresh = cv2.resize(thresh, (50, 50))
            imgarr.append(thresh)
        self.dicImg.update({"轉正": imgarr})

    #  將圖片顯示出來
    def showImg(self, img=None):

        if img is None:
            img = self.im

        cv2.imshow(self.imageName, img)
        cv2.namedWindow(self.imageName, cv2.WINDOW_NORMAL)
        #  調整視窗 讓標題列顯示出來
        cv2.resizeWindow(self.imageName, 250, 60)
        cv2.waitKey()

    #  將多個圖片顯示在一個figure
    def showImgEveryStep(self):
        diclength = len(self.dicImg)
        if diclength > 0:
            fig = plt.figure(figsize=(10, 10))
            gs = gridspec.GridSpec(diclength+1, 6)

            # 依序列出dict物件裡的圖片
            for index, key in enumerate(self.dicImg):
                #  如果不是list物件 就是圖片 可以呼叫imshow
                if not isinstance(self.dicImg[key], list):
                    ax = fig.add_subplot(gs[index, :6])
                    ax.imshow(self.dicImg[key], interpolation='nearest')
                    ax.set_title(key, fontproperties=self.font)
                else:
                    try:
                        for i, img in enumerate(self.dicImg[key]):
                            ax = fig.add_subplot(gs[index, i])
                            ax.imshow(img, interpolation='nearest')
                    except IndexError:
                        pass

            plt.tight_layout()
            plt.show()
        else:
            print '圖片數字陣列為空'


if __name__ == '__main__':
    for i in range(10):
        #  取得驗證碼資料夾裡 隨機一個驗證碼的路徑
        x = Image(r"D:\RailWayCapcha", random.choice(os.listdir(r"D:\RailWayCapcha")))
        # x.posterization()
        x.removeLines()
        # x.medianBlur()
        # x.removeNoise()
        # x.threshold()
        # x.splitImg()
        # x.positiveImg()
        x.showImgEveryStep()

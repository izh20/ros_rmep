import cv2
import time



class MessageItem(object):
    # 用于封装信息的类,包含图片和其他信息
    def __init__(self,frame,message):
        self._frame = frame
        self._message = message

    def getFrame(self):
        # 图片信息
        return self._frame

    def getMessage(self):
        #文字信息,json格式
        return self._message


class Tracker(object):
    '''
    追踪者模块,用于追踪指定目标
    '''
    def __init__(self, tracker_type="BOOSTING", draw_coord=True):
        '''
        初始化追踪器种类
        '''
        # 获得opencv版本
        (major_ver, minor_ver, subminor_ver) = (cv2.__version__).split('.')
        self.tracker_types = ['BOOSTING', 'MIL', 'KCF', 'TLD', 'MEDIANFLOW', 'GOTURN']
        self.tracker_type = tracker_type
        self.isWorking = False
        self.draw_coord = draw_coord
        # 构造追踪器
        print(int(major_ver*10+minor_ver))

        if int(major_ver*10+minor_ver) < 33:
            self.tracker = cv2.Tracker_create(tracker_type)
        else:
            if tracker_type == 'BOOSTING':
                self.tracker = cv2.TrackerBoosting_create()
            if tracker_type == 'MIL':
                self.tracker = cv2.TrackerMIL_create()
            if tracker_type == 'KCF':
                self.tracker = cv2.TrackerKCF_create()
            if tracker_type == 'TLD':
                self.tracker = cv2.TrackerTLD_create()
            if tracker_type == 'MEDIANFLOW':
                self.tracker = cv2.TrackerMedianFlow_create()
            if tracker_type == 'GOTURN':
                self.tracker = cv2.TrackerGOTURN_create()


    def initWorking(self, frame, box):
        '''
        追踪器工作初始化
        frame:初始化追踪画面
        box:追踪的区域
        '''
        if not self.tracker:
            raise Exception("追踪器未初始化")
        status = self.tracker.init(frame, box)
        if not status:
            raise Exception("追踪器工作初始化失败")
        self.coord = box
        self.isWorking = True
    def track(self, frame):
        '''
        开启追踪
        '''
        message = None
        if self.isWorking:
            status, self.coord = self.tracker.update(frame)
            if status:
                message = {"coord": [((int(self.coord[0]), int(self.coord[1])),
                                      (int(self.coord[0] + self.coord[2]), int(self.coord[1] + self.coord[3])))]}
                if self.draw_coord:
                    p1 = (int(self.coord[0]), int(self.coord[1]))
                    p2 = (int(self.coord[0] + self.coord[2]), int(self.coord[1] + self.coord[3]))
                    cv2.rectangle(frame, p1, p2, (255, 0, 0), 2, 1)
                    message['msg'] = "is tracking"
        return MessageItem(frame, message)


if __name__ == '__main__':

    # 初始化视频捕获设备
    gVideoDevice = cv2.VideoCapture(0)
    gCapStatus, gFrame = gVideoDevice.read()
    print("frame",type(gFrame))
    # 选择 框选帧
    print("按 n 选择下一帧，按 y 选取当前帧")
    while True:
        if (gCapStatus == False):
            print("捕获帧失败")
            quit()

        _key = cv2.waitKey(0) & 0xFF
        #print("key:",_key,"  n:",ord('n'),"  y",ord('y'))
        if(_key == ord('n')):
            gCapStatus,gFrame = gVideoDevice.read()
        if(_key == ord('y')):
            break
 
        cv2.imshow("pick frame",gFrame)
 
    # 框选感兴趣区域region of interest
    cv2.destroyWindow("pick frame")
    gROI = cv2.selectROI("ROI frame",gFrame,False)
    if (not gROI):
        print("空框选，退出")
        quit()
 
    # 初始化追踪器
    gTracker = Tracker(tracker_type="KCF")
    gTracker.initWorking(gFrame,gROI)
 
    # 循环帧读取，开始跟踪
    while True:
        gCapStatus, gFrame = gVideoDevice.read()
        if(gCapStatus):
            # 展示跟踪图片
            _item = gTracker.track(gFrame)
            cv2.imshow("track result",_item.getFrame())
 
            if _item.getMessage():
                # 打印跟踪数据
                print(_item.getMessage())
            else:
                # 丢失，重新用初始ROI初始
                print("丢失，重新使用初始ROI开始")
                gTracker = Tracker(tracker_type="KCF")
                gTracker.initWorking(gFrame, gROI)
 
            _key = cv2.waitKey(1) & 0xFF
            if (_key == ord('q')) | (_key == 27):
                break
            if (_key == ord('r')) :
                # 用户请求用初始ROI
                print("用户请求用初始ROI")
                gTracker = Tracker(tracker_type="KCF")
                gTracker.initWorking(gFrame, gROI)
 
        else:
            print("捕获帧失败")
            quit()

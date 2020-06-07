# coding=utf-8

import sys
import json
import base64
import requests
import json
import cv2
import time
sys.path.append('../../connection/network/')
import robot_connection
from liveview import RobotLiveview
# make it work in both python2 both python3
IS_PY3 = sys.version_info.major == 3
if IS_PY3:
    from urllib.request import urlopen
    from urllib.request import Request
    from urllib.error import URLError
    from urllib.parse import urlencode
    from urllib.parse import quote_plus
else:
    import urllib2
    from urllib import quote_plus
    from urllib2 import urlopen
    from urllib2 import Request
    from urllib2 import URLError
    from urllib import urlencode

# skip https auth
import ssl
ssl._create_default_https_context = ssl._create_unverified_context

API_KEY = 'K8FdbGfd5su2WZTfH69aBFi6'

SECRET_KEY = 'fxkTb1HVCU22kGfiTuQiVBndVxW5HMyV'


FACE_DETECT = "https://aip.baidubce.com/rest/2.0/face/v3/detect"
FACE_MATCH="https://aip.baidubce.com/rest/2.0/face/v3/match"
"""  TOKEN start """
TOKEN_URL = 'https://aip.baidubce.com/oauth/2.0/token'


"""
    get token
"""
def fetch_token():
    params = {'grant_type': 'client_credentials',
              'client_id': API_KEY,
              'client_secret': SECRET_KEY}
    post_data = urlencode(params)
    if (IS_PY3):
        post_data = post_data.encode('utf-8')
    req = Request(TOKEN_URL, post_data)
    try:
        f = urlopen(req, timeout=5)
        result_str = f.read()
    except URLError as err:
        print(err)
    if (IS_PY3):
        result_str = result_str.decode()


    result = json.loads(result_str)

    if ('access_token' in result.keys() and 'scope' in result.keys()):
        if not 'brain_all_scope' in result['scope'].split(' '):
            print ('please ensure has check the  ability')
            exit()
        return result['access_token']
    else:
        print ('please overwrite the correct API_KEY and SECRET_KEY')
        exit()

"""
    read file
"""
def read_file(image_path):
    f = None
    try:
        f = open(image_path, 'rb')
        return f.read()
    except:
        print('read image file fail')
        return None
    finally:
        if f:
            f.close()


"""
    call remote http server
"""
def request(url, data):
    req = Request(url, data.encode('utf-8'))
    has_error = False
    try:
        f = urlopen(req)
        result_str = f.read()
        if (IS_PY3):
            result_str = result_str.decode()
        return result_str
    except  URLError as err:
        print(err)

def face_match(unknow_image,known_image):
    '''
    人脸对比
    '''
    token = fetch_token()
    url = FACE_MATCH + "?access_token=" + token
    img_str = cv2.imencode('.jpg',unknow_image)[1].tostring()
    b1=str(base64.b64encode(img_str),"utf-8")
    b2=str(base64.b64encode(known_image),"utf-8")    
    data1=[
    {
        "image": b1,
        "image_type": "BASE64",
        "face_type": "LIVE",
        "quality_control": "LOW",
        "liveness_control": "NONE"
    },
    {
        "image": b2,
        "image_type": "BASE64",
        "face_type": "LIVE",
        "quality_control": "LOW",
        "liveness_control": "NONE"
    }
    ]
    params = json.dumps(data1) #indent=2按照缩进格式
    headers = {'content-type': 'application/json'}
    
    response = requests.post(url, data=params, headers=headers) 
    data=response.json()
    print(data)
    
    if data['error_msg']=='SUCCESS':
        score=data['result']['score']
        if score > 80:
            print('图片识别相似度度为'+str(score)+',是同一人')
            return True
        else:
            print('图片识别相似度度为'+str(score)+',不是同一人')
            return False
    else:
        print("图片识别失败")
        return False
    
def face_detect(image):
    '''
    人脸检测
    '''
    # get access token
    token = fetch_token()
    
    # concat url
    url = FACE_DETECT + "?access_token=" + token
    #print("url",url)
    # file_content = read_file(image)
    # print("type",type(file_content))
    #frame=cv2.imread(image)
    img_str = cv2.imencode('.jpg',image)[1].tostring()
    response = request(url, urlencode(
    {
        'image': base64.b64encode(img_str),
        'image_type': 'BASE64',
        'face_field': 'gender,age',
        'max_face_num': 1
    }))
    #print(response)
    #print(type(response))
    data = json.loads(response)
    if data["error_code"] == 0:
        face_num = data["result"]["face_num"]
        if face_num == 0:
            # could not find face
            print("no face in the picture")
            return False
        else:            
            # get face list
            face_list = data["result"]["face_list"]
            for i in range(face_num):
                location=face_list[i]['location']
                print(location) 
                cv2.putText(image,face_list[i]["gender"]["type"]+":"+str(face_list[i]["age"]),(int(location['left']),int(location['top']-10)), cv2.FONT_HERSHEY_SIMPLEX, 1,(255,255,255),2,cv2.LINE_AA)
                cv2.rectangle(image, (int(location['left']), int(location['top'])), (int(location['width']+location['left']), int(location['height']+location['top'])), (0, 0, 255), 2)
            roi = {'left':int(location['left']),'top':int(location['top']),'width':int(location['width']),'height':int(location['height'])}
           
            return roi
    # cv2.imshow('image',image)
    # cv2.waitKey(1) 
        

# if __name__ == '__main__':
#     connection = robot_connection.RobotConnection('192.168.42.2')
#     connection.open()
#     view = RobotLiveview(connection)
#     view.display()
#     image1=read_file('9.jpg')
#     image2=read_file('wyf.jpg')
#     #face_detect('wyf.jpg')
#     time.sleep(5)
    
    
#     while True:
#         re,image3 = view.read()
#         #print(type(image3))
#         #data1=face_match(image3,image1)
#         face_detect(image3)
#         time.sleep(0.5)
        


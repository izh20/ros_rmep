# Rmep

![robomaster ep](/media/izh20/文档/ep案例/案例介绍/image/robomaster_ep.jpg)

## 简介

本项目以Robomaster EP为开发对象，使用`jetson nano`的硬件平台，基于ROS机器人操作系统进行二次开发，这样一来，可以快速的使用ros的开源算法应用到Robomaster EP机器人上，进行一些算法验证或测试，也可以很容易的将英伟达的深度学习[开源项目](https://github.com/dusty-nv/jetson-inference)快速的应用于该机器人上，使Robomaster EP机器人更加智能，实现更多复杂有趣的功能，例如加入深度相机，即可对周围环境进行三维建模，加入激光雷达，即可进行室内建图和定位导航，由于时间紧张，相关硬件前几天才收到，这些有趣的功能目前都还没有实现。目前我只做了一些小的demo，接入了百度的API，实现一些简单的人工智能功能，例如语音识别(**该功能尚未接入ros框架，就暂且不开放出来**)，人脸跟踪。

## 安装

本代码依赖于ros，因此本教程以ros-melodic为例，硬件为jetson nano，进行安装讲解

1. [ros-melodic安装](https://blog.csdn.net/beckhans/article/details/90747828)

2. 由于python３不支持使用cv_bridge将numpy格式的图像格式转化成ros支持的图像格式，所以我们需要编译python3版本的[cv_bridge](https://stackoverflow.com/questions/49221565/unable-to-use-cv-bridge-with-ros-kinetic-and-python3)，

3. 下载源码

   ```bash
   $ cd ~
   $ sudo apt-get install git cmake
   $ mkdir catkin_ws
   $ cd catkin_ws
   $ mkdir src
   $ cd src
   $ git clone https://github.com/izh20/ros_rmep
   $ cd ../
   $ catkin_make
   ```

   

## 测试

首先需要启动`roscore`

```bash
$ roscore
```

然后需要启动rmep_base节点，来获取ep的基本数据，如视频流数据，里层计数据，云台等数据(TO DO)

然后将这些传感器的数据作为消息发布到ros网络中。同时该节点还会调用百度的人脸API进行人脸识别，将人脸的roi作为`face_detect`消息发布出去。

```bash
$ cd ~/catkin_ws/src/rm_ep/src
$ python3 rmep_base.py
```

* 使用kcf算法进行人脸跟踪

然后启动roborts_tracking_node，该节点订阅`image_topic`，`face_detect`数据，对人脸进行跟踪

```bash
$ cd ~/catkin_ws
$ source devel/setup.bash 
$ rosrun roborts_tracking roborts_tracking_test 
```

运行完以上命令后，面部对准rmep的相机，按下键盘的`g`，云台便会自动跟踪人脸，如果跟踪丢失,可以按下`s`,云台便会停止跟踪,再重新按下`g`进行跟踪


## gmapping
打开一个终端，获取ep的底盘数据，发布里程计数据并启动激光雷达，ｇmapping，tf_static
```bash
$ cd ~/catkin_ws
$ source devel/setup.bash
$ roslaunch rm_ep start_demo.launch
```
再打开一个终端,启动ep，将ep的数据通过topic发到ros中
```bash
$ cd ~/catkin_ws/src/rm_ep/scripts/
$ python3 rmep_bash.py
```
再打开一个终端，启动键盘控制,`i`前进，`,`后退,`j`左旋转，`l`右旋转
```bash
$ cd ~/catkin_ws/src/rm_ep/scripts/
$ python3 racecar_teleop.py
```
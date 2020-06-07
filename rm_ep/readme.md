# [Use cv_bridge with ROS and Python3](https://stackoverflow.com/questions/49221565/unable-to-use-cv-bridge-with-ros-kinetic-and-python3)
` from cv_bridge.boost.cv_bridge_boost import getCvType
ImportError: dynamic module does not define module export function (PyInit_cv_bridge_boost) `

* `$ cd ~/catkin_workspace/install/lib/python3/dist-packages`

* ` $ sudo cp -r cv_bridge /usr/lib/python3.6/dist-packages/
  `

## 完成人脸识别　　下一步将人脸识别和追踪算法结合　
｀ 5.13日
## 需要注意的是，即使使用的virtualenv中，python指向的是python3，但是只要不在.py文件中添加python3的shebang，rosrun还是会调用python2的。这样可以很方便地兼容原来Python2的Package。
尝试在python2 中使用tf,python3中

## rosdep update (解决方案)[https://blog.csdn.net/u013468614/article/details/102917569]
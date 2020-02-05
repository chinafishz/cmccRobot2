# cmccRobot2

作者：施仲夏

代码说明：

一、cmccRobot2与cmccRobot的区别：

    cmccRobot是目前自用的程序，代码结构适合单机使用，现计划在cmccRobot2项目重构架构，改为C/S模式，同时服务端增加消息队列功能，以利于多并发及批量处理
    cmccrobot的链接 ： https://github.com/chinafishz/cmccRobot
  
二、架构

    （一）itchatserver：负责收发微信信息，信息转化为命令，业务逻辑处理
    （二）kivyclient：前台客户端
    （三）thiftserver: 消息队列服务器，保存kivyclient及itchatserver的信息记录，异步批量处理
    
三、使用

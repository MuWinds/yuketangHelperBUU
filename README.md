# yuketangHelperBUU（原yuketangHelperBUULite）
雨课堂刷课脚本 fork from [Cat1007/yuketangHelperSCUTLite](https://github.com/Cat1007/yuketangHelperSCUTLite)

20241101更新：更新多线程刷课，更新扫码快速登录

20250307更新：更新AI答题，这个仓库再也不用带Lite后缀了 xD

#### 说点什么：

之前也有想到伪造心跳包的方法去快速刷网课，结果上GitHub一搜发现有师兄已经实现了这个思路。

在此十分感谢@[heyblackC](https://github.com/heyblackC)，让我不用再研究包里变量含义了hhhh

以下是原脚本仓库：

https://github.com/heyblackC/yuketangHelper



#### 脚本改进：

- 修改一些域名及对应的参数，适配本科生系统
- 修复一个正则表达式匹配Bug
- 修改了一些文本提示



#### 食用方法：

1. 安装好python环境

2. 安装pip（最好换一下国内的镜像源）[参考](https://blog.csdn.net/yuzaipiaofei/article/details/80891108)

3. 克隆或下载该仓库

4. 安装vscode以及vscode的python插件，并根据提示使用pip安装所需要的包

5. 安装依赖：pip install -r requirements.txt

6. 打开config.json和openai_ask.py文件，配置openai类型的大模型接口和system prompt，prompt示例：回答下面的问题,直接返回答案对应选项的字母,不要回复多余内容,如果不知道答案,请直接回答C,多选题回答格式是每个选项之间用一个半角逗号和一个空格分开，判断题只用返回true或false，不用回复标点符号。

7. 右上角绿色三角点击运行，运行之前先将自己的雨课堂账号和微信去进行绑定

8. 运行时输入雨课堂网站域名，输入完后会弹出微信登录二维码窗口（系统需要安装图像查看的软件），扫码登录后按提示输入对应的课程编号并回车

8. 直接爽到起飞🛫️

#+----+----+----+----+----+----+----+----+----+----+----+
#                     CMDLINE_MENU
# Developed by xxAp2005
# Last Update 2025/3/27Thr
# appreciate to MuWinds’s support
#
# current version v1.0.2
#+----+----+----+----+----+----+----+----+----+----+----+

#import time

# 导入datetime模块
import datetime
# 导入os模块
import os



enable_debug = "true"
if enable_debug == "true":
    print("[cmdline_menu]已启用debug输出")

#检测是否执行初始化
initialized = "false"

#获取系统用户名
username = os.getlogin()

#初始化头空格全局变量
headerSpace = "    "

# 获取当前日期
current_date = datetime.date.today()

# 格式化日期
formatted_date = current_date.strftime("%Y-%m-%d")


#初始化菜单尺寸 边框样式
def initialize_menu_type(menu_type,border_style):
    global initialized
    global menuType,borderStyle
    # 检查 menu_type 是否合法
    if menu_type not in ["small", "medium", "large"]:
        print("无效的菜单类型. 选择 'small', 'medium', 或者 'large'.")
        print("cmdlineMENU初始化失败，菜单类型已缺省为small！")
        menuType = "small"
    
    # 检查 border_style 是否合法
    if border_style not in ["solid", "dashed"]:
        print("无效的边框样式. 选择 'solid' 或 'dashed'.")
        print("边框样式已缺省为 solid！")
        borderStyle = "solid"
    else:
        borderStyle = border_style

    if enable_debug == "true":
        print("debug: at def_initialize_menu_type menuType设置为" + menu_type)
    menuType = menu_type
    initialized = "true"
    if enable_debug == "true":
        print("debug: at def_initialize_menu_type initialized = " + initialized + " menuType=" + menuType)

    # 调用 header_space 并传入 menuType
    header_space(menuType)  # 确保这里传入的是更新后的 menuType
    initialized = True
    if enable_debug == "true":
        print(f"debug: at def_initialize_menu_type menuType={menuType}, borderStyle={borderStyle}, initialized={initialized}")




def clear_cmdline_x10():                                    #生成10行空格用于清屏
    for _ in range(10):
        print(" ")



def small_border(border_style):
    if border_style == "solid":
        print("+" + "-" * 30 + "+")
    elif border_style == "dashed":
        print("+----" * 7 + "+")

def medium_border(border_style):
    if border_style == "solid":
        print("+" + "-" * 50 + "+")
    elif border_style == "dashed":
        print("+----" * 12 + "+")

def large_border(border_style):
    if border_style == "solid":
        print("+" + "-" * 70 + "+")
    elif border_style == "dashed":
        print("+----" * 17 + "+")




#def small_border():
#   print("+" + "-" * 30 + "+")  # 总宽度 32 字符
#
#def medium_border():
#    print("+" + "-" * 50 + "+")  # 总宽度 52 字符
#
#def large_border():
#    print("+" + "-" * 70 + "+")  # 总宽度 72 字符


#def small_border():                                         #打印小尺寸边框
#    print("+-----+-----+-----+-----+-----+-----+")
#
#def medium_border():                                        #打印中尺寸边框
#    print("+-----+-----+-----+-----+-----+-----+-----+-----+")
#
#def large_border():                                         #打印大尺寸边框
#    print("+-----+-----+-----+-----+-----+-----+-----+-----+-----+-----+-----+")



def drawBorder(menuType , border_style):       
                                  #打印边框
    if menuType == "small":
        small_border(border_style)
    
    if menuType == "medium":
        medium_border(border_style)
    
    if menuType == "large":
        large_border(border_style)


def header_space(menuType):
    global headerSpace
    if enable_debug == "true":
        print("debug: at def_header_space menuType = " + menuType)
    if menuType == "small":
        headerSpace = " " * 6  # 6个空格，适配 small_border 的宽度
    
    if menuType == "medium":
        headerSpace = " " * 10  # 10个空格，适配 medium_border 的宽度
    
    if menuType == "large":
        headerSpace = " " * 14  # 14个空格，适配 large_border 的宽度



#def header_space(menuType):
#    global headerSpace
#    if menuType == "small":
#        headerSpace = "    "
#    
#    if menuType == "medium":
#        headerSpace = "        "
#
#    if menuType == "large":
#        headerSpace = "            "
    


def create_option(sequence_number, option_text):
    global menuType
    # 统一格式：[序号] 选项文本，并自动适应 menuType 的缩进
    print(headerSpace + f"[{sequence_number}] {option_text}")

#def create_option(sequence_number, option_text):            #新建选项
#    global menuType
#    if menuType == "small":
#        print("    ")
#        print(headerSpace + "["+ sequence_number +"]" + option_text)
#
#    if menuType == "medium":
#        print("            ")
#        print(headerSpace + "            ["+ sequence_number +"]" + option_text)
#
#    if menuType == "large":
#        print("            ")
#        print(headerSpace + "            ["+ sequence_number +"]" + option_text)



def read_selection():                                       #读取选项
    selection = int(input("请输入选项序号："))
    return selection

def read_keyboardInput(title):                              #读取用户键盘输入
    content = str(input(title))
    return content


def singlespace():                                          #换行
    print(" ")



def raw_text(text):                                         #打印文本
    print(headerSpace + text)



def welcome_panel(motd):
    singlespace()
    print(headerSpace + f"欢迎!  {username}     今天是 {formatted_date}")
    singlespace()
    raw_text(motd)  # 直接调用 raw_text 确保对齐

#def welcome_panel(motd):
#    singlespace()
#    print(headerSpace + "欢迎!  " + username + "     现在是 " + formatted_date)
#    singlespace()
#    raw_text(headerSpace + motd)

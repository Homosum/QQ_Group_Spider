# coding=UTF-8
import getpass
from tools import MyWeb

if __name__ == '__main__':



    try:
            #获取用户数据
        qq_num=input("请输入你的QQ号:\n")
        qq_password=getpass.getpass('你的密码:\n')

        # run=False
    except Exception as e:
        print("账号密码错误,重来一遍吧")
        print(e)


        # 获取qq_group数据
    run = True
    while run:
        my_web = MyWeb()
        print("正在获取数据...\n")
        my_web.get_qq_group(qq_num, qq_password)

        you_group=input("需要爬去的qq群号码:\n")
        print("正在拼命爬取数据,请稍后...\n")
        my_web.get_qq_nums(qq_num,qq_password,you_group)
        choice = raw_input('输入任意键退出,输入Y继续:')
        go_on = 'Y'
        go_on_m = 'y'
        if choice == go_on or go_on_m:
            run=False
        else:
            run=True


    exit()





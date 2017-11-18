# coding=UTF-8
from selenium import webdriver
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
from lxml import etree
import time
# from models import  QQ_Member
import random
import codecs
import ConfigParser
from pandas import DataFrame
import sys
import logging
import threading
from pyvirtualdisplay import Display

#输出日志文件
logger = logging.getLogger()
logger.setLevel(logging.INFO)
logfile = './logger.txt' #日志文件的保存位置
fh = logging.FileHandler(logfile, mode='w') #日志文件输出配置
fh.setLevel(logging.DEBUG)

ch = logging.StreamHandler()
ch.setLevel(logging.WARNING)  #控制台输出配置

formatter = logging.Formatter("%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s")
fh.setFormatter(formatter)
ch.setFormatter(formatter)
logger.addHandler(fh)
logger.addHandler(ch)


#设置display
display = Display(visible=0, size=(1440,900))
display.start()

class MyWeb:
    def __init__(self):
        self.groupDict = {}
        #self.chromedirverPath = '/Users/Homosum/Downloads/chromedriver' #chromedirver的位置
        self.chromedirverPath = '/Users/Homosum/Downloads/geckodriver'
        self.qqSavePath = '/opt/scripts/qqspider/qqfile'  #结果csv文件的保存位置
        self.groupSavePath = '/opt/scripts/qqspider/groupfile'


    def get_group(self,user,password):
        driver = webdriver.Firefox()
        driver.get("https://qun.qq.com/member.html")
        print('i got it')
        IframeElement = driver.find_element_by_name("login_frame")
        driver.switch_to_frame(IframeElement)
        try:
            driver.find_element_by_xpath("//*[@id='bottom_qlogin']/a[1]").click()  # 登录界面
            driver.find_element_by_xpath("//*[@id='u']").send_keys(user)
            driver.find_element_by_xpath("//*[@id='p']").send_keys(password)

            driver.find_element_by_xpath("//*[@id='login_button']").click()  # 点击登录

            time.sleep(1.5)

            driver.switch_to_default_content()  # 防止出现TypeError: can't access dead object 错误特别重要

            web_data = driver.page_source
            selector = etree.HTML(web_data)
            # print('8')
        except Exception as e:
            logger.warning("登录失败,请检查QQ号和账号及网络状态")
            # print('9')
        try:
            qq_numbers = selector.xpath("//li[@data-id]/@data-id")  # 获取所有的QQ群组号码和名称
            qq_names = selector.xpath("//li[@data-id]/@title")
            temp_array = zip(qq_numbers, qq_names)
            dic_array = []
            for arr in temp_array:
                group = QQ_Group()
                group.num = arr[0]
                group.name = arr[1]
                dic = classToDict(group)
                dic_array.append(dic)
            frame = DataFrame(dic_array)
            frame.fillna('NA')
            filePath = my_web.groupSavePath
            path = ('%s/%s.csv' % (filePath, user))
            frame.to_csv(path, encoding='utf-8')
            print('已保存%s' % path)
            logger.info('已保存%s' % path)
        except Exception as e:
            # print('10')
            logger.info(e)
            logger.info('QQ服务异常失败')
            logger.warning("QQ服务器异常")
        driver.close()



    def get_qq_group(self, user, password):
        # cf = ConfigParser.ConfigParser()
        # cf.read('conf.ini')
        # chromedriver = '/Users/Homosum/Downloads/chromedriver'
        # driver = webdriver.Chrome(self.chromedirverPath)
        driver = webdriver.Firefox()
        driver.get("https://qun.qq.com/member.html")
	print('i got it')
        IframeElement = driver.find_element_by_name("login_frame")
        driver.switch_to_frame(IframeElement)
        try:
            driver.find_element_by_xpath("//*[@id='bottom_qlogin']/a[1]").click()  # 登录界面
            driver.find_element_by_xpath("//*[@id='u']").send_keys(user)
            driver.find_element_by_xpath("//*[@id='p']").send_keys(password)

            driver.find_element_by_xpath("//*[@id='login_button']").click()  # 点击登录

            time.sleep(1.5)

            driver.switch_to_default_content()  # 防止出现TypeError: can't access dead object 错误特别重要

            web_data = driver.page_source
            selector = etree.HTML(web_data)
	   #print('8')
        except Exception as e:
            logger.warning("登录失败,请检查QQ号和账号及网络状态")
	    #print('9')
        try:
            qq_numbers = selector.xpath("//li[@data-id]/@data-id")  # 获取所有的QQ群组号码和名称
            qq_names = selector.xpath("//li[@data-id]/@title")
            temp_array = zip(qq_numbers, qq_names)
            self.groupDict = dict(temp_array)
            threads = []
            for qq_name, qq_number in zip(qq_names, qq_numbers):
                print("%-20s  %-13s " % (qq_name, qq_number))
		logger.info("%-20s  %-13s " % (qq_name, qq_number))
                qq_groupS = str(qq_number)
                certain_thread = threading.Thread(target=self.get_qq_nums,args=(user,password,qq_groupS))
                threads.append(certain_thread)
#                certain_thread.setDaemon(True)
#                certain_thread.start()

            for threadOne in threads:
                threadOne.setDaemon(True)
                threadOne.start()
                while True:
                    if(len(threading.enumerate())<2):
                        break

            # self.get_qq_nums(user,password,qq_groupS)
	    #print('11')
        except Exception as e:
	    #print('10')
            logger.info(e)
            logger.info('QQ服务异常失败')
            logger.warning("QQ服务器异常")
        driver.close()

    def get_qq_nums(self, user, password, qq_group):
        try:
#            cf = ConfigParser.ConfigParser()
#            cf.read('conf.ini')
        # chromedriver = cf.get('main', 'path')
#            chromedriver = "/Users/Homosum/Downloads/chromedriver"
#             driver = webdriver.Chrome(self.chromedirverPath)

            driver = webdriver.Firefox()
            driver.get("http://qun.qq.com/member.html#gid={}".format(qq_group))
            IframeElement = driver.find_element_by_name("login_frame")
            driver.switch_to_frame(IframeElement)

            driver.find_element_by_xpath("//*[@id='bottom_qlogin']/a[1]").click()  # 登录界面
            driver.find_element_by_xpath("//*[@id='u']").send_keys(user)
            driver.find_element_by_xpath("//*[@id='p']").send_keys(password)

            driver.find_element_by_xpath("//*[@id='login_button']").click()  # 点击登录
            time.sleep(1.5)

            driver.switch_to_default_content()  # 防止出现TypeError: can't access dead object 错误特别重要
            time.sleep(1.5)
            web_data = driver.page_source
            selector = etree.HTML(web_data)
            try:
		#print('999')
                people_num = selector.xpath("//*[@id='groupMemberNum']/text()")  # 获取群组人数量
                print('people_num:%s'%people_num)
		if len(people_num) == 0:
                   people_nums = 0
		else:
		   people_nums = int(people_num[0])
		#print('777')
            except Exception as e:
                logger.warning("网络问题")
                driver.close()

            count = 1

            logger.info('QQ群人数%d' % (people_nums))

            for _ in range(int(people_nums / 20)):
                js = "var q=document.documentElement.scrollTop=500000"
                #            js = "var q=document.body.scrollTop=500000"
                driver.execute_script(js)
                time.sleep(2)
                count += 1
	    #print('666')
            web_data = driver.page_source  # 重新获取网页源代码
            selector = etree.HTML(web_data)
            people_nicks = selector.xpath("//tbody[@class='list']/tr/td[3]/span/text()")  # 获取昵称
            people_nicks = get_freshList(people_nicks)

            people_names = selector.xpath(
                "//tbody[@class='list']/tr/td[4]/span/text()")  # 获取群名片                                  #获取群名片
            people_names = get_freshList(people_names)

            people_QQs = selector.xpath("//tbody[@class='list']/tr/td[5]/text()")  # 获取qq号
            people_QQs = get_freshList(people_QQs)

            people_sexs = selector.xpath("//tbody[@class='list']/tr/td[6]/text()")  # 获取性别
            people_sexs = get_freshList(people_sexs)

            people_ages = selector.xpath("//tbody[@class='list']/tr/td[7]/text()")  # 获取Q龄
            people_ages = get_freshList(people_ages)

            people_grades = selector.xpath("//tbody[@class='list']/tr/td[9]/text()")  # 获取活跃度
            people_grades = get_freshList(people_grades)
	    #print('555')
            result_array = []
            countS = 0
            #name_ = driver.find_element_by_xpath("//*[@id='groupTit']").text
	    name_A = selector.xpath("//*[@id='groupTit']/text()")
            print('name_%s'%name_A)
            name_ = name_A[0]
            logger.info('用户:%s,群号:%s,爬取人数:%d' % (user,name_,len(people_QQs)))
	    #print('用户:%s,群号:%s,爬取人数:%d' % (user,name_,len(people_QQs)))
	    #print('444')
            for countS in range(len(people_QQs)):
                member = QQ_Member()
                member.name = people_nicks[countS]
                member.sex = people_sexs[countS]
                member.qq_age = people_ages[countS]
                member.num = people_QQs[countS]
                member.source = name_
                dic = classToDict(member)
                result_array.append(dic)
	    #print('333')
            frame = DataFrame(result_array)
            frame.fillna('NA')
            filePath = my_web.qqSavePath
            path = ('%s/%s.csv' % (filePath, qq_group))
            frame.to_csv(path, encoding='utf-8')
	    #print('222')
	    print('已保存%s'%path)
	    logger.info('已保存%s'%path)
            driver.close()
	    #print('111')
            pass
        except Exception as e:
            driver.close()


class QQ_Group:
    def __init__(self):
        self.num = ''
        self.name = ''


class QQ_Member:
    def __init__(self):
        self.name = ''
        self.num = ''
        self.sex = ''
        self.qq_age = ''
        self.source = ''

def get_freshList(dataList):
    freshList = []
    for i in dataList:
        freshList.append("".join(i.replace('\n', '').replace(' ', '').replace('\t', '')))

    return freshList


def classToDict(obj):
    is_list = obj.__class__ == [].__class__
    is_set = obj.__class__ == set().__class__

    if is_list or is_set:
        obj_arr = []
        for o in obj:
            dict = {}
            dict.update(o.__dict__)
            obj_arr.append(dict)
        return obj_arr
    else:
        dict = {}
        dict.update(obj.__dict__)
        return dict


if __name__ == '__main__':


    sys.setrecursionlimit(1000000) #这里设置为一百万



    try:
            #获取用户数据
       # qq_num=input("请输入你的QQ号:\n")
       # qq_password=getpass.getpass('你的密码:\n')
        qq_num = sys.argv[1]
        qq_password = sys.argv[2]
#        you_group = sys.argv[3]
        # run=False
    except Exception as e:
        logger.info("账号密码错误,重来一遍吧")
        logger.info(e)


        # 获取qq_group数据
    # run = True
    # while run:
    my_web = MyWeb()
        # print("正在获取数据...\n")
    my_web.get_group(qq_num,qq_password)
    # my_web.get_qq_group(qq_num, qq_password)
    # my_web.get_qq_nums(qq_num,qq_password,you_group)


    exit()







# coding=UTF-8
#Web
from selenium import webdriver
from lxml import etree
import time
from models import  QQ_Member
import random
import codecs
import ConfigParser
from pandas import DataFrame
#####################################

def get_freshList(dataList):
    freshList=[]
    for i in dataList:
        freshList.append("".join(i.replace('\n','').replace(' ','').replace('\t','')))

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

class MyWeb:
    def __init__(self):
        self.groupDict  = {}
    


    def get_qq_group(self,user, password):
        cf = ConfigParser.ConfigParser()
        cf.read('conf.ini')
        chromedriver = cf.get('main', 'path')
        # chromedriver = "/Users/Homosum/Downloads/chromedriver"
        driver = webdriver.Chrome(chromedriver)
        driver.get("http://qun.qq.com/member.html")

        IframeElement = driver.find_element_by_name("login_frame")
        driver.switch_to_frame(IframeElement)
        try:
            driver.find_element_by_xpath("//*[@id='bottom_qlogin']/a[1]").click()  # 登录界面
            driver.find_element_by_xpath("//*[@id='u']").send_keys(user)
            driver.find_element_by_xpath("//*[@id='p']").send_keys(password)

            driver.find_element_by_xpath("//*[@id='login_button']").click()  # 点击登录
            time.sleep(2)

            driver.switch_to_default_content()  # 防止出现TypeError: can't access dead object 错误特别重要

            web_data = driver.page_source
            selector = etree.HTML(web_data)
        except Exception as e:
            print("登录失败,请检查QQ号和账号及网络状态")


        try:
            qq_numbers= selector.xpath("//li[@data-id]/@data-id")  # 获取所有的QQ群组号码和名称
            qq_names= selector.xpath("//li[@data-id]/@title")
            temp_array = zip(qq_numbers,qq_names)
            self.groupDict = dict(temp_array)
            for qq_name, qq_number in zip(qq_names, qq_numbers):
                print("%-20s  %-13s " % (qq_name, qq_number))
        except Exception as e:
            print(e)
            print("QQ服务器异常")
        driver.quit()








    def get_qq_nums(self,user,password,qq_group):
        cf = ConfigParser.ConfigParser()
        cf.read('conf.ini')
        chromedriver = cf.get('main', 'path')
        # chromedriver = "/Users/Homosum/Downloads/chromedriver"
        driver = webdriver.Chrome(chromedriver)
        driver.get("http://qun.qq.com/member.html#gid={}".format(qq_group))

        IframeElement = driver.find_element_by_name("login_frame")
        driver.switch_to_frame(IframeElement)

        driver.find_element_by_xpath("//*[@id='bottom_qlogin']/a[1]").click()  # 登录界面
        driver.find_element_by_xpath("//*[@id='u']").send_keys(user)
        driver.find_element_by_xpath("//*[@id='p']").send_keys(password)

        driver.find_element_by_xpath("//*[@id='login_button']").click()  # 点击登录
        time.sleep(2)

        driver.switch_to_default_content()  # 防止出现TypeError: can't access dead object 错误特别重要
        time.sleep(2)
        web_data = driver.page_source
        selector = etree.HTML(web_data)
        try:
            people_num = selector.xpath("//*[@id='groupMemberNum']/text()")  # 获取群组人数量
            people_num = int(people_num[0])
        except Exception as e:
            print("网络问题")

        count = 1

        print 'QQ群人数%d'%(people_num)

        for _ in range(int(people_num / 20)):
            # js = "var q=document.documentElement.scrollTop=500000"
            js = "var q=document.body.scrollTop=500000"
            driver.execute_script(js)
            time.sleep(random.randint(2, 6))
            print("爬取第"+str(count)+"页...")
            count += 1

        web_data = driver.page_source  # 重新获取网页源代码
        selector = etree.HTML(web_data)
        people_nicks = selector.xpath("//tbody[@class='list']/tr/td[3]/span/text()")  # 获取昵称
        people_nicks = get_freshList(people_nicks)

        people_names=selector.xpath("//tbody[@class='list']/tr/td[4]/span/text()")     #获取群名片                                  #获取群名片
        people_names=get_freshList(people_names)

        people_QQs = selector.xpath("//tbody[@class='list']/tr/td[5]/text()")  # 获取qq号
        people_QQs = get_freshList(people_QQs)

        people_sexs = selector.xpath("//tbody[@class='list']/tr/td[6]/text()")  # 获取性别
        people_sexs = get_freshList(people_sexs)

        people_ages = selector.xpath("//tbody[@class='list']/tr/td[7]/text()")  # 获取Q龄
        people_ages = get_freshList(people_ages)

        people_grades = selector.xpath("//tbody[@class='list']/tr/td[9]/text()")  # 获取活跃度
        people_grades = get_freshList(people_grades)

        result_array = []
        countS = 0
        key_ = '%s' % (qq_group)
        name_ = self.groupDict[key_]
        print '爬取人数%d'%(len(people_QQs))
        for countS in range(len(people_QQs)):
            member = QQ_Member()
            member.name = people_nicks[countS]
            member.sex = people_sexs[countS]
            member.qq_age = people_ages[countS]
            member.num = people_QQs[countS]
            member.source = name_
            dic = classToDict(member)
            result_array.append(dic)
        frame = DataFrame(result_array)
        frame.fillna('NA')
        filePath = raw_input('输入要保存的文件夹:\n')
        path = ('%s/%s.csv'%(filePath,qq_group))
        frame.to_csv(path,encoding='utf-8')
        driver.quit()

        pass


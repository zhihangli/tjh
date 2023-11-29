import requests
import urllib
import json
import numpy as np
import time
import datetime
import os

##########需配置参数##########
param_set = {
    'mode' : 0,   #运行模式：0-有空闲即通知；1-精确日期通知
    'reqdate' : '2022-08-05',	#目标日期,运行模式为0时可不设置
    'reqplace' : '汉口院区',		#目标院区：汉口院区、中法新城院区、光谷院区
    'ksname' : '妇产科',		#科室名称
    'ysname' :'徐晓燕',
    'gap_time' : 120,		#刷新间隔时间s
    "restart_time":  1800,	#刷到号以后时间间隔s
    'cycle_number': 29,  #循环次数
    'PUSH_PLUS_TOKEN': '',#pushplus密钥
    }
##########结束配置参数##########

code_table = {
    '汉口院区' : '270017',
    '中法新城院区': '270023',
    '光谷院区' : '270018',
    '徐晓燕' : '101235',
    '陈素华' :'100416',
    '乌剑利' : '101574',
    '林星光' : '101573',
    '邓东锐' : '100757',
    '曾万江' : '100422',
    '吴媛媛' : '101457',
    '石鑫玮' : '101760', #测试用
    '邓又斌': '100900',
    '妇产科':'1763ZJH',
    '超声影像科':'1632',
    }
# 请求头
headers_tj = {"Content-Type": "application/x-www-form-urlencoded"}

#请求数据
formdata_tj = {
	'yqcode1':code_table.get(param_set.get('reqplace')),
	'kscode1':code_table.get(param_set.get('ksname')),
	'doctorCode':code_table.get(param_set.get('ysname')),
	'scheduleType':'',
	'laterThan17':'true'
    }

#对请求数据做编码
fromdata_tj = urllib.parse.urlencode(formdata_tj).encode(encoding='utf-8')
url_tj = 'https://tjhapp.com.cn:8013/yuyue/getdocinfoNewV2'

#notify 通过 push+ 推送消息
def pushplus_bot(title: str, content: str ,PUSH_PLUS_TOKEN):
    url = "http://www.pushplus.plus/send"
    data = {
        "token": PUSH_PLUS_TOKEN,
        "title": title,
        "content": content,
    }
    body = json.dumps(data).encode(encoding="utf-8")
    headers = {"Content-Type": "application/json"}
    response = requests.post(url=url, data=body, headers=headers).json()
    if response["code"] == 200:
        print("消息推送成功！")
    else:
        url_old = "http://pushplus.hxtrip.com/send"
        headers["Accept"] = "application/json"
        response = requests.post(url=url_old, data=body, headers=headers).json()
        if response["code"] == 200:
            print("hxtrip推送成功！")
        else:
            print("消息推送失败！")
#查询
def precision_status(r_tj):
    hospitalmc = []
    deptName = []
    clinicDate = []
    clinicDuration = []
    #sumFee = []
    yystatus = []
    for i in range(np.size(r_tj['datalistbyyq'])):
        if r_tj['datalistbyyq'][i]['hospitalmc'] == param_set.get('reqplace'):
            for j in range(np.size(r_tj['datalistbyyq'][i]['schedule'])):
                if r_tj['datalistbyyq'][i]['schedule'][j]['deptName'][0:2] != '知名':
                    hospitalmc.append(r_tj['datalistbyyq'][i]['hospitalmc'])
                    deptName.append(r_tj['datalistbyyq'][i]['schedule'][j]['deptName'])
                    clinicDate.append(r_tj['datalistbyyq'][i]['schedule'][j]['clinicDate'])
                    clinicDuration.append(r_tj['datalistbyyq'][i]['schedule'][j]['clinicDuration'])
                    #sumFee.append(r_tj['datalistbyyq'][i]['schedule'][j]['sumFee'])
                    yystatus.append(r_tj['datalistbyyq'][i]['schedule'][j]['yystatus'])
    data = np.vstack([hospitalmc,deptName,clinicDate,clinicDuration,yystatus])
    [l,r] = np.where(data == param_set.get('reqdate'))
    if data[4,r[0]] == '预约':
        print('--------------------\n%s可预约的专家号详情：'%r_tj['datainfo']['doctorName'])
        print(data[1,0],data[0,0],datetime.datetime.now().strftime('%F %T'))
        print(data.T)
        title = '%s%s%s%s有可预约的专家号'%(param_set.get("reqdate"),r_tj['datainfo']['doctorName'],data[0,r][0],data[1,r][0])
        content = '医生：%s\n%s'%(r_tj['datainfo']['doctorName'],data.T)
        pushplus_bot(title,content,param_set.get('PUSH_PLUS_TOKEN'))
        pushplus_bot(title,content,param_set.get('PUSH_PLUS_TOKEN_L'))
        result = '可预约'
    else:
        result = '号满'
    return result

def check_status(r_tj):
    hospitalmc = []
    deptName = []
    clinicDate = []
    clinicDuration = []
    #sumFee = []
    yystatus = []
    for i in range(np.size(r_tj['datalistbyyq'])):
        for j in range(np.size(r_tj['datalistbyyq'][i]['schedule'])):
            if r_tj['datalistbyyq'][i]['schedule'][j]['deptName'][0:2] != '知名':
                hospitalmc.append(r_tj['datalistbyyq'][i]['hospitalmc'])
                deptName.append(r_tj['datalistbyyq'][i]['schedule'][j]['deptName'])
                clinicDate.append(r_tj['datalistbyyq'][i]['schedule'][j]['clinicDate'])
                clinicDuration.append(r_tj['datalistbyyq'][i]['schedule'][j]['clinicDuration'])
                #sumFee.append(r_tj['datalistbyyq'][i]['schedule'][j]['sumFee'])
                yystatus.append(r_tj['datalistbyyq'][i]['schedule'][j]['yystatus'])
    data = np.vstack([hospitalmc,deptName,clinicDate,clinicDuration,yystatus])
    data2=data.tolist()
    if data2[4].count('预约') != 0:
        print('--------------------\n%s可预约的专家号详情：'%r_tj['datainfo']['doctorName'])
        print(data[1,0],data[0,0],datetime.datetime.now().strftime('%F %T'))
        print(data.T)
        title = '%s有可预约的专家号'%(r_tj['datainfo']['doctorName'])
        content = '医生：%s\n%s'%(r_tj['datainfo']['doctorName'],data.T)
        pushplus_bot(title,content,param_set.get('PUSH_PLUS_TOKEN'))
        pushplus_bot(title,content,param_set.get('PUSH_PLUS_TOKEN_L'))
        result = '可预约'
    else:
        result = '号满'
    return result

#关闭警告
requests.packages.urllib3.disable_warnings()
#查询医生工作院区和科室数量
print('正在查询',param_set['ysname'],'医生挂号信息。')
if (param_set.get('mode')==1):
    print('运行模式为1，目标挂号时间及院区为：\n',param_set['reqdate'],param_set['reqplace'])
elif (param_set.get('mode')==0):
    print('运行模式为0，将通知所有可预约信息。')
loop_count = 0
while loop_count <param_set.get('cycle_number') :
    loop_count = loop_count + 1
    response_tj = json.loads(requests.post(url_tj,fromdata_tj,headers=headers_tj,verify=False).text)
    if response_tj['success']:
        if param_set.get('mode')==1:
            result = precision_status(response_tj)
        elif param_set.get('mode')==0:
            result = check_status(response_tj)
    else:
        result = '查询失败'
    print('第%s次查询，结果为：'%str(loop_count),result)
    if result == '可预约':
        #showinfo('有可预约的专家号','有可预约的专家号')
        time.sleep(param_set.get('restart_time'))
    else:
        time.sleep(param_set.get('gap_time'))

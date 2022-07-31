import requests
import urllib
import json
import numpy as np
import time

##########需配置参数##########
param_set = {
'reqdate' : '2022-08-05',	#目标日期
'reqplace' : '汉口院区',		#目标院区
'yqcode' : '270017',	#院区代码	#汉口院区270017	#中法新城270023
'kscode' : '1770',		#科室代码	#妇产科1770
'yscode' : '100416',    #医生代码   #徐晓燕101235  #陈素华100416
'PUSH_PLUS_TOKEN': '',  #pushplus密钥
'gap_time' : 120,		#刷新间隔时间s
'restart_time':  1800,	#刷到号以后时间间隔s
'cycle_number':29       #设置循环次数
}
##########结束配置参数##########

headers_tj = {"Content-Type": "application/x-www-form-urlencoded"}# 请求头
formdata_tj = {     #请求数据
	"yqcode1":param_set.get("yqcode"),
	"kscode1":param_set.get("kscode"),
	"doctorCode":param_set.get("yscode"),
	"scheduleType":"",
	"laterThan17":"true"
}
fromdata_tj = urllib.parse.urlencode(formdata_tj).encode(encoding='utf-8')#对数据编码
url_tj = 'https://tjhapp.com.cn:8013/yuyue/getdocinfoNewV2'#请求链接

#通过 push+ 推送消息
def pushplus_bot(title: str, content: str ,PUSH_PLUS_TOKEN) -> None:
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

#请求结果处理
def check_status(r_tj):
    hospitalmc = []
    deptName = []
    clinicDate = []
    clinicDuration = []
    #sumFee = []
    yystatus = []
    for i in range(np.size(r_tj['datalistbyyq'])):
        if(r_tj['datalistbyyq'][i]['hospitalmc'] == param_set.get('reqplace')):
            for j in range(np.size(r_tj['datalistbyyq'][i]['schedule'])):
                if(r_tj['datalistbyyq'][i]['schedule'][j]['deptName'][0:2] != '知名'):
                    hospitalmc.append(r_tj['datalistbyyq'][i]['hospitalmc'])
                    deptName.append(r_tj['datalistbyyq'][i]['schedule'][j]['deptName'])
                    clinicDate.append(r_tj['datalistbyyq'][i]['schedule'][j]['clinicDate'])
                    clinicDuration.append(r_tj['datalistbyyq'][i]['schedule'][j]['clinicDuration'])
                    #sumFee.append(r_tj['datalistbyyq'][i]['schedule'][j]['sumFee'])
                    yystatus.append(r_tj['datalistbyyq'][i]['schedule'][j]['yystatus'])
    data = np.vstack([hospitalmc,deptName,clinicDate,clinicDuration,yystatus])
    [l,r] = np.where(data == param_set.get('reqdate'))
    if(data[4,r] == '预约'):
        print('--------------------\n%s可预约的专家号详情：'%r_tj['datainfo']['doctorName'])
        print(data[1,0],data[0,0])
        print(data.T)
        title = '%s%s%s%s有可预约的专家号'%(param_set.get("reqdate"),r_tj['datainfo']['doctorName'],data[0,r][0],data[1,r][0])
        content = '医生：%s\n%s'%(r_tj['datainfo']['doctorName'],data.T)
        pushplus_bot(title,content,param_set.get('PUSH_PLUS_TOKEN'))
    result = data[4,r][0]
    return result

requests.packages.urllib3.disable_warnings()#关闭警告
loop_count = 0
print('正在查询挂号信息。\n目标挂号时间及院区为：\n',param_set['reqdate'],param_set['reqplace'])
while loop_count < param_set.get('cycle_number') :
    response_tj = json.loads(requests.post(url_tj,fromdata_tj,headers=headers_tj,verify=False).text)
    result = check_status(response_tj)
    loop_count = loop_count + 1
    print('第%s次查询 %s 医生，结果为：'%(str(loop_count),response_tj['datainfo']['doctorName']),result)
    if (result == '预约'):
        time.sleep(param_set.get('restart_time'))
    else:
        time.sleep(param_set.get('gap_time'))
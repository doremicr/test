# _*_ coding:utf-8 _*_
import os
import yaml
import requests
import logging
import re
import json
import time
import datetime



current_path = os.path.abspath(os.path.dirname(__file__))


def http_request(method, url, params=None, headers=None, auth=None, data=None):
    logging.info("method: {}, url: {}".format(method.lower(), url))
    proxies = {
        "http": "socks5://localhost:1082"
    }
    #params=json.dumps(params)
    #headers=json.dumps(headers)
    #data=json.dumps(data)
    #auth=json.dumps(auth)
    try:
        r = requests.request(
            method.lower(),
            url,
            params=json.dumps(params),
            headers=headers,
            auth=auth,
            data=json.dumps(data),
            proxies=proxies)

        return 200,'', r
    except Exception as e:
        return 501, 'request is error.', e

#验证数据类型
def typeValidate(type1,source):
    if isinstance(source,unicode):
        source=source.decode('string_escape')#字符串解码 unicode->str
    if type1=='int':
        return isinstance(source,int)
    elif type1=='dict':
        return isinstance(source,dict)
    elif type1=='list':
        return isinstance(source,list)
    elif type1=='str':
        return isinstance(source,str)
    elif type1=='bool':
        return isinstance(source,bool)
    elif type1=='float':
        return isinstance(source,float)
    elif type=='tuple':
        return isinstance(source,tuple)
    return isinstance(source,str)

#验证字符串长度
def lenValidate(length,source):
    if len(source)==length:
        return True
    else:
        return False


#验证正则表达式
def reValidate(patten1,source):
    if re.match(r""+patten1,source)!=None:
        return True
    else:
        return False
#验证最大长度
def maxlenValidate(length,source):
    if(len(source)>length):
        return False
    else:
        return True

#验证最小长度
def minlenValidate(length,source):
    if(len(source)<length):
        return False
    else:
        return True
#验证url
def urlValidate(url):
    regex = re.compile
    r'^(?:http|ftp)s?://'  # http:// or https://
    r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'  # domain...
    r'localhost|'  # localhost...
    r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
    r'(?::\d+)?'  # optional port
    r'(?:/?|[/?]\S+)$', re.IGNORECASE

    if re.match(regex,url)!=None:
        return True
    else:
        return False

#验证值
def valueValidate(src,det):

    if(src==det):
        return True
    else:
        return False

#迭代分析数据
def iteration(info,json):
    #不存在数据嵌套，为尾节点
    num=PD(info)
    if num==0:
        keys=info.keys()
        for k in keys:
            if k == 'value':
                if valueValidate(info[k], json) == False:
                    print("value valid Failed source: %s, dest: %s"%(info[k], json))

                    return False
            elif k == 'len':
                if lenValidate(info[k], json) == False:
                    print("len Failed source: %s, dest: %s"%(info[k], json))
                    return False
            elif k == 'regular':
                if reValidate(info[k], json) == False:
                    print("re Failded source: %s, dest: %s"%(info[k], json))
                    return False
            elif k == 'max':
                if maxlenValidate(info[k], json) == False:
                    print("max source: %s, dest: %s"%(info[k], json))
                    return False
            elif k == 'min':
                if minlenValidate(info[k], json) == False:
                    print("min source: %s, dest: %s"%(info[k], json))
                    return False
            elif k == 'type':
                if typeValidate(info[k], json) == False:
                    print("type Failded source: %s, dest: %s"%(info[k], json))
                    return False
        return True
    elif num==1:
        keys = info.keys()
        for k1 in keys:
            if json[k1]!=None:
                if iteration(info[k1], json[k1])==False:
                    return False

            else:
                print("接口返回的 %s 值为None"%(k1))
        return True
    elif num==2:
        if isinstance(info,list):

            if json!=None and len(json)!=0:
                for i in range(len(info)):
                    if iteration(info[i], json[i]) == False:
                        return False
            else:
                print("接口返回的 %s 值为None"%(json))

            return True

    

#判断需要解析的数据类型   0->尾节点数据，直接解析；1->dict；2->array
def PD(info):
    if isinstance(info,dict):
        keys = info.keys()
        for k in keys:
            if isinstance(info[k],dict):
                return 1

    elif isinstance(info,list):
        return 2
    return 0

def analyzeInfo(info,url,method,params,data,headers,auth):
    #url = info['url']
    #for i in range(len(url)):
        print("正在进行请求，URL：%s"%(url))
        # method = info['method']
        returnstr = info['return']
        h = http_request(method=method, url=url,params=params,data=data,headers=headers,auth=auth)

        #请求执行
        if h[0] == 200:
            # http返回正确
            print h[2].json()
            if h[2].status_code == 200:
                # 结果验证
                json = h[2].json()  # 返回的json数据
                #print('接口返回的数据:%s'%(json))
                return iteration(returnstr,json)
            else:
                return False
        else:
            print(h)
            return False


if __name__ == '__main__':
    f = open('/Users/chenrui/http1019/alarm_ok_yaml.yaml', 'r')
    info = yaml.load(f.read())
    end_time=int(time.time())
    start_time=end_time-5*60
    params = {"start_time":start_time,"end_time":end_time}
    for j in range(len(info)):
        info1 = info[j]

        method=info1['method']
        if method=='get':
            url = info1['url']
            if isinstance(url,list):
                for i in range(len(url)):
                    url1=url[i]+'?start_time='+str(start_time)+'&end_time='+str(end_time)
                    print analyzeInfo(info1,url1,method,None,None,None,None)
                    print ("==============================================")
            else:
                print analyzeInfo(info1,url,method,None,None,None,None)
                print ("==============================================")


        elif method=='post':
            url=info1['url']
            data=info1['data']
            headers=info1['headers']
            if isinstance(data,list):
                for i in range(len(data)):
                    print analyzeInfo(info1,url,method,None,data[i],headers,None)
                    print ("==============================================")
            else:
                print analyzeInfo(info1, url, method,None,data, headers, None)
                print ("==============================================")

        print ("-----------------------------------------")
        print ("-----------------------------------------")

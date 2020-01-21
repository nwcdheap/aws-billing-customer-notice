import json
import os
import boto3
import operator
import time
from datetime import datetime, timedelta, timezone
clientBjs = boto3.client('cloudwatch',region_name='cn-north-1')             # 创建cloudwatch，可以指定region_name
clientZhy = boto3.client('cloudwatch',region_name='cn-northwest-1')         # 创建cloudwatch，可以指定region_name
sns = boto3.client('sns')

def lambda_handler(event, context):
    endTime = datetime.utcnow().replace(tzinfo=timezone.utc)            # 统计结束时间（当前时间）
    delta = timedelta(days=1)                                           # 时间间隔位1天
    startTime = endTime-delta                                           # 统计开始时间（当前时间前一天）
    
    metricsBjs = clientBjs.list_metrics(                                      # 获取账单分类度量（按服务分类）
        Namespace='AWS/Billing'
    )
    metricsZhy = clientZhy.list_metrics(                                      # 获取账单分类度量（按服务分类）
        Namespace='AWS/Billing'
    )    
    billingsBjs = []                                                       # 创建存放账单信息的列表   
    billingsZhy = []                                                       # 创建存放账单信息的列表   
    
    for i,v in enumerate(metricsBjs['Metrics']):                           # 对度量进行循环，获取不同的度量账单
        res = clientBjs.get_metric_data(
            MetricDataQueries=[
                {
                    'Id': 'm1',
                    'MetricStat': {
                        'Metric': {
                            'Namespace': 'AWS/Billing',
                            'MetricName': 'EstimatedCharges',
                            'Dimensions': v['Dimensions']               # 将每个度量的Dimensions取出作为参数
                        },
                        'Period': 300,
                        'Stat': 'Average',
                        'Unit': 'None'
                    }
                },
            ],
            StartTime=startTime,                                        # 当前时间1天前，获取近一天的账单信息
            EndTime=endTime                                             # 当前时间
        )
        # 将每个度量获取的服务名和账单保存进billings列表
        serviceName = v['Dimensions'][0]['Value']
        servicePrice = res['MetricDataResults'][0]['Values'][0] if res['MetricDataResults'][0]['Values'] else 0.0
        billingsBjs.append({'ServiceName':serviceName,"Price":servicePrice})
        
    for i,v in enumerate(metricsZhy['Metrics']):                           # 对度量进行循环，获取不同的度量账单
        res = clientZhy.get_metric_data(
            MetricDataQueries=[
                {
                    'Id': 'm1',
                    'MetricStat': {
                        'Metric': {
                            'Namespace': 'AWS/Billing',
                            'MetricName': 'EstimatedCharges',
                            'Dimensions': v['Dimensions']               # 将每个度量的Dimensions取出作为参数
                        },
                        'Period': 300,
                        'Stat': 'Average',
                        'Unit': 'None'
                    }
                },
            ],
            StartTime=startTime,                                        # 当前时间1天前，获取近一天的账单信息
            EndTime=endTime                                             # 当前时间
        )
        # 将每个度量获取的服务名和账单保存进billings列表
        serviceName = v['Dimensions'][0]['Value']
        servicePrice = res['MetricDataResults'][0]['Values'][0] if res['MetricDataResults'][0]['Values'] else 0.0
        billingsZhy.append({'ServiceName':serviceName,"Price":servicePrice})    
        # print(res["MetricDataResults"][0]["Timestamps"])
        if res["MetricDataResults"][0]["Timestamps"]:
            billTime = res["MetricDataResults"][0]["Timestamps"][0]             # 最近账单时间（账单每天出两次，1：30和13：30，UTC时间）
    
    cnBillTime = billTime.astimezone(timezone(timedelta(hours=8)))      # 最近账单的中国时间 +8:00
    formatTime = cnBillTime.strftime("北京时间%Y年%m月%d日%H:%M:%S")     # 对账单时间进行格式化输出
    
    # 替换总账单的名称
    for i,v in enumerate(billingsBjs):
        if v["ServiceName"] == "CNY":
            v["ServiceName"] = "北京总账单(RMB)"                              # 替换列表中主账单的名称为"总账单(RMB)" 
            totalBjs = v["Price"]
            billingsBjs.remove(v)                                           # 把总帐单删除
            billingsBjs.insert(0,v)                                         # 把总帐单放到列表第一位
            break
            
    for i,v in enumerate(billingsZhy):
        if v["ServiceName"] == "CNY":
            v["ServiceName"] = "宁夏总账单(RMB)"                              # 替换列表中主账单的名称为"总账单(RMB)" 
            totalZhy = v["Price"]
            billingsZhy.remove(v)                                           # 把总帐单删除
            billingsZhy.insert(0,v)                                         # 把总帐单放到列表第一位
            break
    
    # 对账单列表内容进行排序，按照分类服务的价格进行倒叙
    billingsZhy = sorted(billingsZhy,key=operator.itemgetter('Price'),reverse=True)
    billingsBjs = sorted(billingsBjs,key=operator.itemgetter('Price'),reverse=True)
    
    # 计算两个区域的账单总价
    total = totalBjs + totalZhy
    
    # 将宁夏的账单列表转化为字符串
    zhyBillingStr = ''
    for i in billingsZhy:
        zhyBillingStr = zhyBillingStr + i["ServiceName"] + " : "+ str(i["Price"]) + "\n" + "    "
        
    # 将北京的账单列表转化为字符串
    bjsBillingStr = ''
    for i in billingsBjs:
        bjsBillingStr = bjsBillingStr + i["ServiceName"] + " : "+ str(i["Price"]) + "\n" + "    "    
    
    accountDesc = os.environ['CustomSubject']
    accountId   = os.environ['AccountID']
    
    # 生成发送邮件的字符串
    billing = """
    账单生成时间为:%s
    账单总额为:%.2f
    账单描述:%s
    账单ID:%s
    -------------------------------------------------------
    北京区域服务明细账单
    %s
    -------------------------------------------------------   
    宁夏区域服务明细账单
    %s
    """ % (formatTime,total,accountDesc,accountId,bjsBillingStr,zhyBillingStr)
    
    print(billing)
    
    totalInt = str(int(total))
    
    # 将邮件内容发送到SNS Topic
    sns.publish(
        TopicArn=os.environ['SnsArn'],
        Message=billing,
        Subject='AWS中国区域每日账单:' + totalInt + '--账户描述:' + accountDesc + '--账户ID:' + accountId
    )
    
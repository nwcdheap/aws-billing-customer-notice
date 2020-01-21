### 免责说明
建议部署过程中使用此方案，是否使用请自行考虑评估。
当您对方案需要进一步的沟通和反馈后，可以联系nwcd_labs@nwcdcloud.cn获得更进一步的支持。
欢迎联系参与方案共建和提交方案需求, 也欢迎在github项目issue中留言反馈bugs。

### 点击以下图标，在AWS中国宁夏区域创建账单通知服务
[![RUNOOB 图标](https://nwcdlab.s3.cn-northwest-1.amazonaws.com.cn/cloudformation/cf.png)](https://console.amazonaws.cn/cloudformation/home?region=cn-northwest-1#/stacks/new?stackName=awsChinaRegionBillingNotice&templateURL=https://nwcdlab.s3.cn-northwest-1.amazonaws.com.cn/cloudformation/lambdaBilling/chinaBillingNotice.yaml)

### 文档说明
1. AWS中国区域的北京区域的Cloudwatch控制台可以设置账单的告警，但是功能比较局限
2. 本项目通过在宁夏区域部署Lambda抓取Billing的Metrics，通过Cloudwatch的Rule进行每天定时触发，将收集到的信息发布到SNS的Topic
3. 设置邮件地址订阅SNS Topic，每天定时收到账单邮件
4. 邮件内容包含AWS中国区域总账单以及北京/宁夏区域的详细账单（按服务的金额进行倒序排列）
5. 本项目Cloudformation模板只支持一个邮件进行订阅，如果需要多个邮件进行订阅，请部署后到Amazon SNS服务中主动进行多个邮件的订阅
6. 项目发布后请到输入的邮箱中确认订阅（否则收不到SNS的推送信息）
7. 如果需要更新邮件地址和通知时间，可以更新Cloudformation Stack

### 模板简介
打开模板后，会在宁夏区域创建CLoudformation Stack
![](https://nwcdlab.s3.cn-northwest-1.amazonaws.com.cn/cloudformation/lambdaBilling/billingCfA.jpg)

* 在EmailAddress中输入要接收账单详情的邮箱地址
* 在EmailCustomSubject中输入自定义字符串，2-20的长度，会显示在邮件接收标题中，默认为Custom Content
* 在ScheduleTime中选择每天发送邮件的时间，支持24小时整点时间，默认为10AM
![](https://nwcdlab.s3.cn-northwest-1.amazonaws.com.cn/cloudformation/lambdaBilling/billingCfB.jpg)

### 其他事项
1. 如果需要自定义请下载模板进行修改
2. 如果需要发布在北京区域，请修改Launch Stack图标的链接地址中的https://console.amazonaws.cn/cloudformation/home?region=cn-northwest-1 的cn-northwest-1修改为cn-north-1
3. 如果需要发布在AWS全球区域，请自行测试。AWS全球区域的Billing Alarm位于us-east-1

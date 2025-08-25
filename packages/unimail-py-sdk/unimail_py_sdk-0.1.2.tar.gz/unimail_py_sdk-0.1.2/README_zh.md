# unimal-py-sdk

unimail 的 python 语言 sdk, 快速集成到你的项目

[github](https://github.com/i-curve/unimail-py-sdk) [英文文档](README.md)

<!-- @import "[TOC]" {cmd="toc" depthFrom=1 depthTo=6 orderedList=false} -->

<!-- code_chunk_output -->

- [unimal-py-sdk](#unimal-py-sdk)
  - [简单使用](#简单使用)
  - [api docs](#api-docs)
  - [支持的语言](#支持的语言)

<!-- /code_chunk_output -->

## 简单使用

- pip 安装包

```shell
pip install unimail-py-sdk
```

- 初始化客户端

你需要申请一个 key

main.py

```python
from unimail-py-sdk import Client, Result

# please input your key here
key: str = ""

client: Client = Client(key)

client.check_connect()
```

- 发邮件

例如
收件人: aaa@gmail.com  
邮件标题: email subject  
邮件正文: this is a email content

```python
    result: Result := client.send_email("aaa@gmail.com", "email subject", "this is a email content")

    if result.is_success:
        print("send email success")
    else:
        print(f"send email fail, error: {result.msg}")
```

- 批量发送邮件

例如
收件人: aaa@gmail.com,bbb@gmail.com  
邮件标题: email subject  
邮件正文: this is a email content

```python
    result: Result := client.batch_send_email("aaa@gmail.com", "email subject", "this is a email content")

    if result.is_success:
        print("send email success")
    else:
        print(f"send email fail, error: {result.msg}")
```

## api docs

1. Client(key: str, host: str, data: str, obj: json): Client

init a client by key

2. client.set_language(language :str) -> bool

set language for the client,default is zh

3. client.check_connect() -> bool

check the host and key is ok

4. client.send_email(receiver :str, subject :str, content :str) -> Result

send email to receiver. if you have many receiver, you can concat the receiver by ";" or use BatchSendEmail

5. client.batch_send_email(receivers :list, subject :str, content :str) -> Result

like SendEmail, but receivers is a slice

## 支持的语言

sdk 默认返回的 msg 为中文

- [x] english (en)
- [x] simple chinese (zh)
- [x] vietnamese (vi)
- [x] idonesian (id)
- [x] thai (th)
- [x] gujarati (gu)

如果你需要添加了更多语言，欢迎提 issue

'''py
 ' @Author: i-curve
 ' @Date: 2025-01-04 22:01:42
 ' @Last Modified by: i-curve
 ' @Name:
'''
import requests
import json


class Result:
    def __init__(self, code: int = 0, msg: str = "success", data=None, obj=None):
        self.code = code
        self.msg = msg
        self.data = data
        if obj is not None:
            self.__dict__ = obj

    def is_success(self) -> bool:
        return self.code == 0

    def __str__(self) -> str:
        return self.to_str()

    def to_str(self) -> str:
        return json.dumps(self.__dict__, ensure_ascii=False)

    @classmethod
    def HttpError(cls):
        return Result(500, "http error")


class Client:

    __supportLang = ["zh", "en", "vi", "th", "id", "gu"]

    def __init__(self, key: str, host: str = "https://unimail-back.allcloud.top"):
        self.__host = host
        self.__key = key
        self.__lang = "zh"

    def set_language(self, lang: str) -> bool:
        """
        设置语言
        :param lang: 语言 ["zh", "en", "vi", "th", "id", "gu"]
        :return: 是否设置成功
        """
        if lang not in Client.__supportLang:
            return False
        self.__lang = lang
        return True

    def check_connect(self) -> bool:
        """
        检查连接是否正常"""
        try:
            result = requests.post(self.__host + "/api/email/checkConnection",
                                   json={"authorization": self.__key},
                                   headers={"Content-Type": "application/json", "Accept-Language": self.__lang}).json()
            return result["code"] == 0
        except Exception as e:
            return False

    def send_email(self, receiver: str, subject: str, content: str) -> Result:
        """
        发送邮件
        :param receiver: 收件人
        :param subject: 主题
        :param content: 内容
        """
        try:
            result = requests.post(self.__host + "/api/email/sendEmail",
                                   json={"authorization": self.__key,
                                         "receiver": receiver,
                                         "title": subject,
                                         "content": content},
                                   headers={"Content-Type": "application/json", "Accept-Language": self.__lang}).json()
            return Result(obj=result)
        except Exception as e:
            return Result.HttpError()

    def batch_send_email(self, receivers: list, subject: str, content: str):
        """
        发送邮件
        :param receivers: 收件人
        :param subject: 主题
        :param content: 内容
        """
        try:
            result = requests.post(self.__host + "/api/email/batchSendEmail",
                                   json={"authorization": self.__key,
                                         "receivers": receivers,
                                         "title": subject,
                                         "content": content},
                                   headers={"Content-Type": "application/json", "Accept-Language": self.__lang}).json()
            return Result(obj=result)
        except Exception as e:
            return Result.HttpError()

    def send_email_async(self, receiver: str, subject: str, content: str) -> Result:
        """todo"""
        return self.send_email(receiver, subject, content)
    def batch_send_email_async(self, receivers: list, subject: str, content: str):
        """todo"""
        return self.batch_send_email(receivers, subject, content)
    def check_result(self, key: str):
        """todo"""
        return Result.HttpError()
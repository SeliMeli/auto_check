class Error(Exception):
    pass


class LoginException(Error):
    def __init__(self, user, password, response, message='login failed'):
        super().__init__(message, user, password, response)
        self.user = user
        self.password = password
        self.response = response


class CheckException(Error):
    def __init__(self, user, response, message=u'打卡失败'):
        super().__init__(message, user, response)
        self.message = message
        self.response = response


class RetryException(Error):
    def __init__(self, message='retried 2 times, checked failed'):
        super().__init__(message)
        self.message = message

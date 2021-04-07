class JwcException(Exception):
    def __init__(self, msg: str):
        self.msg = msg

    pass


class LoginException(JwcException):
    def __init__(self, status=-100, msg=None):
        self.status = status
        self.msg = msg

    def __str__(self):
        return f'Vatu登录错误: code {self.status}, Msg: {self.msg}'


class CourseQueryException(JwcException):
    def __init__(self, msg: str):
        self.msg = msg

    def __str__(self):
        return f'课程查询错误: {self.msg}'

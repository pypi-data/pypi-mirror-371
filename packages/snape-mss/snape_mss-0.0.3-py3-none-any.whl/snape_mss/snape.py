import json

class SnapeRequest:
    def __init__(self, method: str, path: str, headers: dict, body: dict):
        self.method = method
        self.path = path
        self.headers = headers
        self.body = body

    def to_dict(self):
        return {
            "method": self.method,
            "path": self.path,
            "headers": self.headers,
            "body": self.body
        }

    def to_json(self):
        return json.dumps(self.to_dict())

class SnapeResponse:
    def __init__(self, status_code: int = 200, body: dict = None, headers: dict = None):
        self.status_code = status_code
        self.body = body if body is not None else {}
        self.headers = headers if headers is not None else {
            "Content-Type": "application/json"
        }

    def to_dict(self):
        return {
            "statusCode": self.status_code,
            "body": self.body,
            "headers": self.headers
        }

    def to_json(self):
        return json.dumps(self.to_dict())

import random
import string
import uuid
from builtins import str


def get_random_str(size: int = 16):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=size)).lower()


class MockConfig:

    def __init__(self):
        self.scan_uuid = str(uuid.uuid4())
        self.ts = "1991-01-01T00:00:00Z"
        self.output = "/tmp/" + get_random_str() + "output.pb"
        self.target = "/tmp/"

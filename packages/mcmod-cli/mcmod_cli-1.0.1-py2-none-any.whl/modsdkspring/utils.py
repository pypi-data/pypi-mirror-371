# -*- coding: utf-8 -*-
import uuid
import random
import string

def generate_uuid():
    """生成UUID v4"""
    return str(uuid.uuid4())

def generate_random_string(length=8):
    """生成随机字符串"""
    chars = string.ascii_letters + string.digits
    return ''.join(random.choice(chars) for _ in range(length))
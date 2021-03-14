import os
import django
from datetime import datetime

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ops11.settings')
django.setup()


class Comment:
    def __init__(self, email, content, created=None):
        self.email = email
        self.content = content
        self.created = created or datetime.now()


from rest_framework import serializers


class CommentSerializer(serializers.Serializer):
    email = serializers.EmailField()
    content = serializers.CharField(max_length=200)
    # created = serializers.DateTimeField()




# 序列化
# 直接渲染数据
comment = Comment(email='leila@example.com', content='foo bar')
serializer = CommentSerializer(comment)
print(serializer.data)


# 反序列化
# 1. 数据解析
# 2. 校验
# 3. 保存
import io
from rest_framework.parsers import JSONParser
from rest_framework.renderers import JSONRenderer

json_str = serializer.data
json_str['email'] = "51reboot@qq.com"

json_str = JSONRenderer().render(json_str)
stream = io.BytesIO(json_str)
parse_data = JSONParser().parse(stream)  # dict | list
print(f"data: {parse_data}")


s = CommentSerializer(data=parse_data)
if s.is_valid():
    print(s.validated_data)
else:
    print("valid failed.")
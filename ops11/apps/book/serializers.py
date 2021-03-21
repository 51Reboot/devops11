from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.serializers import ModelSerializer

from .models import Book
from .models import Publisher


def multiple_of_ten(value):
    if value % 10 != 0:
        raise serializers.ValidationError('Not a multiple of ten')


class PublisherModelSerializer(ModelSerializer):
    # address = serializers.CharField(read_only=True)
    address = serializers.CharField(validators=[multiple_of_ten, ])
    # address = serializers.ReadOnlyField()

    # 反序列化 校验
    def validate_address(self, value):
        if not value.endswith("zhengzhou"):
            raise ValidationError("必须是以 zhengzhou 结尾")
        return value

    def validate(self, attrs):
        print(f"attrs: {attrs}")
        if attrs.get('address'):
            if '-' not in attrs['address']:
                raise ValidationError("address 必须包含-.")
        return attrs

    class Meta:
        model = Publisher

        # 序列化
        # fields = ["name", "create_time"]
        fields = "__all__"

        # 反序列化
        # read_only_fields = ["address", ]
        extra_kwargs = {
            'address': {
                # 'write_only': True,
                'required': True,
                'min_length': 5,
                'max_length': 10,
                "error_messages": {
                    "required": "address 是必传参数.",
                    "min_length": "长度最小为5.",
                    "max_length": "长度最大为10.",
                },
            }
        }



class BookModelSerializer(ModelSerializer):
    class Meta:
        model = Book
        fields = "__all__"
        # depth = 1
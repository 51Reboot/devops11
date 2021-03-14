from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.hashers import make_password
from faker import Faker
from xpinyin import Pinyin

from apps.user.models import UserProfile


class Command(BaseCommand):
    help = 'Bulk sync user to local db by auto generator user.'

    def add_arguments(self, parser):
        pass
        # parser.add_argument('poll_ids', nargs='+', type=str)
        # parser.add_argument(
        #     '--delete',
        #     action='store_true',
        #     help='Delete poll instead of closing it',
        # )

    def handle(self, *args, **options):
        password = make_password('123456')
        faker = Faker(locale="zh_CN")
        p = Pinyin()
        for _ in range(100):
            pinyin_username = p.get_pinyin(faker.name_male()).replace("-", "")
            data = {
                'name': faker.name_male(),
                'username': pinyin_username,
                'phone': faker.phone_number(),
                'password': password,
                'is_superuser': False,
                'email': "{}@gmail.com".format(pinyin_username),
            }
            try:
                # u = UserProfile.objects.create(**data)
                # u.save()
                u, ok = UserProfile.objects.get_or_create(username=pinyin_username, defaults=data)
                self.stdout.write(self.style.SUCCESS(f'Create user {pinyin_username} {ok}.'))
            except Exception as e:
                raise CommandError('创建失败！', e.args)
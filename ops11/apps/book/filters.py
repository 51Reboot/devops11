import django_filters

from .models import Book


from apps.user.models import UserProfile



class BookFilter(django_filters.FilterSet):

    class Meta:
        model = Book
        # 针对字段指定匹配条件
        # ?name=&price__lt=&price__gt=70&create_time__year__gt=
        fields = {
            'price': ['lte', 'gt'],
        }


class CustomBookFilter(django_filters.FilterSet):

    author_username = django_filters.CharFilter(method='my_custom_filter')

    def my_custom_filter(self, qs, name, value):
        print(qs)
        print(name)
        print(value)

        try:
            u = UserProfile.objects.get(username=value)
        except UserProfile.DoesNotExist:
            return qs.none()
        return u.book_set.all()

    class Meta:
        model = Book
        fields = ['author_username']


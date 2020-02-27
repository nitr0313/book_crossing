from rest_framework.serializers import ModelSerializer

from bookcross.models import BookInstance


class BookInstanceSerializer(ModelSerializer):
    class Meta:
        model = BookInstance
        fields = '__all__'
        # TODO Не отправляется не верная ссылка на обложку
        # TODO Убрать лишние поля (раз мы берем только доступные книги, поля нужны соответсвующие!!!

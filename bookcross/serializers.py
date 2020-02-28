from rest_framework.serializers import ModelSerializer, StringRelatedField

# from rest_framework import serializers
from bookcross.models import BookInstance


class BookInstanceSerializer(ModelSerializer):
    genre = StringRelatedField(many=True)
    owner = StringRelatedField()
    author = StringRelatedField()

    class Meta:
        model = BookInstance
        # fields = '__all__'
        fields = ['id','title', 'author', 'summary', 'isbn', 'genre', 'owner', 'get_rating', 'get_cover_url']
        # TODO Не отправляется не верная ссылка на обложку

        # TODO Убрать лишние поля (раз мы берем только доступные книги, поля нужны соответсвующие!!!

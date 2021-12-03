from functools import update_wrapper

from django.utils.decorators import _multi_decorate
from drf_yasg import openapi

request_body = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    required=['tags', 'image', 'name', 'text', 'cooking_time'],
    title='Recipe',
    properties={
        'ingridients': openapi.Schema(
            type=openapi.TYPE_ARRAY,
            items=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'id': openapi.Schema(type=openapi.TYPE_STRING,
                                         title='id ингредиента'),
                    'amount': openapi.Schema(type=openapi.TYPE_INTEGER,
                                             title='количество ингредиента',
                                             maxLength='2147483647',
                                             minLength='0',
                                             nullable='true')
                },
                required=['id', ]
            ),
            title='Ingridient'
        ),
        'tags': openapi.Schema(
            type=openapi.TYPE_ARRAY,
            items=openapi.Schema(type=openapi.TYPE_INTEGER, title='id тэга'),
            title='Tags'
        ),
        'image': openapi.Schema(type=openapi.TYPE_STRING,
                                title='изображение в base64'),
        'name': openapi.Schema(type=openapi.TYPE_STRING,
                               title='Название рецепта'),
        "text": openapi.Schema(type=openapi.TYPE_STRING,
                               title='Описание рецепта'),
        "cooking_time": openapi.Schema(type=openapi.TYPE_INTEGER,
                                       minLength='1',
                                       title='Время приготовления'),
    },
)


def multi_method_decorator(decorator, names):

    def _dec(obj):
        for name in names:
            method = getattr(obj, name)
            _wrapper = _multi_decorate(decorator, method)
            setattr(obj, name, _wrapper)
        return obj

    if not hasattr(decorator, '__iter__'):
        update_wrapper(_dec, decorator)
    obj = decorator if hasattr(decorator, '__name__') else decorator.__class__
    _dec.__name__ = 'method_decorator(%s)' % obj.__name__
    return _dec

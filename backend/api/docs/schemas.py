from drf_yasg import openapi
from drf_yasg.inspectors import SwaggerAutoSchema

recipe_request_body = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    required=['tags', 'image', 'name', 'text', 'cooking_time'],
    title='Recipe',
    properties={
        'ingredients': openapi.Schema(
            type=openapi.TYPE_ARRAY,
            items=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'id': openapi.Schema(type=openapi.TYPE_INTEGER,
                                         title='id ингредиента'),
                    'amount': openapi.Schema(type=openapi.TYPE_INTEGER,
                                             title='Количество ингредиента',
                                             maxLength='2147483647',
                                             minLength='0',
                                             nullable='true')
                },
                required=['id', ]
            ),
            title='Ingredient'
        ),
        'tags': openapi.Schema(
            type=openapi.TYPE_ARRAY,
            items=openapi.Schema(type=openapi.TYPE_INTEGER, title='id тэга'),
            title='Tags'
        ),
        'image': openapi.Schema(type=openapi.TYPE_STRING,
                                title='Изображение в base64'),
        'name': openapi.Schema(type=openapi.TYPE_STRING,
                               title='Название рецепта'),
        'text': openapi.Schema(type=openapi.TYPE_STRING,
                               title='Описание рецепта'),
        'cooking_time': openapi.Schema(type=openapi.TYPE_INTEGER,
                                       minLength='1',
                                       title='Время приготовления'),
    },
)

follower_params = [
    openapi.Parameter('id', openapi.IN_PATH,
                      description='following id', type=openapi.TYPE_INTEGER),
    openapi.Parameter('recipes_limit', openapi.IN_QUERY,
                      description='recipes limit', type=openapi.TYPE_INTEGER)
]


class EmptyAutoSchema(SwaggerAutoSchema):

    def get_query_parameters(self):
        return []

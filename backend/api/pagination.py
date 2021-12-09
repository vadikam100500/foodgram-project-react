from django.utils.encoding import force_str
from rest_framework.compat import coreapi, coreschema
from rest_framework.pagination import PageNumberPagination, _positive_int


class LimitPagination(PageNumberPagination):
    page_size_query_param = 'limit'


class FollowPagination(LimitPagination):
    recipe_limit = None
    recipe_limit_param = 'recipes_limit'

    def get_recipe_limit(self, request):
        try:
            self.recipe_limit = _positive_int(
                request.query_params[self.recipe_limit_param],
                strict=True,
            )
        except (KeyError, ValueError):
            pass

    def get_page_size(self, request):
        self.get_recipe_limit(request)
        return super().get_page_size(request)

    def get_schema_fields(self, view):
        fields = super().get_schema_fields(view)
        fields.append(
            coreapi.Field(
                name=self.recipe_limit_param,
                required=False,
                location='query',
                schema=coreschema.Integer(
                    title='Recipe size',
                    description=force_str('limit of recipes '
                                          'per one following')
                )
            )
        )
        return fields

    def get_schema_operation_parameters(self, view):
        parameters = super().get_schema_operation_parameters(view)
        parameters.append(
            {
                'name': self.recipe_limit_param,
                'required': False,
                'in': 'query',
                'description': force_str('limit of recipes '
                                         'per one following'),
                'schema': {'type': 'integer'},
            },
        )
        return parameters

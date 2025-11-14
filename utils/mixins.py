from rest_framework.response import Response


class GetWithOrmMixin:
    """ Para obtener uno o varios objetos (list o retrieve) con el ORM de Django.
        Requiere que el ModelViewSet tenga los atributos `serializer_class` y `orm_fields`.  """

    def list(self, request, *args, **kwargs):
        try:
            objs = self.queryset.values(*self.orm_fields)
            return Response(objs, status=200)
        except Exception as e:
            return Response(data={'error': str(e)}, status=500)

    def retrieve(self, request, *args, **kwargs):
        try:
            obj = self.get_object()
            queryset = self.queryset.filter(pk=obj.pk)
            obj_values = queryset.values(*self.orm_fields).first()
            return Response(obj_values)
        except Exception as e:
            return Response(data={'error': str(e)}, status=500)

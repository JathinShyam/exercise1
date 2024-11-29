from rest_framework.pagination import CursorPagination

class ModelPagination(CursorPagination):
    page_size = 5
    # page_size_query_param = 'page_size'
    ordering = '-name'

    def paginate_queryset(self, queryset, request, view=None):
        
        print(self.get_page_size(request))
        return super().paginate_queryset(queryset, request, view)
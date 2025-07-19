from rest_framework.pagination import PageNumberPagination

class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'  # امکان تغییر تعداد از طریق URL
    max_page_size = 100
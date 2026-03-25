from rest_framework.pagination import PageNumberPagination

class CustomPageNumberPagination(PageNumberPagination):
    """
    Custom pagination class that allows clients to specify page size.
    
    Query Parameters:
    - page: Page number (default: 1)
    - page_size: Number of items per page (default: 10, max: 100)
    
    Examples:
    - /api/rides/?page=1&page_size=20
    - /api/rides/?page=2&page_size=50
    """
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

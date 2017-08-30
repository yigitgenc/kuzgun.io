from rest_framework.authentication import TokenAuthentication


class QueryStringTokenAuthentication(TokenAuthentication):
    """
    Query string based token authentication.
    This authentication class allows user able to
    reach API without username and password.
    """
    def authenticate(self, request):
        key = request.query_params.get('token', '').strip()

        if key:
            return self.authenticate_credentials(key)
        return super(QueryStringTokenAuthentication, self).authenticate(request)

from rest_framework.authentication import TokenAuthentication


class QueryStringTokenAuthentication(TokenAuthentication):
    def authenticate(self, request):
        key = request.query_params.get('token', '').strip()

        if key:
            return self.authenticate_credentials(key)
        return super(QueryStringTokenAuthentication, self).authenticate(request)

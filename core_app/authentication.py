from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from rest_framework import HTTP_HEADER_ENCODING

class BearerTokenAuthentication(BaseAuthentication):
    def authenticate(self, request):
        auth = request.headers.get('Authorization', None)
        if not auth:
            return None

        # Xử lý Bearer token
        try:
            prefix, token = auth.split(' ')
            if prefix.lower() != 'bearer':
                raise AuthenticationFailed('Invalid token prefix')
        except ValueError:
            raise AuthenticationFailed('Invalid token header format')

        # Xác thực token
        user = self.authenticate_token(token)
        if user is None:
            raise AuthenticationFailed('Invalid token')

        return (user, token)

    def authenticate_token(self, token):
        # Thay đổi logic xác thực token của bạn ở đây
        # Ví dụ đơn giản: kiểm tra token cụ thể
        if token == 'VALID_TOKEN':
            from django.contrib.auth.models import User
            return User.objects.get(username='admin')  # Thay đổi theo logic của bạn
        return None

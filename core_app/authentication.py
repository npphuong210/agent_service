from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from rest_framework import HTTP_HEADER_ENCODING
from rest_framework.authtoken.models import Token
from django.core.exceptions import ObjectDoesNotExist

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

def get_user_instance_by_token(request):
    try:
        # Lấy token từ header của yêu cầu
        token_key = request.META.get('HTTP_AUTHORIZATION').split()[1]
        # Truy vấn token trong cơ sở dữ liệu
        token = Token.objects.get(key=token_key)
        # Trả về user tương ứng với token
        return token.user
    except (IndexError, ObjectDoesNotExist, AttributeError):
        return None
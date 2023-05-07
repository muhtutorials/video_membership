from starlette.authentication import AuthCredentials, AuthenticationBackend, SimpleUser, UnauthenticatedUser

from app.auth.utils import get_current_user


class JWTCookieBackend(AuthenticationBackend):
    async def authenticate(self, request):
        user = get_current_user(request)
        if user is None:
            roles = ['anon']
            return AuthCredentials(roles), UnauthenticatedUser()
        roles = ['authenticated']
        return AuthCredentials(roles), SimpleUser(user['id'])

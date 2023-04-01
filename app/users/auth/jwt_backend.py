from starlette.authentication import (
    AuthenticationBackend,
    SimpleUser,
    UnauthenticatedUser,
    AuthCredentials
)

from app.users.auth import backends as auth_backend

class JwtAuthenticationBackend(AuthenticationBackend):
    
    async def authenticate(self, request):
        token = request.cookies.get('token')
        user = None
        if token:
            user = auth_backend.verify_user_by(token)
        
        if not user:
            scopes = ['anon']
            return AuthCredentials(scopes), UnauthenticatedUser()
        
        scopes = ['admin'] # we should extract users_roles from user model
        
        return AuthCredentials(scopes), SimpleUser(user['user_id'])



from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from app.views import RegisterView, LoginView, CustomUserListCreateView, CustomUserRetrieveUpdateDestroyView, LogoutView
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/schema/', SpectacularAPIView.as_view(), name='api-schema'),
    path(
        'api/docs/',
        SpectacularSwaggerView.as_view(url_name='api-schema'),
        name='api-docs',
    ),
    path('silk/', include('silk.urls', namespace='silk')),

    path('users/', CustomUserListCreateView.as_view(), name='user-list-create'),
    path('users/<int:pk>/', CustomUserRetrieveUpdateDestroyView.as_view(), name='user-detail'),
    path('api/register/', RegisterView.as_view(), name='register'),
    path('api/login/', LoginView.as_view(), name='login'),
    # path('api/logout/', LogoutView.as_view(), name='logout'),
    # path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),   

    path('app/', include('app.urls')),
    
]
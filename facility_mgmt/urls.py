from django.contrib import admin
from django.urls import path, include
from core.views import CustomLoginView

urlpatterns = [
    path('admin/', admin.site.urls),
    # override the default login view so admin users go straight to /admin/
    path('accounts/login/', CustomLoginView.as_view(), name='login'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('', include('core.urls')),
]

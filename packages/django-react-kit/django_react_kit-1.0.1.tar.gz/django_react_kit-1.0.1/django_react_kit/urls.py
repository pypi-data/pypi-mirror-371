from django.urls import re_path
from .views import ReactView

app_name = 'django_react_kit'

urlpatterns = [
    # Catch-all pattern for React routing
    # This will match any URL and let React handle the routing
    re_path(r'^(?P<path>.*)$', ReactView.as_view(), name='react_view'),
]
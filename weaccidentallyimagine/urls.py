"""URL Configuration"""

from django.conf.urls import url
from django.http import HttpResponse

from main import views

urlpatterns = [
    url(r'(?P<seed>[0-9]+)$', views.main_view, name=''),
    url(r'^$', views.main_view, name=''),
    # robots.txt --- Tell webcrawlers to ignore fixed seed links
    url(r'^robots.txt$', lambda r: HttpResponse(
            "User-agent: *\n"
            "Allow: /$\n"
            "Disallow: /",
            content_type="text/plain")),
]

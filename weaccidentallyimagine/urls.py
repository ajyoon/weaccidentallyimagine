"""URL Routing"""

from django.conf.urls import url
from django.http import HttpResponse

from main import views

urlpatterns = [
    # Root goes to main view, generating a random version
    url(r'^$', views.main_view, name=''),
    # Pass any present numerical random seed to the view for
    # reproducible rendering
    url(r'(?P<seed>[0-9]+)$', views.main_view, name=''),
    # robots.txt --- Tell webcrawlers to ignore fixed seed links
    # (Will crawlers get confused about all this anyway???)
    url(r'^robots.txt$', lambda r: HttpResponse(
            "User-agent: *\n"
            "Allow: /$\n"
            "Disallow: /",
            content_type="text/plain")),
]

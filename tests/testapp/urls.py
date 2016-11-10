from django.conf.urls import url
from resticus.views import SessionAuthEndpoint, TokenAuthEndpoint

from .views import *

urlpatterns = [
    url(r'^auth/$', SessionAuthEndpoint.as_view(),
        name='session_auth'),
    url(r'^auth/basic/$', BasicAuthEndpoint.as_view(),
        name='basic_auth'),
    url(r'^auth/token/$', TokenAuthEndpoint.as_view(),
        name='token_auth'),

    url(r'^authors/$', AuthorList.as_view(),
        name='author_list'),
    url(r'^authors/(?P<author_id>\d+)$', AuthorDetail.as_view(),
        name='author_detail'),

    url(r'^publishers/$', PublisherList.as_view(),
        name='publisher_list'),
    url(r'^publishers-ready-only/$', ReadOnlyPublisherList.as_view(),
        name='readonly_publisher_list'),
    url(r'^publishers/(?P<pk>\d+)$', PublisherDetail.as_view(),
        name='publisher_detail'),

    url(r'^books/(?P<isbn>\d+)$', BookDetail.as_view(),
        name='book_detail'),

    url(r'^fail-view/$', FailsIntentionally.as_view(),
        name='fail_view'),
    url(r'^echo-view/$', EchoView.as_view(),
        name='echo_view'),
    url(r'^error-raising-view/$', ErrorRaisingView.as_view(),
        name='error_raising_view'),
    url(r'^.*$', WildcardHandler.as_view()),
]

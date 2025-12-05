from allianceauth import urls
from django.urls import include, path
from django.conf import settings

urlpatterns = [
    path(f'ht/{settings.HEALTH_TOKEN}/', include('health_check.urls')),
    path('', include(urls)),
]

handler500 = 'allianceauth.views.Generic500Redirect'
handler404 = 'allianceauth.views.Generic404Redirect'
handler403 = 'allianceauth.views.Generic403Redirect'
handler400 = 'allianceauth.views.Generic400Redirect'

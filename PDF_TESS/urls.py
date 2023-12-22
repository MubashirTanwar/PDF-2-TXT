from django.urls import path
from . import views
from django.conf import settings

urlpatterns = [
    path('upload_pdf/', views.upload_pdf, name='upload_pdf'),
    path('pdf_list/', views.pdf_list, name='pdf_list'),
]

if settings.DEBUG:
    from django.conf.urls.static import static
    from django.contrib.staticfiles.urls import staticfiles_urlpatterns
    urlpatterns += staticfiles_urlpatterns()
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

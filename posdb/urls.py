from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView
# បន្ថែម import ពីរនេះ
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', RedirectView.as_view(url='/accounts/login/'), name='home'),
    path('admin/', admin.site.urls),
    path('sales/', include('sales.urls')),
    path('accounts/', include('django.contrib.auth.urls')),
]

# បន្ថែមបន្ទាត់នេះនៅខាងក្រោមគេបង្អស់ ដើម្បីឱ្យ Django ស្គាល់ផ្លូវទៅរក Files រូបភាព
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
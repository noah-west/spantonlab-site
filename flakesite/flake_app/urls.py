from django.urls import path

from . import views

app_name = "flake_app"

urlpatterns = [
    path('', views.FlakeIndex.as_view(), name='flake-index'),
    path('flake/<int:pk>', views.FlakeDetail.as_view(), name = 'flake-detail'),
    path('flake/<int:pk>/edit', views.FlakeEdit.as_view(), name = 'flake-edit'),
    path('flake/api/upload', views.FlakeUpload.as_view(), name = 'flake-upload'),
    path('flake/api/update/<int:pk>', views.FlakeUpdateRetrieve.as_view(), name = 'flake-update'),
    path('flake/<int:pk>/map', views.flake_map_image, name = 'map-image'),
    path('flake/<int:pk>/flake', views.flake_image, name = 'flake-image'),
    path('flake/<int:pk>/gamma_flake', views.gamma_flake_image, name = 'flake-gamma'),
    path('device', views.DeviceIndex.as_view(), name = 'device-index'),
    path('device/<int:pk>', views.DeviceDetail.as_view(), name = 'device-detail'),
    path('device/<int:pk>/download', views.device_powerpoint, name = 'device-download'),
    path('device/create', views.DeviceCreate.as_view(), name = 'device-create'),
]
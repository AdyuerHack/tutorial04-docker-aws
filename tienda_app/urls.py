from django.urls import path
from .api.views import CompraAPIView, LibroListAPIView
from .views import CompraView, compra_rapida_fbv, catalogo_inventario_view

urlpatterns = [
    # Rutas Monolito HTML
    path('', catalogo_inventario_view, name='catalogo_raiz'),
    path('inventario/', catalogo_inventario_view, name='inventario_html'),
    path('compra/<int:libro_id>/', CompraView.as_view(), name='finalizar_compra'),
    path('compra-rapida/<int:libro_id>/', compra_rapida_fbv, name='compra_rapida_fbv'),

    # Rutas API REST Headless (DRF)
    path('api/v1/comprar/', CompraAPIView.as_view(), name='api_comprar'),
    path('api/v1/libros/', LibroListAPIView.as_view(), name='api_libros'),
]
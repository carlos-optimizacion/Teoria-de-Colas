from django.urls import path
from . import views

app_name = "portal"

urlpatterns = [
    path("", views.home, name="home"),
    path("fundamentos/", views.fundamentals, name="fundamentals"),
    path("modelos/mm1/", views.model_mm1, name="mm1"),
    path("modelos/mms/", views.model_mms, name="mms"),
    path("modelos/mmsk/", views.model_mmsk, name="mmsk"),
    path("modelos/mm1-espera-limitada/", views.model_mm1c, name="mm1c"),
    path("modelos/mms-capacidad-total/", views.model_mmstotal, name="mmstotal"),
    path("modelos/erlang-b/", views.model_erlangb, name="erlangb"),
    path("modelos/mg1/", views.model_mg1, name="mg1"),
    path("modelos/dd1/", views.model_dd1, name="dd1"),
    path("aplicar/casos/", views.cases, name="cases"),
    path("aplicar/colas-simples/", views.simple_lab, name="simple"),
    path("aplicar/colas-complejas/", views.complex_lab, name="complex"),
    path("aplicar/comparador/", views.comparator, name="comparator"),
    path("aplicar/economia/", views.economics, name="economics"),
    path("aplicar/dimensionamiento/", views.sizing, name="sizing"),
    path("analizar/validador/", views.validator, name="validator"),
    path("analizar/end-to-end/", views.end_to_end, name="endtoend"),
    path("simular/colas/", views.simulator, name="simulator"),
    path("api/model/", views.model_api, name="model_api"),
    path("api/queue/", views.queue_api, name="queue_api"),
    path("api/compare/", views.compare_api, name="compare_api"),
    path("api/economic/", views.economic_api, name="economic_api"),
    path("api/sizing/", views.sizing_api, name="sizing_api"),
    path("api/validator/", views.validator_api, name="validator_api"),
    path("api/end-to-end/", views.end_to_end_api, name="end_to_end_api"),
    path("api/simulator/", views.simulator_api, name="simulator_api"),
]

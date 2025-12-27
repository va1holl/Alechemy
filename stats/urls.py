from django.urls import path
from . import views

app_name = "stats"

urlpatterns = [
    path("dashboard/", views.dashboard, name="dashboard"),
    path("export-pdf/", views.export_pdf_report, name="export_pdf"),
]

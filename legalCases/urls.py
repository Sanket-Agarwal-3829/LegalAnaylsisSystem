from django.urls import path

from . import views

app_name = 'legal'

urlpatterns = [
    path("", views.index, name="index"),
    path("new-judgement",views.make_summary,name='make_summary'),
    path('download/<str:document_id>', views.download, name='download'),
    path('summary', views.summarySearch, name='summary-Search'),
    path(r'view-pdf/<str:document>', views.pdf_view, name='pdf_view'),   
    path('create-folder', views.CreateFolder, name='create-folder'),
    path('history', views.getHistory, name='history'),
    path(r'pdfs/<str:title>', views.get_pdfs, name='get-pdfs'),   
    path('download_zip',views.download_zip,name="download-zip"),
]
from django.urls import path
from .views import (
    AreaListCreateView, AreaDetailView,
    PostcodeListCreateView, PostcodeDetailView, TimeSlotBulkCreateView, TimeSlotDetailView, TimeSlotListCreateView
)

urlpatterns = [
    # Area URLs
    path('areas/', AreaListCreateView.as_view(), name='area-list-create'),
    path('areas/<int:pk>/', AreaDetailView.as_view(), name='area-detail'),
    
    # Postcode URLs
    path('postcodes/', PostcodeListCreateView.as_view(), name='postcode-list-create'),
    path('postcodes/<int:pk>/', PostcodeDetailView.as_view(), name='postcode-detail'),

    # Time Slot URLs
    path('time-slots/', TimeSlotListCreateView.as_view(), name='timeslot-list-create'),
    path('time-slots/bulk-create/', TimeSlotBulkCreateView.as_view(), name='timeslot-bulk-create'),
    path('time-slots/<int:pk>/', TimeSlotDetailView.as_view(), name='timeslot-detail'),
]
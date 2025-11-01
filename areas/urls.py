from django.urls import path
from .views import (
    AreaListCreateView, AreaDetailView, AreaTimeSlotListView, DayTimeSlotsBulkToggleView,
    PostcodeListCreateView, PostcodeDetailView, TimeSlotToggleView
)

urlpatterns = [
    # Area URLs
    path('areas/', AreaListCreateView.as_view(), name='area-list-create'),
    path('areas/<int:pk>/', AreaDetailView.as_view(), name='area-detail'),
    # Time Slot URLs
    path('areas/<int:area_pk>/time-slots/', AreaTimeSlotListView.as_view(), name='area-timeslots-list'),
    path('areas/<int:area_pk>/time-slots/<int:slot_pk>/toggle/', TimeSlotToggleView.as_view(), name='timeslot-toggle'),
    path('areas/<int:area_pk>/time-slots/day/<int:day>/toggle/', DayTimeSlotsBulkToggleView.as_view(), name='day-timeslots-bulk-toggle'),
    # Postcode URLs
    path('postcodes/', PostcodeListCreateView.as_view(), name='postcode-list-create'),
    path('postcodes/<int:pk>/', PostcodeDetailView.as_view(), name='postcode-detail'), 
]
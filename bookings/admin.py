from django.contrib import admin
from .models import Subject, Booking

@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'created_at')
    search_fields = ('name', 'code')

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('id', 'student', 'tutor', 'subject', 'start_time', 'status')
    list_filter = ('status', 'subject', 'start_time')
    search_fields = ('student__email', 'tutor__email', 'topic')
    readonly_fields = ('created_at', 'updated_at')
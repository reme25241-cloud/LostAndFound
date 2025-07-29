from django.db import models
from django.contrib.auth.models import User
from django.core.mail import send_mail

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    name = models.CharField(max_length=100)
    contact = models.CharField(max_length=15, blank=True)
    email = models.EmailField(null=True, blank=True)
    age = models.PositiveIntegerField(null=True, blank=True)
    gender = models.CharField(max_length=10, choices=[
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other')
    ], blank=True)
    address = models.TextField(blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    qr_code_image = models.ImageField(upload_to='qr_codes/', blank=True, null=True)  

    def __str__(self):
        return self.name

from django.conf import settings

class Message(models.Model):
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sent_messages')
    receiver = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='received_messages', null=True, blank=True)
    text = models.TextField(blank=True)
    image = models.ImageField(upload_to='messages/', blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    is_group_message = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.sender} to {self.receiver or 'Group'}"



# feedback models.py

from django.db import models
from django.conf import settings

class Feedback(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    resolved = models.BooleanField(default=False)

    def __str__(self):
        return f"Feedback from {self.user.name} at {self.created_at.strftime('%Y-%m-%d %H:%M')}"

# models.py mainApplicationFunctionality20240625
from django.contrib.auth import get_user_model
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class LostItem(models.Model):
    """
    Model to track lost and found items reported by users.
    """
    CATEGORY_CHOICES = [
        ('electronics', 'Electronics'),
        ('clothing', 'Clothing'),
        ('stationery', 'Stationery'),
        ('id_card', 'ID Card'),
        ('accessories', 'Accessories'),
        ('others', 'Others'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='lost_items')
    full_name = models.CharField(max_length=100)
    date_lost = models.DateField()
    location_lost = models.CharField(max_length=100)
    item_category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    item_description = models.TextField()
    item_photo = models.ImageField(upload_to='lost_items/', blank=True, null=True)
    contact_info = models.CharField(max_length=50)

    # Status tracking
    is_found = models.BooleanField(default=False)
    found_timestamp = models.DateTimeField(null=True, blank=True)
    found_by = models.ForeignKey(
        User, null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='found_reports'
    )

    reported_at = models.DateTimeField(default=timezone.now)
    is_archived = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.full_name} lost {self.item_category} at {self.location_lost} [{ 'Found' if self.is_found else 'Pending' }]"

    class Meta:
        ordering = ['-reported_at']
        verbose_name = "Lost Item"
        verbose_name_plural = "Lost Items"

    

class FoundReport(models.Model):
    lost_item = models.ForeignKey(LostItem, on_delete=models.CASCADE, related_name='found_reports')
    finder_name = models.CharField(max_length=100)
    contact_number = models.CharField(max_length=15)
    address = models.TextField()
    location_found = models.CharField(max_length=100)
    date_found = models.DateField()
    time_found = models.TimeField()
    found_photo = models.ImageField(upload_to='found_items/', blank=True, null=True)
    reported_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Found report by {self.finder_name} for {self.lost_item.item_category}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.lost_item.user.profile.email:
            send_mail(
                subject='Your lost item might be found!',
                message=(
                    f"Hello {self.lost_item.full_name},\n\n"
                    f"Your lost item ({self.lost_item.item_description}) might have been found by {self.finder_name}.\n"
                    f"Location: {self.location_found}\nDate: {self.date_found}\n"
                    f"Please login to verify details.\n\nRegards,\nLost & Found Team"
                ),
                from_email='noreply@lostfound.com',
                recipient_list=[self.lost_item.user.profile.email],
                fail_silently=True,
            )
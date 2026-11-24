from django.db import models
from django.contrib.auth.models import User


class CarDb(models.Model):
    created_by = models.ForeignKey(User,on_delete=models.CASCADE,related_name="cars")
    car_name = models.CharField(max_length=100)
    brand = models.CharField(max_length=100)
    model = models.CharField(max_length=100)
    registration_number = models.CharField(max_length=20, unique=True)
    fuel_type = models.CharField(max_length=50)
    seating_capacity = models.PositiveIntegerField()
    rent_per_day = models.PositiveIntegerField()
    available = models.BooleanField(default=True)

    def __str__(self):
        return self.car_name


class RentalBookingDb(models.Model):

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('rejected', 'Rejected'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    created_by = models.ForeignKey(User,on_delete=models.CASCADE,related_name="rental_bookings")
    car = models.ForeignKey(CarDb,on_delete=models.PROTECT,related_name="bookings")
    pickup_date = models.DateField()
    return_date = models.DateField()
    pickup_location = models.CharField(max_length=200)
    total_days = models.PositiveIntegerField()
    total_amount = models.PositiveIntegerField()

    status = models.CharField(max_length=20,choices=STATUS_CHOICES,default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.created_by.username} - {self.car.car_name}"
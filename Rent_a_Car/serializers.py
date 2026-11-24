from django.contrib.auth.models import User
from rest_framework import serializers
from Rent_a_Car.models import CarDb, RentalBookingDb
from datetime import date


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ["id", "first_name", "last_name", "username", "email", "password"]

    def create(self, validated_data):
        user = User.objects.create_user(
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )
        return user

class CarSerializer(serializers.ModelSerializer):
    class Meta:
        model = CarDb
        fields = "__all__"
        read_only_fields = ["created_by"]

class RentalBookingSerializer(serializers.ModelSerializer):

    class Meta:
        model = RentalBookingDb
        fields = "__all__"
        read_only_fields = [
            "created_by",
            "total_days",
            "total_amount",
            "status",
            "created_at"
        ]

    def validate(self, data):

        pickup_date = data.get('pickup_date',self.instance.pickup_date if self.instance else None)
        return_date = data.get('return_date',self.instance.return_date if self.instance else None)

        if pickup_date and pickup_date < date.today():
            raise serializers.ValidationError("Pickup date cannot be in the past..!")

        if pickup_date and return_date and return_date <= pickup_date:
            raise serializers.ValidationError("Return date must be after pickup date..!")
        car = data.get('car',self.instance.car_id if self.instance else None)
        if car and not car.available:
            raise serializers.ValidationError("This car is currently unavailable..!")
        return data

    def create(self, validated_data):

        car = validated_data['car']
        total_days = (validated_data['return_date'] -validated_data['pickup_date']).days
        total_amount = total_days * car.rent_per_day
        booking = RentalBookingDb.objects.create(**validated_data,total_days=total_days,total_amount=total_amount)
        return booking
    
    def update(self, instance, validated_data):
        for key, value in validated_data.items():
            setattr(instance, key, value)

        instance.total_days = (instance.return_date - instance.pickup_date).days
        instance.total_amount = (instance.total_days * instance.car.rent_per_day)
        instance.save()
        return instance
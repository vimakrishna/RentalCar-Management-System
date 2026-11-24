from django.shortcuts import render,get_object_or_404
from django.contrib.auth.models import User
from rest_framework.views import APIView
from rest_framework.response import Response
from Rent_a_Car.serializers import UserSerializer,CarSerializer,RentalBookingSerializer
from Rent_a_Car.permissions import IsAdminOrReadOnly,OwnerOnly
from rest_framework import authentication, permissions, serializers
from rest_framework.exceptions import PermissionDenied
from Rent_a_Car.models import CarDb,RentalBookingDb
from django.db.models import Q
from rest_framework.filters import OrderingFilter

# USER REGISTERATION 
class SignUpView(APIView):
    def post(self, request):
        form_data = request.data
        serializer_instance = UserSerializer(data=form_data)
        if serializer_instance.is_valid():
            serializer_instance.save()
            return Response(data={"Message": "User was created successfully..!"},status=201)

        return Response(data={"message": "Invalid data provided...!"},status=400)

class UserListView(APIView):

    authentication_classes = [authentication.BasicAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        if not request.user.is_staff:
            raise PermissionDenied("Only admin can view users..!")
        qs = User.objects.all()
        serializer_instance = UserSerializer(qs, many=True)
        return Response(data=serializer_instance.data, status=200)

# CAR LIST AND CREATE

class CarListCreateView(APIView):

    authentication_classes = [authentication.BasicAuthentication]
    permission_classes = [IsAdminOrReadOnly]

    filter_backends = [OrderingFilter]
    ordering_fields = ['rent_per_day', 'car_name', 'seating_capacity']

    def get(self, request):
        if request.user.is_staff:
            qs = CarDb.objects.all()
        else:
            qs = CarDb.objects.filter(available=True)
        # Search by car name, brand and model
        search = request.query_params.get('search')
        if search:
            qs = qs.filter(
                Q(car_name__icontains=search) |
                Q(brand__icontains=search) |
                Q(model__icontains=search)
            )
        # Filter by fuel type
        fuel_type = request.query_params.get('fuel_type')
        if fuel_type:
            qs = qs.filter(fuel_type__iexact=fuel_type)
        # Filter by maximum rent
        max_rent = request.query_params.get('max_rent')
        if max_rent:
            try:
                qs = qs.filter(rent_per_day__lte=int(max_rent))
            except ValueError:
                return Response(
                    {"Message": "Enter a valid rent amount..!"},
                    status=400
                )
            ordering = request.query_params.get('ordering')

            if ordering:
                qs = qs.order_by(ordering)
        serializer_instance = CarSerializer(qs, many=True)
        return Response(serializer_instance.data, status=200)

    def post(self, request):
        form_data = request.data
        serializer_instance = CarSerializer(data=form_data)
        if serializer_instance.is_valid():
            serializer_instance.save(created_by=request.user)
            return Response(serializer_instance.data,status=201)
        return Response(serializer_instance.errors,status=400)

class CarRetrieveUpdateDeleteView(APIView):

    authentication_classes = [authentication.BasicAuthentication]
    permission_classes = [IsAdminOrReadOnly]

    def get(self, request, pk):

        qs = get_object_or_404(CarDb, pk=pk)
        serializer_instance = CarSerializer(qs)
        return Response(serializer_instance.data)

    def put(self, request, pk):

        qs = get_object_or_404(CarDb, pk=pk)
        form_data = request.data
        serializer_instance = CarSerializer(qs, data=form_data)
        if serializer_instance.is_valid():
            serializer_instance.save()
            return Response(serializer_instance.data)
        return Response(serializer_instance.errors, status=400)


    def delete(self, request, pk):

        qs = get_object_or_404(CarDb, pk=pk)
        qs.delete()
        return Response(
            {"Message": "Car deleted successfully...!"},
            status=200
        )

class RentalBookingListCreateView(APIView):

    authentication_classes = [authentication.BasicAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):

        if request.user.is_staff:
            qs = RentalBookingDb.objects.all()
        else:
            qs = RentalBookingDb.objects.filter(created_by=request.user)
        serializer_instance = RentalBookingSerializer(qs, many=True)
        return Response(serializer_instance.data)

    def post(self, request):

        form_data = request.data
        serializer_instance = RentalBookingSerializer(data=form_data)
        if serializer_instance.is_valid():
            serializer_instance.save(created_by=request.user)
            return Response(serializer_instance.data,status=201)
        return Response(serializer_instance.errors, status=400)

class RentalBookingRetrieveUpdateDeleteView(APIView):

    authentication_classes = [authentication.BasicAuthentication]
    permission_classes = [permissions.IsAuthenticated, OwnerOnly]

    def get(self, request, pk):

        qs = get_object_or_404(RentalBookingDb, pk=pk)
        self.check_object_permissions(request, qs)
        serializer_instance = RentalBookingSerializer(qs)
        return Response(serializer_instance.data)

    def put(self, request, pk):

        qs = get_object_or_404(RentalBookingDb, pk=pk)
        self.check_object_permissions(request, qs)
        if qs.status != 'pending':
            raise PermissionDenied("Only pending bookings can be updated...!")
        form_data = request.data

        serializer_instance = RentalBookingSerializer(qs,data=form_data)
        if serializer_instance.is_valid():
            serializer_instance.save()
            return Response(serializer_instance.data)
        return Response(serializer_instance.errors, status=400)

    def patch(self, request, pk):

        qs = get_object_or_404(RentalBookingDb, pk=pk)
        self.check_object_permissions(request, qs)
        if qs.status != 'pending':
            raise PermissionDenied("Only pending bookings can be updated...!")
        form_data = request.data

        serializer_instance = RentalBookingSerializer(qs,data=form_data,partial=True)
        if serializer_instance.is_valid():
            serializer_instance.save()
            return Response(serializer_instance.data)
        return Response(serializer_instance.errors, status=400)

    def delete(self, request, pk):

        qs = get_object_or_404(RentalBookingDb, pk=pk)
        self.check_object_permissions(request, qs)
        if qs.status != 'pending':
            raise PermissionDenied("Only pending bookings can be cancelled...!")
        qs.status = 'cancelled'
        qs.save()
        return Response({"Message": "Booking cancelled successfully...!"},status=200)


class BookingStatusUpdateView(APIView):

    authentication_classes = [authentication.BasicAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def put(self, request, pk):
        if not request.user.is_staff:raise PermissionDenied("Only admin can update booking status...!")
        qs = get_object_or_404(RentalBookingDb, pk=pk)
        form_data = request.data
        status_value = form_data.get('status')
        if status_value not in ['confirmed', 'rejected']:
            return Response({"Message": "Invalid booking status...!"},status=400)
        if qs.status != 'pending':
            return Response({"Message": "Only pending bookings can be updated...!"},status=400)
        qs.status = status_value
        qs.save()
        return Response({"Message": "Booking status updated successfully...!"},status=200)







from django.shortcuts import render

# Create your views here.
from rest_framework import viewsets, permissions, status
from rest_framework.exceptions import PermissionDenied
from .permissions import IsTrainer, IsClient, IsAdmin
from .models import User, TrainerProfile, Subscription, Goal, Plan, DailyLog, Metric
from .serializers import (UserSerializer, UserRegistrationSerializer, SubscriptionSerializer, 
                          GoalSerializer,  OnboardingSerializer, PlanSerializer, DailyLogSerializer, MetricSerializer
)
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.decorators import action
from rest_framework.response import Response

class UserViewSet(viewsets.ModelViewSet):
    queryset         = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'register':
            return UserRegistrationSerializer
        if self.action == 'onboard':
            return OnboardingSerializer
        return UserSerializer

    def get_permissions(self):
        if self.action in ['register', 'onboard']:
            return [permissions.AllowAny()] if self.action == 'register' else [permissions.IsAuthenticated()]
        return super().get_permissions()

    @action(detail=False, methods=['post'], url_path='register')
    def register(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        output = UserSerializer(user, context={'request': request})
        return Response(output.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'], url_path='onboard', permission_classes=[permissions.IsAuthenticated])
    def onboard(self, request, pk=None):
        """
        POST /api/users/{id}/onboard/
        Updates name, country, state, and flips is_onboarded=True
        """
        user = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.update(user, serializer.validated_data)
        return Response({'success': True}, status=status.HTTP_200_OK)
class SubscriptionViewSet(viewsets.ModelViewSet):    
    queryset = Subscription.objects.all()
    serializer_class = SubscriptionSerializer
    
    def get_queryset(self):
        user = self.request.user

        if user.role == 'user':
            return Subscription.objects.filter(client=user)

        if user.role == 'trainer':
            return Subscription.objects.filter(trainer=user)

        return Subscription.objects.all()

    def perform_create(self, serializer):
        serializer.save(client=self.request.user)

    def get_permissions(self):
        if self.action == 'create':
            return [IsClient()]
        elif self.action in ['list', 'retrieve']:
            return [IsAuthenticated()]
        return [IsAdminUser()]
    
class GoalViewSet(viewsets.ModelViewSet):
    queryset = Goal.objects.all()
    serializer_class = GoalSerializer

    def get_queryset(self):
        user = self.request.user
        if user.role == 'client':
            return Goal.objects.filter(user=user)
        if user.role == 'trainer':            
            client_ids = user.client_subscriptions.values_list('client', flat=True)
            return Goal.objects.filter(user__in=client_ids)
        return Goal.objects.none()

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsClient()]
        return [IsAuthenticated()]

class PlanViewSet(viewsets.ModelViewSet):
    queryset = Plan.objects.all()
    serializer_class = PlanSerializer
    
    def get_queryset(self):
        user = self.request.user
        if user.role == 'client':
            return Plan.objects.filter(user=user)
        if user.role == 'trainer':
            return Plan.objects.filter(trainer=user)
        return Plan.objects.none()

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsTrainer()]
        return [IsAuthenticated()]

    def perform_create(self, serializer):
        client = serializer.validated_data['user']
        trainer = self.request.user
        if not Subscription.objects.filter(client=client, trainer=trainer, status='active').exists():
            raise PermissionDenied("Trainer is not subscribed to this client")
        serializer.save(trainer=trainer)

        if not Subscription.objects.filter(
            trainer=trainer,
            client=client,
            status='active'
        ).exists():
            raise PermissionDenied("You can only create plans for your active clients.")

        serializer.save(trainer=trainer)

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsTrainer()]

        if self.action in ['list', 'retrieve']:
            return [IsAuthenticated()]

        
        return [IsAdminUser()]

class DailyLogViewSet(viewsets.ModelViewSet):
    queryset = DailyLog.objects.all()
    serializer_class = DailyLogSerializer

class MetricViewSet(viewsets.ModelViewSet):
    queryset = Metric.objects.all()
    serializer_class = MetricSerializer
# users/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .views import (
    UserViewSet,
    SubscriptionViewSet,
    GoalViewSet,
    PlanViewSet,
    DailyLogViewSet,
    MetricViewSet,
)

router = DefaultRouter()
router.register('users',           UserViewSet,           basename='user')
router.register('subscriptions',   SubscriptionViewSet,   basename='subscription')
router.register('goals',           GoalViewSet,           basename='goal')
router.register('plans',           PlanViewSet,           basename='plan')
router.register('daily-logs',      DailyLogViewSet,       basename='dailylog')
router.register('metrics',         MetricViewSet,         basename='metric')

urlpatterns = [
    path('', include(router.urls)),
    path(
        'users/register/',
        UserViewSet.as_view({'post': 'register'}),
        name='user-register'
    ),
    
    # JWT auth endpoints:
    path('auth/login/',           TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/token/refresh/',   TokenRefreshView.as_view(),     name='token_refresh'),
]

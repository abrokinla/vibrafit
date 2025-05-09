from rest_framework import serializers
from .models import User, TrainerProfile, Subscription, Goal, Plan, DailyLog, Metric

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model  = User
        fields = [
            'id','email','role',
            'is_active','is_staff','created_at','updated_at',
            # expose onboarding/profile fields
            'name','country','state','is_onboarded',
        ]
        read_only_fields = [
            'id','is_active','is_staff','created_at','updated_at',
            'is_onboarded',
        ]


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model  = User
        fields = ['id', 'email', 'password', 'role']
        read_only_fields = ['id']

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        if user.role == 'trainer':
            TrainerProfile.objects.create(user=user)
        return user


class OnboardingSerializer(serializers.Serializer):
    name    = serializers.CharField(max_length=100)
    country = serializers.CharField(max_length=100)
    state   = serializers.CharField(max_length=100)

    def update(self, instance, validated_data):
        # instance is a User
        instance.name         = validated_data['name']
        instance.country      = validated_data['country']
        instance.state        = validated_data['state']
        instance.is_onboarded = True
        instance.save()
        return instance

class SubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscription
        fields = ['id', 'client', 'trainer', 'start_date', 'end_date', 'status']
        read_only_fields = ['client']

class GoalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Goal
        fields = ['id', 'user', 'description', 'target_value', 'target_date', 'status', 'created_at']
        read_only_fields = ['created_at']

class PlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = Plan
        fields = ['id', 'user', 'trainer', 'date', 'nutrition_plan', 'exercise_plan', 'created_at']
        read_only_fields = ['trainer', 'created_at']

class DailyLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = DailyLog
        fields = ['id', 'user', 'plan', 'date', 'actual_nutrition', 'actual_exercise', 'completion_percentage', 'notes']

class MetricSerializer(serializers.ModelSerializer):
    class Meta:
        model = Metric
        fields = ['id', 'user', 'type', 'value', 'recorded_at']

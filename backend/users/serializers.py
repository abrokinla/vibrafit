from rest_framework import serializers
from .models import User, TrainerProfile, Subscription, Goal, Plan, DailyLog, Metric

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id','email','role','is_active','is_staff','created_at','updated_at']
        read_only_fields = ['id','is_active','is_staff','created_at','updated_at']


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
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

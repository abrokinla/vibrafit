from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from users.models import User, TrainerProfile, Subscription, Plan, Goal
from rest_framework_simplejwt.tokens import RefreshToken

def get_token_for_user(user):
    refresh = RefreshToken.for_user(user)
    return str(refresh.access_token)

class AuthAndRegistrationTests(APITestCase):
    def test_client_registration_and_login(self):
        url = reverse('user-register')
        data = {'email': 'cli@example.com', 'password': 'pass1234', 'role': 'client'}
        resp = self.client.post(url, data, format='json')
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(email='cli@example.com', role='client').exists())

        # now login
        login_url = reverse('token_obtain_pair')
        resp2 = self.client.post(login_url, {'email': 'cli@example.com', 'password': 'pass1234'}, format='json')
        self.assertEqual(resp2.status_code, status.HTTP_200_OK)
        self.assertIn('access', resp2.data)

    def test_trainer_registration_creates_profile(self):
        url = reverse('user-register')
        data = {'email': 'trn@example.com', 'password': 'pass1234', 'role': 'trainer'}
        resp = self.client.post(url, data, format='json')
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        user = User.objects.get(email='trn@example.com')
        self.assertEqual(user.role, 'trainer')
        self.assertTrue(TrainerProfile.objects.filter(user=user).exists())

class SubscriptionTests(APITestCase):
    def setUp(self):
        # create client and trainer
        self.client_user = User.objects.create_user(email='cli@x.com', password='pw', role='client')
        self.trainer = User.objects.create_user(email='trn@x.com', password='pw', role='trainer')
        # active subscription
        self.sub = Subscription.objects.create(client=self.client_user, trainer=self.trainer,
                                               start_date='2025-01-01', end_date='2025-12-31', status='active')

    def test_client_can_create_subscription(self):
        token = get_token_for_user(self.client_user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')

        url = reverse('subscription-list')
        data = {
            'trainer': self.trainer.id,
            'start_date': '2025-02-01',
            'end_date': '2025-12-31',
            'status': 'active'
        }
        resp = self.client.post(url, data, format='json')
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertEqual(resp.data['client'], self.client_user.id)

    def test_client_list_own_subscriptions(self):
        token = get_token_for_user(self.client_user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')

        url = reverse('subscription-list')
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(len(resp.data), 1)
        self.assertEqual(resp.data[0]['client'], self.client_user.id)

    def test_trainer_list_their_subscriptions(self):
        token = get_token_for_user(self.trainer)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')

        url = reverse('subscription-list')
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(len(resp.data), 1)
        self.assertEqual(resp.data[0]['trainer'], self.trainer.id)

class PlanTests(APITestCase):
    def setUp(self):
        self.client_user = User.objects.create_user(email='cli2@x.com', password='pw', role='client')
        self.trainer = User.objects.create_user(email='trn2@x.com', password='pw', role='trainer')
        # need a subscription for plan creation
        Subscription.objects.create(client=self.client_user, trainer=self.trainer,
                                    start_date='2025-01-01', end_date='2025-12-31', status='active')

    def test_trainer_can_create_plan_for_active_client(self):
        token = get_token_for_user(self.trainer)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')

        url = reverse('plan-list')
        data = {
            'user': self.client_user.id,
            'date': '2025-03-01',
            'nutrition_plan': 'Eat healthy',
            'exercise_plan': 'Run 5k'
        }
        resp = self.client.post(url, data, format='json')
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertEqual(resp.data['trainer'], self.trainer.id)

    def test_trainer_cannot_create_plan_for_non_client(self):
        other = User.objects.create_user(email='cli3@x.com', password='pw', role='client')
        token = get_token_for_user(self.trainer)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')

        url = reverse('plan-list')
        data = {
            'user': other.id,
            'date': '2025-03-01',
            'nutrition_plan': 'Eat healthy',
            'exercise_plan': 'Run 5k'
        }
        resp = self.client.post(url, data, format='json')
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

import json
import mock

from django.urls import reverse
from test_utils import APITest, FAKE_UUIDS, factories

from enterprise.constants import ENTERPRISE_ADMIN_ROLE
from integrated_channels.canvas.models import CanvasEnterpriseCustomerConfiguration


class CanvasConfigurationViewSetTests(APITest):
    def setUp(self):
        super(CanvasConfigurationViewSetTests, self).setUp()
        self.user.is_superuser = True
        self.user.save()

        self.enterprise_customer = factories.EnterpriseCustomerFactory(uuid=FAKE_UUIDS[0])
        self.enterprise_customer_user = factories.EnterpriseCustomerUserFactory(
            enterprise_customer=self.enterprise_customer,
            user_id=self.user.id,
        )

        self.canvas_enterprise_customer_configuration = factories.CanvasEnterpriseCustomerConfigurationFactory(
            enterprise_customer=self.enterprise_customer,
        )

    @mock.patch('enterprise.rules.crum.get_current_request')
    def test_list(self, mock_current_request):
        mock_current_request.return_value = self.get_request_with_jwt_cookie(
            system_wide_role=ENTERPRISE_ADMIN_ROLE,
        )
        url = reverse('api:v1:canvas:configuration-list')
        response = self.client.get(url)
        data = json.loads(response.content.decode('utf-8')).get('results')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(len(data) == 1)
        self.assertEqual(data[0].get('canvas_account_id'),
                         self.canvas_enterprise_customer_configuration.canvas_account_id)
        self.assertEqual(data[0].get('enterprise_customer'),
                         self.canvas_enterprise_customer_configuration.enterprise_customer.uuid)

    @mock.patch('enterprise.rules.crum.get_current_request')
    def test_get(self, mock_current_request):
        mock_current_request.return_value = self.get_request_with_jwt_cookie(
            system_wide_role=ENTERPRISE_ADMIN_ROLE,
        )
        url = reverse('api:v1:canvas:configuration-detail', args=[self.canvas_enterprise_customer_configuration.id])
        response = self.client.get(url)
        data = json.loads(response.content.decode('utf-8'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data.get('canvas_account_id'),
                         self.canvas_enterprise_customer_configuration.canvas_account_id)
        self.assertEqual(data.get('enterprise_customer'),
                         self.canvas_enterprise_customer_configuration.enterprise_customer.uuid)

    @mock.patch('enterprise.rules.crum.get_current_request')
    def test_post(self, mock_current_request):
        self.canvas_enterprise_customer_configuration.delete()

        mock_current_request.return_value = self.get_request_with_jwt_cookie(
            system_wide_role=ENTERPRISE_ADMIN_ROLE,
        )
        url = reverse('api:v1:canvas:configuration-list')
        payload = {
            'active': True,
            'canvas_account_id': 0,
            'enterprise_customer': self.enterprise_customer.uuid,
        }
        response = self.client.post(url, payload, format='json')
        data = json.loads(response.content.decode('utf-8'))
        self.assertEqual(response.status_code, 201)
        self.assertEqual(data.get('canvas_account_id'), 0)
        self.assertEqual(data.get('enterprise_customer'), self.enterprise_customer.uuid)

    @mock.patch('enterprise.rules.crum.get_current_request')
    def test_update(self, mock_current_request):
        mock_current_request.return_value = self.get_request_with_jwt_cookie(
            system_wide_role=ENTERPRISE_ADMIN_ROLE,
        )
        url = reverse('api:v1:canvas:configuration-detail', args=[self.canvas_enterprise_customer_configuration.id])
        payload = {
            'canvas_account_id': 1000,
            'enterprise_customer': FAKE_UUIDS[0],
        }
        response = self.client.put(url, payload)
        self.canvas_enterprise_customer_configuration.refresh_from_db()
        self.assertEqual(self.canvas_enterprise_customer_configuration.canvas_account_id, 1000)
        self.assertEqual(response.status_code, 200)

    @mock.patch('enterprise.rules.crum.get_current_request')
    def test_partial_update(self, mock_current_request):
        mock_current_request.return_value = self.get_request_with_jwt_cookie(
            system_wide_role=ENTERPRISE_ADMIN_ROLE,
        )
        url = reverse('api:v1:canvas:configuration-detail', args=[self.canvas_enterprise_customer_configuration.id])
        payload = {
            'canvas_account_id': 100,
        }
        response = self.client.patch(url, payload)
        self.assertEqual(response.status_code, 200)

    @mock.patch('enterprise.rules.crum.get_current_request')
    def test_destroy(self, mock_current_request):
        mock_current_request.return_value = self.get_request_with_jwt_cookie(
            system_wide_role=ENTERPRISE_ADMIN_ROLE,
        )
        url = reverse('api:v1:canvas:configuration-detail', args=[self.canvas_enterprise_customer_configuration.id])
        response = self.client.delete(url)
        configs = CanvasEnterpriseCustomerConfiguration.objects.filter()
        self.assertEqual(response.status_code, 204)
        self.assertEqual(len(configs), 0)


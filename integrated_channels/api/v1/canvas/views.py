"""
Viewsets for Canvas
"""
from rest_framework import permissions, status, viewsets
from rest_framework.response import Response
from edx_rbac.mixins import PermissionRequiredMixin
from enterprise.models import EnterpriseCustomerUser


from integrated_channels.canvas.models import CanvasEnterpriseCustomerConfiguration

from .serializers import CanvasEnterpriseCustomerConfigurationSerializer


class CanvasConfigurationViewSet(PermissionRequiredMixin, viewsets.ModelViewSet):
    serializer_class = CanvasEnterpriseCustomerConfigurationSerializer
    permission_classes = (permissions.IsAuthenticated, permissions.DjangoModelPermissions,)
    permission_required = 'enterprise.can_access_admin_dashboard'

    def get_queryset(self):
        enterprise_customer_users = EnterpriseCustomerUser.objects.filter(user_id=self.request.user.id)
        if enterprise_customer_users:
            enterprise_customers_uuids = [enterprise_customer_user.enterprise_customer.uuid for
                                          enterprise_customer_user in enterprise_customer_users]
            return CanvasEnterpriseCustomerConfiguration.objects.filter(
                enterprise_customer__uuid__in=enterprise_customers_uuids
            )
        return Response(status=status.HTTP_404_NOT_FOUND)

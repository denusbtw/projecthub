from rest_framework.views import exception_handler

from projecthub.core.models import TenantMembership


def custom_exception_handler(exc, context):
    # Call REST framework's default exception handler first,
    # to get the standard error response.
    response = exception_handler(exc, context)

    # Now add the HTTP status code to the response.
    if response is not None:
        response.data["status_code"] = response.status_code

    return response


def get_tenant_membership(tenant, user):
    return TenantMembership.objects.filter(user=user, tenant=tenant).first()
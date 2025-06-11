import pytest
from django.core.exceptions import PermissionDenied
from django.http import Http404

from projecthub.core.middleware import TenantMiddleware


@pytest.mark.django_db
class TestTenantMiddleware:

    def test_no_error_if_subdomain_is_none_and_whitelisted_path(self, rf):
        request = rf.get("/admin/")
        middleware = TenantMiddleware(lambda req: None)
        middleware(request)

    def test_error_if_no_subdomain(self, rf):
        request = rf.get("/")
        middleware = TenantMiddleware(lambda req: None)

        with pytest.raises(PermissionDenied) as exc:
            middleware(request)

        assert "Subdomain required" in str(exc.value)

    def test_no_error_if_subdomain(self, rf, tenant_factory):
        tenant_factory(sub_domain="subdomain")
        request = rf.get("/", HTTP_HOST="subdomain.localhost")
        middleware = TenantMiddleware(lambda req: None)
        middleware(request)

    def test_error_if_tenant_with_this_subdomain_does_not_exist(self, rf):
        request = rf.get("/", HTTP_HOST="subdomain.localhost")
        middleware = TenantMiddleware(lambda req: None)

        with pytest.raises(Http404) as exc:
            middleware(request)

        assert "Tenant is not found" in str(exc.value)

    def test_error_if_tenant_is_inactive(self, rf, tenant_factory):
        tenant_factory(sub_domain="subdomain", is_active=False)
        request = rf.get("/", HTTP_HOST="subdomain.localhost")
        middleware = TenantMiddleware(lambda req: None)

        with pytest.raises(PermissionDenied) as exc:
            middleware(request)

        assert "Tenant is inactive" in str(exc.value)

    def test_tenant_is_set_if_exists(self, tenant, http_host, rf):
        request = rf.get("/", HTTP_HOST=http_host)
        middleware = TenantMiddleware(lambda req: None)
        middleware(request)
        assert request.tenant == tenant

import pytest

from projecthub.core.middleware import TenantMiddleware


@pytest.mark.django_db
class TestTenantMiddleware:

    def test_tenant_is_set_if_exists(self, tenant, http_host, rf):
        request = rf.get("/", HTTP_HOST=http_host)
        middleware = TenantMiddleware(lambda req: None)
        middleware(request)
        assert request.tenant == tenant

    def test_tenant_is_none_if_does_not_exist(self, rf):
        request = rf.get("/", HTTP_HOST="doesnotexist.localhost")
        middleware = TenantMiddleware(lambda req: None)
        middleware(request)
        assert request.tenant is None

    def test_tenant_middleware_resolves_normalized_subdomain(self, tenant_factory, rf):
        tenant = tenant_factory(sub_domain="this_is_tenant")
        request = rf.get("/", HTTP_HOST="this-is-tenant.localhost")
        middleware = TenantMiddleware(lambda req: None)
        middleware(request)
        assert request.tenant == tenant

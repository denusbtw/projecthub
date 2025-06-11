from django.core.exceptions import PermissionDenied
from django.http import Http404


class TenantMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.whitelist_paths = [
            "/admin",
            "/api/auth",
        ]

    def __call__(self, request):
        if self.is_whitelisted_path(request.path):
            request.tenant = None
            return self.get_response(request)

        sub_domain = self.get_sub_domain_from_request(request)
        if sub_domain is None:
            raise PermissionDenied("Subdomain required.")

        tenant = self.get_tenant(sub_domain)
        if tenant is None:
            raise Http404("Tenant is not found.")

        request.tenant = tenant
        return self.get_response(request)

    def get_sub_domain_from_request(self, request):
        domain = request.get_host().split(":")[0]
        parts = domain.split(".")
        return parts[0] if len(parts) > 1 else None

    def get_tenant(self, sub_domain):
        from .models import Tenant

        try:
            tenant = Tenant.objects.get(sub_domain=sub_domain)
            if tenant.is_inactive:
                raise PermissionDenied("Tenant is inactive.")
            return tenant
        except Tenant.DoesNotExist:
            return None

    def is_whitelisted_path(self, path):
        return any(path.startswith(p) for p in self.whitelist_paths)

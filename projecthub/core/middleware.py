class TenantMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        sub_domain = self.get_sub_domain_from_request(request)

        if sub_domain is None:
            request.tenant = None
            return self.get_response(request)

        from .models import Tenant

        try:
            tenant = Tenant.objects.get(sub_domain=sub_domain)
            request.tenant = tenant
        except Tenant.DoesNotExist:
            request.tenant = None

        return self.get_response(request)

    def get_sub_domain_from_request(self, request):
        domain = request.get_host().split(":")[0]
        parts = domain.split(".")
        return self.normalize_sub_domain(parts[0]) if len(parts) > 1 else None

    def normalize_sub_domain(self, sub_domain):
        return sub_domain.replace("-", "_")

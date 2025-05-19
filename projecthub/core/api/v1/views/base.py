from rest_framework import exceptions
from rest_framework.generics import GenericAPIView


# not final version
class SecureGenericAPIView(GenericAPIView):
    policy_classes = []

    def not_found(self, request, message=None, code=None):
        raise exceptions.NotFound(detail=message, code=code)

    def get_policies(self):
        return [policy() for policy in self.policy_classes]

    def check_policies(self, request):
        for policy in self.get_policies():
            if not policy.has_access(request, self):
                self.not_found(
                    request,
                    message=getattr(policy, "message", None),
                    code=getattr(policy, "code", None)
                )

    def check_object_policies(self, request, obj):
        for policy in self.get_policies():
            if not policy.has_object_access(request, self, obj):
                self.not_found(
                    request,
                    message=getattr(policy, "message", None),
                    code=getattr(policy, "code", None)
                )

    def get_object(self):
        obj = super().get_object()
        self.check_object_policies(self.request, obj)
        return obj

    def initial(self, request, *args, **kwargs):
        """
        Runs anything that needs to occur prior to calling the method handler.
        """
        self.format_kwarg = self.get_format_suffix(**kwargs)

        # Perform content negotiation and store the accepted info on the request
        neg = self.perform_content_negotiation(request)
        request.accepted_renderer, request.accepted_media_type = neg

        # Determine the API version, if versioning is in use.
        version, scheme = self.determine_version(request, *args, **kwargs)
        request.version, request.versioning_scheme = version, scheme

        # Ensure that the incoming request is permitted
        self.perform_authentication(request)
        self.check_policies(request)
        self.check_permissions(request)
        self.check_throttles(request)



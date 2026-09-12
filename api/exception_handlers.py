"""Consistent JSON error responses for the API."""

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import exception_handler as drf_exception_handler

from main.exceptions import DomainError, NotFoundError, PermissionDeniedError, ValidationDomainError


def api_exception_handler(exc, context):
    if isinstance(exc, PermissionDeniedError):
        return Response(
            {'detail': exc.message, 'code': 'permission_denied'},
            status=status.HTTP_403_FORBIDDEN,
        )
    if isinstance(exc, NotFoundError):
        return Response(
            {'detail': exc.message, 'code': 'not_found'},
            status=status.HTTP_404_NOT_FOUND,
        )
    if isinstance(exc, ValidationDomainError):
        return Response(
            {'detail': exc.message, 'code': 'validation_error'},
            status=status.HTTP_400_BAD_REQUEST,
        )
    if isinstance(exc, DomainError):
        return Response(
            {'detail': exc.message, 'code': 'domain_error'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    response = drf_exception_handler(exc, context)
    if response is not None:
        if isinstance(response.data, dict) and 'detail' in response.data and 'code' not in response.data:
            response.data['code'] = getattr(exc, 'default_code', 'error')
        elif isinstance(response.data, dict) and 'code' not in response.data:
            response.data.setdefault('code', 'validation_error')
    return response

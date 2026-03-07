"""
Consistent JSON response helpers for the API.
"""
from rest_framework.response import Response
from rest_framework import status


def success_response(data=None, status_code=status.HTTP_200_OK):
    """Return a standard success response."""
    payload = {'status': 'success', 'data': data if data is not None else {}}
    return Response(payload, status=status_code)


def error_response(message, status_code=status.HTTP_400_BAD_REQUEST):
    """Return a standard error response."""
    return Response({'status': 'error', 'message': str(message)}, status=status_code)

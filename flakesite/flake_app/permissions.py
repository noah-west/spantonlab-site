from rest_framework import permissions

class IsOwnerOrReadOnly(permissions.BasePermission):
    '''
    Permission that only allows the owner of a flake to update or delete a flake.
    '''
    def has_object_permission(self, request, view, obj):
        if obj is None:
            return True

        if request.method in permissions.SAFE_METHODS:
            return True
        
        if obj.owner is None:
            return True

        return obj.owner == request.user

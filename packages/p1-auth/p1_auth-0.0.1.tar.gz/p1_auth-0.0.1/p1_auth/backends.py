import logging

import jwt
from django.conf import settings
from django.contrib import auth
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import AbstractBaseUser
from django.core.exceptions import PermissionDenied
from django.db import DatabaseError
from django.utils.module_loading import import_string
from rest_framework import authentication

from p1_auth.models import RelatedAssignment

# Get an instance of a logger
logger = logging.getLogger(__name__)


def decode_jwt(request):
    '''Decode Platform One JWT'''
    logger.error(request.headers["Authorization"])
    encoded_auth_header = request.headers["Authorization"]
    auth_header = jwt.decode(encoded_auth_header.split("Bearer ")[1],
                             options={"verify_signature": False})
    logger.error(auth_header)
    return auth_header


class PlatformOneAuthentication(ModelBackend):
    '''Platform One specific authentication'''

    def authenticate(self, request, *args, **kwargs):
        '''attempt to decode Platform One JWT'''
        if hasattr(request, 'headers') and "Authorization" in request.headers \
                and request.headers["Authorization"].startswith("Bearer "):
            # decode JWT
            jwt_decoded = decode_jwt(request)

            # determine username and username field
            username = {
                auth.get_user_model().USERNAME_FIELD:
                jwt_decoded[getattr(
                    settings,
                    "JWT_PREFERRED_USERNAME_FIELD",
                    "preferred_username")]
            }

            # retrieve or create user based on username
            user, new = auth.get_user_model().objects.get_or_create(**username)

            if isinstance(user, AbstractBaseUser) and\
                    user.has_usable_password():
                user.set_unusable_password()
                user.save()

            # update attributes from JWT
            self.update_user_attributes(jwt_decoded, user)

            # update model connections to user
            self.update_user_membership(jwt_decoded, user)

            # update user staff status
            self.update_staff_status(jwt_decoded, user)

            # update user superuser status
            self.update_superuser_status(jwt_decoded, user)

            self.update_from_related_assignments(jwt_decoded, user)

            self.update_custom(jwt_decoded, user, new)

            # return the user
            return user
        # Raise exception to fail authentication and logout session if
        # REQUIRE_JWT
        if hasattr(settings, "REQUIRE_JWT") and settings.REQUIRE_JWT:
            auth.logout(request)
            raise PermissionDenied()
        # fail this authentication method
        return None

    def update_custom(self, jwt_decoded, user, new):
        """
        Handle custom logic when authenticating a user
        Parameters:
        jwt_decoded (dict): The dictionary containing the decoded JWT.
        user (AbstractBaseUser): The authenticated user object, it is expected
        to be an AbstractBaseUser, but can be any model.
        new (bool): A boolean that is true if the user object has been created
        by this request.
        """
        if hasattr(settings, "CUSTOM_AUTHENTICATION_LOGIC") and\
                settings.CUSTOM_AUTHENTICATION_LOGIC:
            for custom in settings.CUSTOM_AUTHENTICATION_LOGIC:
                if isinstance(custom, str):
                    custom = import_string(custom)
                if callable(custom):
                    custom(jwt_decoded, user, new)

    def update_from_related_assignments(self, jwt_decoded, user):
        assignments = RelatedAssignment.objects.all()

        for assignment in assignments:
            assignment.validate(user=user, jwt_json=jwt_decoded)

    def update_superuser_status(self, jwt_decoded, user):
        if hasattr(settings, "USER_SUPERUSER_FLAG"):
            if settings.USER_SUPERUSER_FLAG in jwt_decoded:
                su_attribute = jwt_decoded[settings.USER_SUPERUSER_FLAG]
                if hasattr(settings, "USER_SUPERUSER_VALUE"):
                    if isinstance(su_attribute, list):
                        user.is_superuser = settings.USER_SUPERUSER_VALUE in \
                            su_attribute
                    else:
                        user.is_superuser = settings.USER_SUPERUSER_VALUE == \
                            su_attribute
                else:
                    user.is_superuser = len(su_attribute) > 0
            else:
                user.is_superuser = False

            user.save()

    def update_staff_status(self, jwt_decoded, user):
        if hasattr(settings, "USER_STAFF_FLAG"):
            if settings.USER_STAFF_FLAG in jwt_decoded:
                staff_attribute = jwt_decoded[settings.USER_STAFF_FLAG]
                if hasattr(settings, "USER_STAFF_VALUE"):
                    if isinstance(staff_attribute, list):
                        user.is_staff = settings.USER_STAFF_VALUE in \
                            staff_attribute
                    else:
                        user.is_staff = settings.USER_STAFF_VALUE == \
                            staff_attribute
                else:
                    user.is_staff = len(staff_attribute) > 0
            else:
                user.is_staff = False

            user.save()

    def update_user_membership(self, jwt_decoded, user):
        if hasattr(settings, "USER_MEMBERSHIPS"):
            try:
                for model_key in settings.USER_MEMBERSHIPS:
                    for field_name, jwt_key in\
                            settings.USER_MEMBERSHIPS[model_key].items():
                        if jwt_key in jwt_decoded:
                            related = getattr(user, model_key)
                            string_values = jwt_decoded[jwt_key]
                            if isinstance(string_values, list):
                                for single_value in string_values:
                                    related.update_or_create(
                                        **{field_name: single_value})
                            else:
                                related.update_or_create(
                                    **{field_name: string_values})
            except DatabaseError as db_err:
                if 'Duplicate entry' in str(db_err):
                    return
                else:
                    logger.error("DB Error: %s", db_err)

    def update_user_attributes(self, jwt_decoded, user):
        if hasattr(settings, "USER_ATTRIBUTES_MAP"):
            for model_key in settings.USER_ATTRIBUTES_MAP:
                jwt_key = settings.USER_ATTRIBUTES_MAP[model_key]
                if jwt_key in jwt_decoded:
                    setattr(user, model_key, jwt_decoded[jwt_key])

            user.save()


class PlatformOneRestAuthentication(PlatformOneAuthentication,
                                    authentication.BaseAuthentication):
    def authenticate(self, request, *args, **kwargs):
        user = super(PlatformOneRestAuthentication, self).authenticate(request)
        if user is None:
            return user
        return (user, None)

    def authenticate_header(self, request):
        return "Bearer"

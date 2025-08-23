import logging
from copy import deepcopy

from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist
from django.db import DatabaseError, models

# Get an instance of a logger
logger = logging.getLogger(__name__)

# Create your models here.


class RelatedAssignment(models.Model):
    """Assign users to related model automatically"""
    object_model = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_pk = models.CharField('object ID', max_length=512)
    foreign_object = GenericForeignKey("object_model", "object_pk")

    def check_attributes(self, jwt_json):
        """Check jwt for related attributes"""
        try:
            validators = self.validators.all()
            for check in validators:
                value = self.__traverse(jwt_json, check.jwt_attribute)
                if isinstance(value, list):
                    if check.expected_value not in value:
                        raise ItemNotFoundException('Values do not match')
                else:
                    if check.expected_value != value:
                        raise ItemNotFoundException('Values do not match')
            return True
        except ItemNotFoundException:
            return False

    def __traverse(self, json, path):
        json = deepcopy(json)
        path = deepcopy(path)
        if isinstance(path, dict):
            key, path = path.popitem()
            if key in json:
                return self.__traverse(json[key], path)
            else:
                raise ItemNotFoundException('Unable to follow path')
        if path in json:
            return json[path]
        raise ItemNotFoundException('Unable to follow path')

    def get_instance(self):
        """Return model instance"""
        return self.foreign_object

    def validate(self, user, jwt_json):
        """Check attributes and make assignment on success"""
        if self.check_attributes(jwt_json=jwt_json):
            obj = self.get_instance()
            if obj is not None:
                fields = obj._meta.get_fields(include_hidden=True)
                for field in fields:
                    if field.is_relation and \
                            field.related_model == user._meta.model:
                        self.__add_user(user, obj, field)
                        return True
        return False

    def __add_user(self, user, obj, field):
        try:
            if field.many_to_many or field.one_to_many:
                if hasattr(field, 'get_accessor_name') and\
                        field.get_accessor_name():
                    getattr(obj, field.get_accessor_name()).add(user)
                elif hasattr(field, 'attname') and field.attname:
                    getattr(obj, field.attname).add(user)
                elif hasattr(field, 'related_name') and field.related_name:
                    getattr(obj, field.related_name).add(user)
            elif field.many_to_one:
                if hasattr(field.remote_field, 'get_accessor_name') and\
                        field.remote_field.get_accessor_name():
                    getattr(user, field.remote_field.get_accessor_name())\
                        .add(obj)
                elif hasattr(field.remote_field, 'attname') and\
                        field.remote_field.attname:
                    getattr(user, field.remote_field.attname).add(obj)
                elif hasattr(field.remote_field, 'related_name') and\
                        field.remote_field.related_name:
                    getattr(user, field.remote_field.related_name).add(obj)
            elif field.one_to_one:
                setattr(obj, field.name, user)
                obj.save()
        except DatabaseError as db_err:
            if 'Duplicate entry' in str(db_err):
                return
            else:
                logger.error("DB Error: %s", db_err)

    def __str__(self):
        return f'{self.get_instance()} ({self.object_model})'


class AttributeCheck(models.Model):
    """Check attributes"""
    assignment = models.ForeignKey(
        RelatedAssignment, related_name='validators', on_delete=models.CASCADE)
    jwt_attribute = models.JSONField()
    expected_value = models.JSONField()

    def __str__(self):
        return f'{self.expected_value} - {self.assignment}'


class ItemNotFoundException(ObjectDoesNotExist):
    """Exception used for traversal"""
    pass

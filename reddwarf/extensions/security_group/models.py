# vim: tabstop=4 shiftwidth=4 softtabstop=4

# Copyright 2013 Hewlett-Packard Development Company, L.P.
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.
#

"""
Model classes for Security Groups and Security Group Rules on instances.
"""
import reddwarf.common.remote
from reddwarf.common import cfg
from reddwarf.common import exception
from reddwarf.db.models import DatabaseModelBase
from reddwarf.common.models import NovaRemoteModelBase
from reddwarf.openstack.common import log as logging
from reddwarf.openstack.common.gettextutils import _

from novaclient import exceptions as nova_exceptions

CONF = cfg.CONF
LOG = logging.getLogger(__name__)


def persisted_models():
    return {
        'security_group': SecurityGroup,
        'security_group_rule': SecurityGroupRule,
        'security_group_instance_association':
        SecurityGroupInstanceAssociation,
    }


class SecurityGroup(DatabaseModelBase):
    _data_fields = ['id', 'name', 'description', 'user', 'tenant_id',
                    'created', 'updated', 'deleted', 'deleted_at']

    @classmethod
    def create_sec_group(cls, name, description, context):
        try:
            remote_sec_group = RemoteSecurityGroup.create(name,
                                                          description,
                                                          context)

            if not remote_sec_group:
                raise exception.SecurityGroupCreationError(
                    "Failed to create Security Group")
            else:
                return cls.create(
                    id=remote_sec_group.data()['id'],
                    name=name,
                    description=description,
                    user=context.user,
                    tenant_id=context.tenant)

        except exception.SecurityGroupCreationError, e:
            LOG.exception("Failed to create remote security group")
            raise e

    @classmethod
    def create_for_instance(cls, instance_id, context):
        # Create a new security group
        name = _("SecGroup_%s") % instance_id
        description = \
            _("Default Security Group For DBaaS Instance <%s>") % instance_id
        sec_group = cls.create_sec_group(name, description, context)

        # Currently this locked down by default, since we don't create any
        # default security group rules for the security group.

        # Create security group instance association
        SecurityGroupInstanceAssociation.create(
            security_group_id=sec_group["id"],
            instance_id=instance_id)

        return sec_group

    @classmethod
    def get_security_group_by_id_or_instance_id(self, id, tenant_id):
        try:
            return SecurityGroup.find_by(id=id,
                                         tenant_id=tenant_id,
                                         deleted=False)
        except exception.ModelNotFoundError:
            return SecurityGroupInstanceAssociation.\
                get_security_group_by_instance_id(id)

    def get_rules(self):
        return SecurityGroupRule.find_all(group_id=self.id,
                                          deleted=False)

    def delete(self, context):
        try:
            sec_group_rules = self.get_rules()
            if sec_group_rules:
                for rule in sec_group_rules:
                    rule.delete(context)

            RemoteSecurityGroup.delete(self.id, context)
            super(SecurityGroup, self).delete()

        except exception.ReddwarfError:
            LOG.exception('Failed to delete security group')
            raise exception.ReddwarfError("Failed to delete Security Group")

    @classmethod
    def delete_for_instance(cls, instance_id, context):
        association = SecurityGroupInstanceAssociation.find_by(
            instance_id=instance_id,
            deleted=False)
        if association:
            sec_group = association.get_security_group()
            sec_group.delete(context)
            association.delete()


class SecurityGroupRule(DatabaseModelBase):
    _data_fields = ['id', 'parent_group_id', 'protocol', 'from_port',
                    'to_port', 'cidr', 'group_id', 'created', 'updated',
                    'deleted', 'deleted_at']

    @classmethod
    def create_sec_group_rule(cls, sec_group, protocol, from_port,
                              to_port, cidr, context):
        try:
            remote_rule_id = RemoteSecurityGroup.add_rule(
                sec_group_id=sec_group['id'],
                protocol=protocol,
                from_port=from_port,
                to_port=to_port,
                cidr=cidr,
                context=context)

            if not remote_rule_id:
                raise exception.SecurityGroupRuleCreationError(
                    "Failed to create Security Group Rule")
            else:
                # Create db record
                return cls.create(
                    id=remote_rule_id,
                    protocol=protocol,
                    from_port=from_port,
                    to_port=to_port,
                    cidr=cidr,
                    group_id=sec_group['id'])

        except exception.SecurityGroupRuleCreationError, e:
            LOG.exception("Failed to create remote security group")
            raise e

    def get_security_group(self, tenant_id):
        return SecurityGroup.find_by(id=self.group_id,
                                     tenant_id=tenant_id,
                                     deleted=False)

    def delete(self, context):
        try:
            # Delete Remote Security Group Rule
            RemoteSecurityGroup.delete_rule(self.id, context)
            super(SecurityGroupRule, self).delete()
        except exception.ReddwarfError:
            LOG.exception('Failed to delete security group')
            raise exception.SecurityGroupRuleDeletionError(
                "Failed to delete Security Group")


class SecurityGroupInstanceAssociation(DatabaseModelBase):
    _data_fields = ['id', 'security_group_id', 'instance_id',
                    'created', 'updated', 'deleted', 'deleted_at']

    def get_security_group(self):
        return SecurityGroup.find_by(id=self.security_group_id,
                                     deleted=False)

    @classmethod
    def get_security_group_by_instance_id(cls, id):
        association = SecurityGroupInstanceAssociation.find_by(
            instance_id=id,
            deleted=False)
        return association.get_security_group()


class RemoteSecurityGroup(NovaRemoteModelBase):

    _data_fields = ['id', 'name', 'description', 'rules']

    def __init__(self, security_group=None, id=None, context=None):
        if id is None and security_group is None:
            msg = "Security Group does not have id defined!"
            raise exception.InvalidModelError(msg)
        elif security_group is None:
            try:
                client = reddwarf.common.remote.create_nova_client(context)
                self._data_object = client.security_groups.get(id)
            except nova_exceptions.NotFound, e:
                raise exception.NotFound(id=id)
            except nova_exceptions.ClientException, e:
                raise exception.ReddwarfError(str(e))
        else:
            self._data_object = security_group

    @classmethod
    def create(cls, name, description, context):
        """Creates a new Security Group"""
        client = reddwarf.common.remote.create_nova_client(context)
        try:
            sec_group = client.security_groups.create(name=name,
                                                      description=description)
        except nova_exceptions.ClientException, e:
            LOG.exception('Failed to create remote security group')
            raise exception.SecurityGroupCreationError(str(e))

        return RemoteSecurityGroup(security_group=sec_group)

    @classmethod
    def delete(cls, sec_group_id, context):
        client = reddwarf.common.remote.create_nova_client(context)

        try:
            client.security_groups.delete(sec_group_id)
        except nova_exceptions.ClientException, e:
            LOG.exception('Failed to delete remote security group')
            raise exception.SecurityGroupDeletionError(str(e))

    @classmethod
    def add_rule(cls, sec_group_id, protocol, from_port,
                 to_port, cidr, context):

        client = reddwarf.common.remote.create_nova_client(context)

        try:
            sec_group_rule = client.security_group_rules.create(
                parent_group_id=sec_group_id,
                ip_protocol=protocol,
                from_port=from_port,
                to_port=to_port,
                cidr=cidr)

            return sec_group_rule.id
        except nova_exceptions.ClientException, e:
            LOG.exception('Failed to add rule to remote security group')
            raise exception.SecurityGroupRuleCreationError(str(e))

    @classmethod
    def delete_rule(cls, sec_group_rule_id, context):
        client = reddwarf.common.remote.create_nova_client(context)

        try:
            client.security_group_rules.delete(sec_group_rule_id)

        except nova_exceptions.ClientException, e:
            LOG.exception('Failed to delete rule to remote security group')
            raise exception.SecurityGroupRuleDeletionError(str(e))

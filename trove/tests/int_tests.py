# Copyright 2014 OpenStack Foundation
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

import proboscis
from trove.tests.api import backups
from trove.tests.api import configurations
from trove.tests.api import databases
from trove.tests.api import datastores
from trove.tests.api import flavors
from trove.tests.api import instances
from trove.tests.api import instances_actions
from trove.tests.api.mgmt import accounts
from trove.tests.api.mgmt import admin_required
from trove.tests.api.mgmt import datastore_versions
from trove.tests.api.mgmt import hosts
from trove.tests.api.mgmt import instances as mgmt_instances
from trove.tests.api.mgmt import storage
from trove.tests.api import replication
from trove.tests.api import root
from trove.tests.api import user_access
from trove.tests.api import users
from trove.tests.api import versions
from trove.tests.scenario import groups
from trove.tests.scenario.groups import backup_group
from trove.tests.scenario.groups import cluster_group
from trove.tests.scenario.groups import configuration_group
from trove.tests.scenario.groups import database_actions_group
from trove.tests.scenario.groups import guest_log_group
from trove.tests.scenario.groups import instance_actions_group
from trove.tests.scenario.groups import instance_create_group
from trove.tests.scenario.groups import instance_delete_group
from trove.tests.scenario.groups import instance_error_create_group
from trove.tests.scenario.groups import instance_force_delete_group
from trove.tests.scenario.groups import instance_upgrade_group
from trove.tests.scenario.groups import module_group
from trove.tests.scenario.groups import negative_cluster_actions_group
from trove.tests.scenario.groups import replication_group
from trove.tests.scenario.groups import root_actions_group
from trove.tests.scenario.groups import user_actions_group


GROUP_SERVICES_INITIALIZE = "services.initialize"
GROUP_SETUP = 'dbaas.setup'


def build_group(*groups):
    def merge(collection, *items):
        for item in items:
            if isinstance(item, list):
                merge(collection, *item)
            else:
                if item not in collection:
                    collection.append(item)

    out = []
    merge(out, *groups)
    return out


def register(group_names, *test_groups, **kwargs):
    if kwargs:
        register(group_names, kwargs.values())
        for suffix, grp_set in kwargs.items():
            # Recursively call without the kwargs
            register([name + '_' + suffix for name in group_names], *grp_set)
        return

    # Do the actual registration here
    proboscis.register(groups=build_group(group_names),
                       depends_on_groups=build_group(*test_groups))
    # Now register the same groups with '-' instead of '_'
    proboscis.register(groups=build_group(
                       [name.replace('_', '-') for name in group_names]),
                       depends_on_groups=build_group(*test_groups))

black_box_groups = [
    flavors.GROUP,
    users.GROUP,
    user_access.GROUP,
    databases.GROUP,
    root.GROUP,
    GROUP_SERVICES_INITIALIZE,
    instances.GROUP_START,
    instances.GROUP_QUOTAS,
    instances.GROUP_SECURITY_GROUPS,
    backups.GROUP,
    replication.GROUP,
    configurations.GROUP,
    datastores.GROUP,
    instances_actions.GROUP_RESIZE,
    # TODO(SlickNik): The restart tests fail intermittently so pulling
    # them out of the blackbox group temporarily. Refer to Trove bug:
    # https://bugs.launchpad.net/trove/+bug/1204233
    # instances_actions.GROUP_RESTART,
    instances_actions.GROUP_STOP_MYSQL,
    instances.GROUP_STOP,
    versions.GROUP,
    instances.GROUP_GUEST,
    datastore_versions.GROUP,
]
proboscis.register(groups=["blackbox", "mysql"],
                   depends_on_groups=black_box_groups)

simple_black_box_groups = [
    GROUP_SERVICES_INITIALIZE,
    flavors.GROUP,
    versions.GROUP,
    instances.GROUP_START_SIMPLE,
    admin_required.GROUP,
    datastore_versions.GROUP,
]
proboscis.register(groups=["simple_blackbox"],
                   depends_on_groups=simple_black_box_groups)

black_box_mgmt_groups = [
    accounts.GROUP,
    hosts.GROUP,
    storage.GROUP,
    instances_actions.GROUP_REBOOT,
    admin_required.GROUP,
    mgmt_instances.GROUP,
    datastore_versions.GROUP,
]
proboscis.register(groups=["blackbox_mgmt"],
                   depends_on_groups=black_box_mgmt_groups)

#
# Group designations for datastore agnostic int-tests
#
# Base groups for all other groups
base_groups = [
    GROUP_SERVICES_INITIALIZE,
    flavors.GROUP,
    versions.GROUP,
    GROUP_SETUP
]

# Cluster-based groups
cluster_create_groups = list(base_groups)
cluster_create_groups.extend([groups.CLUSTER_DELETE_WAIT])

cluster_actions_groups = list(cluster_create_groups)
cluster_actions_groups.extend([groups.CLUSTER_ACTIONS_SHRINK_WAIT])

cluster_negative_actions_groups = list(negative_cluster_actions_group.GROUP)

cluster_root_groups = list(cluster_create_groups)
cluster_root_groups.extend([groups.CLUSTER_ACTIONS_ROOT_ENABLE])

cluster_root_actions_groups = list(cluster_actions_groups)
cluster_root_actions_groups.extend([groups.CLUSTER_ACTIONS_ROOT_ACTIONS])

cluster_restart_groups = list(cluster_create_groups)
cluster_restart_groups.extend([groups.CLUSTER_ACTIONS_RESTART_WAIT])

cluster_upgrade_groups = list(cluster_create_groups)
cluster_upgrade_groups.extend([groups.CLUSTER_UPGRADE_WAIT])

cluster_config_groups = list(cluster_create_groups)
cluster_config_groups.extend([groups.CLUSTER_CFGGRP_DELETE])

cluster_config_actions_groups = list(cluster_config_groups)
cluster_config_actions_groups.extend([groups.CLUSTER_ACTIONS_CFGGRP_ACTIONS])

cluster_groups = list(cluster_actions_groups)
cluster_groups.extend([cluster_group.GROUP])

# Single-instance based groups
instance_create_groups = list(base_groups)
instance_create_groups.extend([groups.INST_CREATE,
                               groups.INST_DELETE_WAIT])

instance_error_create_groups = list(base_groups)
instance_error_create_groups.extend([instance_error_create_group.GROUP])

instance_force_delete_groups = list(base_groups)
instance_force_delete_groups.extend([instance_force_delete_group.GROUP])

instance_init_groups = list(base_groups)
instance_init_groups.extend([instance_create_group.GROUP,
                             instance_delete_group.GROUP])

instance_upgrade_groups = list(instance_create_groups)
instance_upgrade_groups.extend([instance_upgrade_group.GROUP])

backup_groups = list(instance_create_groups)
backup_groups.extend([groups.BACKUP,
                      groups.BACKUP_INST])

backup_incremental_groups = list(backup_groups)
backup_incremental_groups.extend([backup_group.GROUP])

backup_negative_groups = list(backup_groups)
backup_negative_groups.extend([groups.BACKUP_CREATE_NEGATIVE])

configuration_groups = list(instance_create_groups)
configuration_groups.extend([configuration_group.GROUP])

configuration_create_groups = list(base_groups)
configuration_create_groups.extend([groups.CFGGRP_CREATE,
                                    groups.CFGGRP_DELETE])

database_actions_groups = list(instance_create_groups)
database_actions_groups.extend([database_actions_group.GROUP])

guest_log_groups = list(instance_create_groups)
guest_log_groups.extend([guest_log_group.GROUP])

instance_actions_groups = list(instance_create_groups)
instance_actions_groups.extend([instance_actions_group.GROUP])

instance_groups = list(instance_actions_groups)
instance_groups.extend([instance_error_create_group.GROUP,
                        instance_force_delete_group.GROUP])

module_groups = list(instance_create_groups)
module_groups.extend([module_group.GROUP])

module_create_groups = list(base_groups)
module_create_groups.extend([groups.MODULE_CREATE,
                             groups.MODULE_DELETE])

replication_groups = list(instance_create_groups)
replication_groups.extend([groups.REPL_INST_DELETE_WAIT])

replication_promote_groups = list(replication_groups)
replication_promote_groups.extend([replication_group.GROUP])

root_actions_groups = list(instance_create_groups)
root_actions_groups.extend([root_actions_group.GROUP])

user_actions_groups = list(instance_create_groups)
user_actions_groups.extend([user_actions_group.GROUP])

# groups common to all datastores
common_groups = list(instance_create_groups)
common_groups.extend([guest_log_groups, instance_init_groups, module_groups])

# Register: Component based groups
register(["backup"], backup_groups)
register(["backup_incremental"], backup_incremental_groups)
register(["backup_negative"], backup_negative_groups)
register(["cluster"], cluster_actions_groups)
register(["cluster_actions"], cluster_actions_groups)
register(["cluster_create"], cluster_create_groups)
register(["cluster_negative_actions"], cluster_negative_actions_groups)
register(["cluster_restart"], cluster_restart_groups)
register(["cluster_root"], cluster_root_groups)
register(["cluster_root_actions"], cluster_root_actions_groups)
register(["cluster_upgrade"], cluster_upgrade_groups)
register(["cluster_config"], cluster_config_groups)
register(["cluster_config_actions"], cluster_config_actions_groups)
register(["common"], common_groups)
register(["configuration"], configuration_groups)
register(["configuration_create"], configuration_create_groups)
register(["database"], database_actions_groups)
register(["guest_log"], guest_log_groups)
register(["instance"], instance_groups)
register(["instance_actions"], instance_actions_groups)
register(["instance_create"], instance_create_groups)
register(["instance_error"], instance_error_create_groups)
register(["instance_force_delete"], instance_force_delete_groups)
register(["instance_init"], instance_init_groups)
register(["instance_upgrade"], instance_upgrade_groups)
register(["module"], module_groups)
register(["module_create"], module_create_groups)
register(["replication"], replication_groups)
register(["replication_promote"], replication_promote_groups)
register(["root"], root_actions_groups)
register(["user"], user_actions_groups)

# Register: Datastore based groups
# These should contain all functionality currently supported by the datastore.
# Keeping them in alphabetical order may reduce the number of merge conflicts.
register(
    ["db2_supported"],
    single=[common_groups,
            configuration_groups,
            database_actions_groups,
            user_actions_groups, ],
    multi=[]
)

register(
    ["cassandra_supported"],
    single=[common_groups,
            backup_groups,
            database_actions_groups,
            configuration_groups,
            user_actions_groups, ],
    multi=[cluster_actions_groups,
           cluster_negative_actions_groups,
           cluster_root_actions_groups,
           cluster_config_actions_groups, ]
)

register(
    ["couchbase_supported"],
    single=[common_groups,
            backup_groups,
            root_actions_groups, ],
    multi=[]
)

register(
    ["couchdb_supported"],
    single=[common_groups,
            backup_groups,
            database_actions_groups,
            root_actions_groups,
            user_actions_groups, ],
    multi=[]
)

register(
    ["mariadb_supported"],
    single=[common_groups,
            backup_incremental_groups,
            configuration_groups,
            database_actions_groups,
            root_actions_groups,
            user_actions_groups, ],
    multi=[replication_promote_groups, ]
    # multi=[cluster_actions_groups,
    #        cluster_negative_actions_groups,
    #        cluster_root_actions_groups,
    #        replication_promote_groups, ]
)

register(
    ["mongodb_supported"],
    single=[common_groups,
            backup_groups,
            configuration_groups,
            database_actions_groups,
            root_actions_groups,
            user_actions_groups, ],
    multi=[cluster_actions_groups, ]
)

register(
    ["mysql_supported"],
    single=[common_groups,
            backup_incremental_groups,
            configuration_groups,
            database_actions_groups,
            instance_groups,
            instance_upgrade_groups,
            root_actions_groups,
            user_actions_groups, ],
    multi=[replication_promote_groups, ]
)

register(
    ["percona_supported"],
    single=[common_groups,
            backup_incremental_groups,
            configuration_groups,
            database_actions_groups,
            instance_upgrade_groups,
            root_actions_groups,
            user_actions_groups, ],
    multi=[replication_promote_groups, ]
)

register(
    ["postgresql_supported"],
    single=[common_groups,
            backup_incremental_groups,
            database_actions_groups,
            configuration_groups,
            root_actions_groups,
            user_actions_groups, ],
    multi=[replication_groups, ]
)

register(
    ["pxc_supported"],
    single=[common_groups,
            backup_incremental_groups,
            configuration_groups,
            database_actions_groups,
            root_actions_groups,
            user_actions_groups, ],
    multi=[]
    # multi=[cluster_actions_groups,
    #        cluster_negative_actions_groups,
    #        cluster_root_actions_groups, ]
)

register(
    ["redis_supported"],
    single=[common_groups,
            backup_groups,
            configuration_groups, ],
    multi=[
        # cluster_actions_groups,
        # cluster_negative_actions_groups,
        replication_promote_groups, ]
)

register(
    ["vertica_supported"],
    single=[common_groups,
            configuration_groups,
            root_actions_groups, ],
    multi=[cluster_actions_groups,
           cluster_negative_actions_groups,
           cluster_root_actions_groups, ]
)

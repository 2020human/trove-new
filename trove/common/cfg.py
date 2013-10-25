# vim: tabstop=4 shiftwidth=4 softtabstop=4

# Copyright 2011 OpenStack Foundation
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
"""Routines for configuring Trove."""

from oslo.config import cfg
import os.path

UNKNOWN_SERVICE_ID = 'unknown-service-id-error'

path_opts = [
    cfg.StrOpt('pybasedir',
               default=os.path.abspath(os.path.join(os.path.dirname(__file__),
                                                    '../')),
               help='Directory where the trove python module is installed'),
]

common_opts = [
    cfg.StrOpt('sql_connection',
               default='sqlite:///trove_test.sqlite',
               help='SQL Connection',
               secret=True),
    cfg.IntOpt('sql_idle_timeout', default=3600),
    cfg.BoolOpt('sql_query_log', default=False),
    cfg.IntOpt('bind_port', default=8779),
    cfg.StrOpt('api_extensions_path', default='trove/extensions/routes',
               help='Path to extensions'),
    cfg.StrOpt('api_paste_config',
               default="api-paste.ini",
               help='File name for the paste.deploy config for trove-api'),
    cfg.BoolOpt('add_addresses',
                default=False,
                help='Whether to add IP addresses to the list operations'),
    cfg.BoolOpt('trove_volume_support',
                default=True,
                help='File name for the paste.deploy config for trove-api'),
    cfg.ListOpt('admin_roles', default=['admin']),
    cfg.BoolOpt('update_status_on_fail', default=False,
                help='If instance failed to become active, '
                     'taskmanager updates statuses, '
                     'service status = FAILED_TIMEOUT_GUESTAGENT, '
                     'instance task status = BUILDING_ERROR_TIMEOUT_GA'),
    cfg.StrOpt('nova_compute_url', default='http://localhost:8774/v2'),
    cfg.StrOpt('cinder_url', default='http://localhost:8776/v2'),
    cfg.StrOpt('heat_url', default='http://localhost:8004/v1'),
    cfg.StrOpt('swift_url', default='http://localhost:8080/v1/AUTH_'),
    cfg.StrOpt('trove_auth_url', default='http://0.0.0.0:5000/v2.0'),
    cfg.StrOpt('host', default='0.0.0.0'),
    cfg.IntOpt('report_interval', default=10,
               help='The interval in seconds which periodic tasks are run'),
    cfg.IntOpt('periodic_interval', default=60),
    cfg.BoolOpt('trove_dns_support', default=False),
    cfg.StrOpt('db_api_implementation', default='trove.db.sqlalchemy.api'),
    cfg.StrOpt('mysql_pkg', default='mysql-server-5.5'),
    cfg.StrOpt('percona_pkg', default='percona-server-server-5.5'),
    cfg.StrOpt('dns_driver', default='trove.dns.driver.DnsDriver'),
    cfg.StrOpt('dns_instance_entry_factory',
               default='trove.dns.driver.DnsInstanceEntryFactory'),
    cfg.StrOpt('dns_hostname', default=""),
    cfg.IntOpt('dns_account_id', default=0),
    cfg.StrOpt('dns_auth_url', default=""),
    cfg.StrOpt('dns_domain_name', default=""),
    cfg.StrOpt('dns_username', default="", secret=True),
    cfg.StrOpt('dns_passkey', default="", secret=True),
    cfg.StrOpt('dns_management_base_url', default=""),
    cfg.IntOpt('dns_ttl', default=300),
    cfg.IntOpt('dns_domain_id', default=1),
    cfg.IntOpt('users_page_size', default=20),
    cfg.IntOpt('databases_page_size', default=20),
    cfg.IntOpt('instances_page_size', default=20),
    cfg.ListOpt('ignore_users', default=['os_admin', 'root']),
    cfg.ListOpt('ignore_dbs', default=['lost+found',
                                       'mysql',
                                       'information_schema']),
    cfg.IntOpt('agent_call_low_timeout', default=5),
    cfg.IntOpt('agent_call_high_timeout', default=60),
    cfg.StrOpt('guest_id', default=None),
    cfg.IntOpt('state_change_wait_time', default=3 * 60),
    cfg.IntOpt('agent_heartbeat_time', default=10),
    cfg.IntOpt('num_tries', default=3),
    cfg.StrOpt('volume_fstype', default='ext3'),
    cfg.StrOpt('format_options', default='-m 5'),
    cfg.IntOpt('volume_format_timeout', default=120),
    cfg.StrOpt('mount_options', default='defaults,noatime'),
    cfg.IntOpt('max_instances_per_user', default=5,
               help='default maximum number of instances per tenant'),
    cfg.IntOpt('max_accepted_volume_size', default=5,
               help='default maximum volume size for an instance'),
    cfg.IntOpt('max_volumes_per_user', default=20,
               help='default maximum for total volume used by a tenant'),
    cfg.IntOpt('max_backups_per_user', default=5,
               help='default maximum number of backups created by a tenant'),
    cfg.StrOpt('quota_driver',
               default='trove.quota.quota.DbQuotaDriver',
               help='default driver to use for quota checks'),
    cfg.StrOpt('taskmanager_queue', default='taskmanager'),
    cfg.BoolOpt('use_nova_server_volume', default=False),
    cfg.BoolOpt('use_heat', default=False),
    cfg.StrOpt('device_path', default='/dev/vdb'),
    cfg.StrOpt('mount_point', default='/var/lib/mysql'),
    cfg.StrOpt('service_type', default='mysql'),
    cfg.StrOpt('block_device_mapping', default='vdb'),
    cfg.IntOpt('server_delete_time_out', default=60),
    cfg.IntOpt('volume_time_out', default=60),
    cfg.IntOpt('heat_time_out', default=60),
    cfg.IntOpt('reboot_time_out', default=60 * 2),
    cfg.StrOpt('service_options', default=['mysql']),
    cfg.IntOpt('dns_time_out', default=60 * 2),
    cfg.IntOpt('resize_time_out', default=60 * 10),
    cfg.IntOpt('revert_time_out', default=60 * 10),
    cfg.BoolOpt('root_on_create', default=False,
                help='Enable the automatic creation of the root user for the '
                ' service during instance-create. The generated password for '
                ' the root user is immediately returned in the response of '
                " instance-create as the 'password' field."),
    cfg.ListOpt('root_grant', default=['ALL']),
    cfg.BoolOpt('root_grant_option', default=True),
    cfg.IntOpt('http_get_rate', default=200),
    cfg.IntOpt('http_post_rate', default=200),
    cfg.IntOpt('http_delete_rate', default=200),
    cfg.IntOpt('http_put_rate', default=200),
    cfg.BoolOpt('hostname_require_ipv4', default=True,
                help="Require user hostnames to be IPv4 addresses."),
    cfg.BoolOpt('trove_security_groups_support', default=True),
    cfg.BoolOpt('trove_security_groups_rules_support', default=True),
    cfg.StrOpt('trove_security_group_name_prefix', default='SecGroup'),
    cfg.StrOpt('trove_security_group_rule_protocol', default='tcp'),
    cfg.IntOpt('trove_security_group_rule_port', default=3306),
    cfg.StrOpt('trove_security_group_rule_cidr', default='0.0.0.0/0'),
    cfg.IntOpt('trove_api_workers', default=None),
    cfg.IntOpt('usage_sleep_time', default=1,
               help='Time to sleep during the check active guest'),
    cfg.IntOpt('usage_timeout', default=300,
               help='Timeout to wait for an guest to become active'),
    cfg.StrOpt('region', default='LOCAL_DEV',
               help='The region this service is located.'),
    cfg.StrOpt('backup_runner',
               default='trove.guestagent.backup.backup_types.InnoBackupEx'),
    cfg.StrOpt('backup_strategy', default='InnoBackupEx',
               help='Default strategy to perform backups'),
    cfg.StrOpt('backup_namespace',
               default='trove.guestagent.strategies.backup.mysql_impl',
               help='Namespace to load backup strategies from'),
    cfg.StrOpt('restore_namespace',
               default='trove.guestagent.strategies.restore.mysql_impl',
               help='Namespace to load restore strategies from'),
    cfg.BoolOpt('verify_swift_checksum_on_restore', default=True,
                help='Enable verification of swift checksum before starting '
                ' restore; makes sure the checksum of original backup matches '
                ' checksum of the swift backup file.'),
    cfg.StrOpt('storage_strategy', default='SwiftStorage',
               help="Default strategy to store backups"),
    cfg.StrOpt('storage_namespace',
               default='trove.guestagent.strategies.storage.swift',
               help='Namespace to load the default storage strategy from'),
    cfg.StrOpt('backup_swift_container', default='database_backups'),
    cfg.BoolOpt('backup_use_gzip_compression', default=True,
                help='Compress backups using gzip.'),
    cfg.BoolOpt('backup_use_openssl_encryption', default=True,
                help='Encrypt backups using openssl.'),
    cfg.StrOpt('backup_aes_cbc_key', default='default_aes_cbc_key',
               help='default openssl aes_cbc key.'),
    cfg.BoolOpt('backup_use_snet', default=False,
                help='Send backup files over snet.'),
    cfg.IntOpt('backup_chunk_size', default=2 ** 16,
               help='Chunk size to stream to swift container'),
    cfg.IntOpt('backup_segment_max_size', default=2 * (1024 ** 3),
               help="Maximum size of each segment of the backup file."),
    cfg.StrOpt('remote_dns_client',
               default='trove.common.remote.dns_client'),
    cfg.StrOpt('remote_guest_client',
               default='trove.common.remote.guest_client'),
    cfg.StrOpt('remote_nova_client',
               default='trove.common.remote.nova_client'),
    cfg.StrOpt('remote_cinder_client',
               default='trove.common.remote.cinder_client'),
    cfg.StrOpt('remote_heat_client',
               default='trove.common.remote.heat_client'),
    cfg.StrOpt('remote_swift_client',
               default='trove.common.remote.swift_client'),
    cfg.StrOpt('exists_notification_transformer',
               help='Transformer for exists notifications'),
    cfg.IntOpt('exists_notification_ticks', default=360,
               help='Number of report_intevals to wait between pushing events '
                    '(see report_interval)'),
    cfg.DictOpt('notification_service_id', default={},
                help='Unique ID to tag notification events'),
    cfg.StrOpt('nova_proxy_admin_user', default='',
               help="Admin username used to connect to Nova", secret=True),
    cfg.StrOpt('nova_proxy_admin_pass', default='',
               help="Admin password used to connect to Nova", secret=True),
    cfg.StrOpt('nova_proxy_admin_tenant_name', default='',
               help="Admin tenant used to connect to Nova", secret=True),
    cfg.StrOpt('network_label_regex', default='^private$'),
    cfg.StrOpt('cloudinit_location', default='/etc/trove/cloudinit',
               help="Path to folder with cloudinit scripts"),
    cfg.StrOpt('guest_config',
               default='$pybasedir/etc/trove/trove-guestagent.conf.sample',
               help="Path to guestagent config file"),
    cfg.DictOpt('service_registry_ext', default=dict(),
                help='Extention for default service managers.'
                     ' Allows to use custom managers for each of'
                     ' service type supported in trove'),
]

CONF = cfg.CONF
CONF.register_opts(path_opts)
CONF.register_opts(common_opts)


def custom_parser(parsername, parser):
    CONF.register_cli_opt(cfg.SubCommandOpt(parsername, handler=parser))


def parse_args(argv, default_config_files=None):
    cfg.CONF(args=argv[1:],
             project='trove',
             default_config_files=default_config_files)

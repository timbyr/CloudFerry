# Copyright (c) 2014 Mirantis Inc.
#
# Licensed under the Apache License, Version 2.0 (the License);
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an AS IS BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and#
# limitations under the License.

import json
import os

from novaclient import client
from novaclient.exceptions import NotFound

from cloudferrylib.utils import utils
import cfglib

LOG = utils.get_log(__name__)


def get_nova_info(conf):
    """Returns information about flavors, VMs, server groups and host
    aggregates in the source cloud.

    Return format:
    ({
        <VM ID>: {
            "id": <VM ID>,
            "flavor": <VM flavor>,
            "host": <host VM is running on>,
        }
    },
    {
        <flavor ID>: {
            "fl_id": <flavor ID>,
            "core": <number of cores for flavor>,
            "name": <flavor name>,
            "ram": <amount of RAM required for flavor>,
            "ephemeral": <amount of ephemeral storage required for flavor>,
            "swap": <swap space needed for flavor>,
            "metadata": {key=value, ...}
        }
    },
    {
        <hostname>: {
            'core': <number of cores/CPUs>,
            'ram': <amount of RAM>,
            'core_ratio': <CPU allocation ratio>,
            'ram_ratio': <RAM allocation ratio>,
        }
    },
    {
        <group ID>: {
            "id: <group ID>,
            "name": <group name>
            "policies": [<policy>, ...],
            "members": [member, ...],
            "metadata": {key=value, ...}
        }
    },
    {
        <aggregate ID>: {
            "id": <aggregate ID>,
            "name": <aggregate name>,
            "hosts": [<host>, ...],
            "az": <availability zone>,
            "metadata": {key=value, ...}
        }
    })"""

    src = conf['src']
    username = src['user']
    password = src['password']
    tenant = src['tenant']
    auth_url = src['auth_url']

    cli = client.Client(2, username, password, tenant, auth_url)

    flavors = {
        i.id: {
            "fl_id": i.id,
            "core": i.vcpus,
            "name": i.name,
            "ram": i.ram,
            "ephemeral": i.ephemeral,
            "swap": i.swap,
            "metadata": i.get_keys()
        } for i in cli.flavors.list()
    }

    vms = {
        vm.id: {
            "id": vm.id,
            "flavor": vm.flavor.get("id"),
        } for vm in cli.servers.list(search_opts={"all_tenants": True})

    }

    hypervisors = {
        hypervisor.hypervisor_hostname: {
            'core': hypervisor.vcpus,
            'ram': hypervisor.memory_mb,
        } for hypervisor in cli.hypervisors.list()
    }

    aggregates = {
        agg.id: {
            "id": agg.id,
            "name": agg.name,
            "hosts": agg.hosts,
            "az": agg.availability_zone,
            "metadata": agg.metadata
        } for agg in cli.aggregates.list()
    }

    try:
        groups = {
            group.id: {
                "id": group.id,
                "name": group.name,
                "policies": group.policies,
                "members": group.members,
                "metadata": group.metadata
            } for group in cli.server_groups.list()
        }
    except NotFound:
        # When running against an Openstack deployment that doesn't support
        # server groups a NotFound exception will be raised. In this case just
        # return an empty group dictionary
        groups = {}

    return flavors, vms, hypervisors, groups, aggregates


def store_nova_data(flavors, vms, nodes, groups, aggregates):
    files = {
        cfglib.CONF.collect.flavors_file: flavors,
        cfglib.CONF.collect.vms_file: vms,
        cfglib.CONF.collect.nodes_file: nodes,
        cfglib.CONF.collect.server_groups_file: groups,
        cfglib.CONF.collect.aggregates_file: aggregates
    }
    for f in files:
        if not os.path.exists(os.path.dirname(f)):
            os.makedirs(os.path.dirname(f))
        with open(f, 'w') as store:
            store.write(json.dumps(files[f]))


def collect(conf):
    """
    Collects nova information from source cloud and stores it in configured
    files.
    """
    store_nova_data(
        *get_nova_info(conf))

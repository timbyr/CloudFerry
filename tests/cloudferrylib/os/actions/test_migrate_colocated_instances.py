# Copyright 2015: Mirantis Inc.
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
# import exceptions

import mock

from tests import test
from cloudferrylib.os.actions import migrate_colocated_instances


class CheckInstanceNetworksTestCase(test.TestCase):

    @staticmethod
    def get_action(instances, server_groups):
        instance_info = {'instances': {}}
        fake_src_compute = mock.Mock()
        fake_src_compute.read_info.return_value = instance_info
        fake_src_cloud = mock.Mock()
        fake_src_cloud.resources = {'compute': fake_src_compute}
        fake_init = {
            'src_cloud': fake_src_cloud,
            'cfg': {}
        }
        return migrate_colocated_instances.MigrateColocatedInstances(
            fake_init,
            )

    def test_all_empty(self):
        action = self.get_action({}, [])
        action.run({}, [])

    def test_same_host(self):
        action = self.get_action({}, {})
        info = {
            'instances': {
                u'ac703099-f4e5-44f5-a485-0052d0d37a65': {
                    'instance': {
                        'status': u'ACTIVE',
                        'host': u'host1',
                        'id': u'ac703099-f4e5-44f5-a485-0052d0d37a65',
                        'old_id': u'c12b8a1e-6cd0-4203-a246-099f39bc4d4d'
                        }},
                u'ac703099-f4e5-44f5-a485-0052d0d37a66': {
                    'instance': {
                        'status': u'ACTIVE',
                        'host': u'host2',
                        'id': u'ac703099-f4e5-44f5-a485-0052d0d37a66',
                        'old_id': u'c12b8a1e-6cd0-4203-a246-099f39bc4d4e'
                        }},
            }}
        group_info = [
            {'name': u'testgroup',
             'members': [u'98c7cbd7-26c2-49bd-bd0d-09f03df7affb'],
             'user': u'admin',
             'policies': [u'anti-affinity'],
             'tenant': u'admin',
             'uuid': u'b9c1c92f-b75e-46fd-9e62-97a167ff3388'}]
        action.run(info=info, server_group_info=group_info)

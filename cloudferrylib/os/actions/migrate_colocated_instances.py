# Copyright (c) 2015 Mirantis Inc.
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


from cloudferrylib.base.action import action
from cloudferrylib.os.compute.server_groups import Handler
from cloudferrylib.utils import utils as utl

LOG = utl.get_log(__name__)


class MigrateColocatedInstances(action.Action):

    def run(self, info=None, server_group_info=None, **kwargs):
        dst_resource = Handler(self.dst_cloud)

        dst_resource.update_server_group_members(info, server_group_info)

        colocated_instances = dst_resource.get_colocated_instances()
        if len(colocated_instances) > 0:
            try:
                dst_resource.migrate(colocated_instances)
            except Exception as e:
                LOG.error(e)
        else:
            LOG.debug("All server groups found on the source cloud")
        return {}

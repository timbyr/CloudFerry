from tests import test

import mock

from novaclient.exceptions import NotFound

from collection.nova import get_nova_info
import cfglib


class CollectTest(test.TestCase):

    def setUp(self):
        super(test.TestCase, self).setUp()
        cfglib.init_config("")
        novaclient = mock.patch('collection.nova.client').start()
        client = mock.Mock()
        client.flavors.list.return_value = []
        client.servers.list.return_value = []
        client.hypervisors.list.return_value = []
        client.aggregates.list.return_value = []
        client.server_groups.list.return_value = []
        novaclient.Client.return_value = client
        self.client = client

    def test_flavor(self):
        flavor = mock.Mock()
        flavor.configure_mock(id=1,
                              vcpus=1,
                              name="test",
                              ram=512,
                              ephemeral=0,
                              swap=0)
        flavor.get_keys.return_value = {"aggregate_extra_specs:ssd": True}
        self.client.flavors.list.return_value = [flavor]
        f, _, _, _, _ = get_nova_info(cfglib.CONF)

        self.assertEqual(self.client.flavors.list.call_count, 1)
        self.assertEqual({1: {"fl_id": 1,
                              "core": 1,
                              "name": "test",
                              "ram": 512,
                              "ephemeral": 0,
                              "swap": 0,
                              "metadata": {"aggregate_extra_specs:ssd":
                                           True}}
                          },
                         f)

    def test_servers(self):
        server = mock.Mock()
        server.configure_mock(id=1)
        server.flavor.get.return_value = "1"

        self.client.servers.list.return_value = [server]
        _, s, _, _, _ = get_nova_info(cfglib.CONF)

        self.assertEqual(self.client.servers.list.call_count, 1)
        self.assertEqual({1: {"id": 1,
                              "flavor": "1"}
                          },
                         s)

    def test_hosts(self):
        host = mock.Mock()
        host.configure_mock(hypervisor_hostname="test",
                            vcpus=1,
                            memory_mb=2048)
        self.client.hypervisors.list.return_value = [host]
        _, _, h, _, _ = get_nova_info(cfglib.CONF)

        self.assertEqual(self.client.hypervisors.list.call_count, 1)
        self.assertEqual({"test": {"core": 1,
                                   "ram": 2048}
                          },
                         h)

    def test_aggregates(self):
        aggregate = mock.Mock()
        aggregate.configure_mock(id=1,
                                 name="test",
                                 hosts=["test"],
                                 availability_zone="az",
                                 metadata={"key": "value"})

        self.client.aggregates.list.return_value = [aggregate]
        _, _, _, _, a = get_nova_info(cfglib.CONF)

        self.assertEqual(self.client.aggregates.list.call_count, 1)
        self.assertEqual({1: {"id": 1,
                              "name": "test",
                              "hosts": ["test"],
                              "az": "az",
                              "metadata": {"key": "value"}
                              }
                          },
                         a)

    def test_groups(self):
        server_group = mock.Mock()
        server_group.configure_mock(
            id=1,
            name="test",
            policies=["anti-affinity"],
            members=["test"],
            metadata={"key": "value"}
        )

        self.client.server_groups.list.return_value = [server_group]
        _, _, _, g, _ = get_nova_info(cfglib.CONF)

        self.assertEqual(self.client.server_groups.list.call_count, 1)
        self.assertEqual({1: {"id": 1,
                              "name": "test",
                              "policies": ["anti-affinity"],
                              "members": ["test"],
                              "metadata": {"key": "value"}
                              }
                          },
                         g)

    def test_groups_grizzly(self):
        def notsupported():
            raise NotFound(404)

        self.client.server_groups.list.side_effect = notsupported
        _, _, _, g, _ = get_nova_info(cfglib.CONF)

        self.assertEqual(self.client.server_groups.list.call_count, 1)
        self.assertEqual({}, g)

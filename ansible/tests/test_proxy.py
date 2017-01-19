import testinfra.utils.ansible_runner
import pytest

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    '.molecule/ansible_inventory').get_hosts('omero-hosts')


def test_services_running_and_enabled(Service):
    service = Service("nginx")
    assert service.is_running
    assert service.is_enabled


# @pytest.mark.parametrize("port", [80, 443, 9000])
@pytest.mark.parametrize("port", [80])
def test_omero_port_listening(Socket, port):
    assert Socket("tcp://0.0.0.0:%d" % port).is_listening

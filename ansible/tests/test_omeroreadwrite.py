import testinfra.utils.ansible_runner
import pytest

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    '.molecule/ansible_inventory').get_hosts('omeroreadwrite-hosts')


@pytest.mark.parametrize("name", ["omero-server", "omero-web", "nginx"])
def test_services_running_and_enabled(Service, name):
    service = Service(name)
    assert service.is_running
    assert service.is_enabled


def test_nginx_port_listening(Socket):
    assert Socket("tcp://0.0.0.0:80").is_listening


@pytest.mark.parametrize("port", [4063, 4064])
def test_omero_port_listening(Socket, port):
    # For some reason OMERO may listen on ipv6 instead of ipv4
    assert (Socket("tcp://127.0.0.1:%d" % port).is_listening or
            Socket("tcp://::1%d" % port).is_listening)


def test_registry_port_listening(Socket):
    assert Socket("tcp://127.0.0.1:4061").is_listening

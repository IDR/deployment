import testinfra.utils.ansible_runner
import pytest
import os

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    '.molecule/ansible_inventory').get_hosts('omeroreadonly-hosts')


@pytest.mark.skipif(os.getenv('TRAVIS') == 'true',
                    reason="Disabled on travis: insufficient resources")
@pytest.mark.parametrize("name", ["omero-server", "omero-web", "nginx"])
def test_services_running_and_enabled(Service, name):
    service = Service(name)
    assert service.is_running
    assert service.is_enabled


@pytest.mark.skipif(os.getenv('TRAVIS') == 'true',
                    reason="Disabled on travis: insufficient resources")
def test_nginx_port_listening(Socket):
    assert Socket("tcp://0.0.0.0:80").is_listening


@pytest.mark.skipif(os.getenv('TRAVIS') == 'true',
                    reason="Disabled on travis: insufficient resources")
@pytest.mark.parametrize("port", [4063, 4064])
def test_omero_port_listening(Socket, port):
    # For some reason OMERO may listen on ipv6 instead of ipv4
    assert (Socket("tcp://0.0.0.0:%d" % port).is_listening or
            Socket("tcp://:::%d" % port).is_listening)


@pytest.mark.skipif(os.getenv('TRAVIS') == 'true',
                    reason="Disabled on travis: insufficient resources")
def test_registry_port_listening(Socket):
    assert Socket("tcp://127.0.0.1:4061").is_listening

import os
import testinfra.utils.ansible_runner
import pytest

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']).get_hosts('omeroreadonly-hosts')


@pytest.mark.skipif(os.getenv('TRAVIS') == 'true',
                    reason="Disabled on travis: insufficient resources")
@pytest.mark.parametrize("name", ["omero-server", "omero-web", "nginx"])
def test_services_running_and_enabled(host, name):
    service = host.service(name)
    assert service.is_running
    assert service.is_enabled


@pytest.mark.skipif(os.getenv('TRAVIS') == 'true',
                    reason="Disabled on travis: insufficient resources")
def test_nginx_port_listening(host):
    assert host.socket("tcp://0.0.0.0:80").is_listening


@pytest.mark.skipif(os.getenv('TRAVIS') == 'true',
                    reason="Disabled on travis: insufficient resources")
@pytest.mark.parametrize("port", [4063, 4064])
def test_omero_port_listening(host, port):
    # For some reason OMERO may listen on ipv6 instead of ipv4
    assert (host.socket("tcp://0.0.0.0:%d" % port).is_listening or
            host.socket("tcp://:::%d" % port).is_listening)


@pytest.mark.skipif(os.getenv('TRAVIS') == 'true',
                    reason="Disabled on travis: insufficient resources")
def test_registry_port_listening(host):
    assert host.socket("tcp://127.0.0.1:4061").is_listening

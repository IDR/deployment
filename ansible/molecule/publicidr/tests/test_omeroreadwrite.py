import os
import testinfra.utils.ansible_runner
import pytest

# TODO: This should be 'omero-hosts' but since read-only can't be tested on
# Travis there are separate files:
# - test_omeroreadwrite.py
# - test_omeroreadonly.py
testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']).get_hosts('omeroreadwrite-hosts')


@pytest.mark.parametrize("name", ["omero-server", "omero-web", "nginx"])
def test_services_running_and_enabled(host, name):
    service = host.service(name)
    assert service.is_running
    assert service.is_enabled


def test_nginx_port_listening(host):
    assert host.socket("tcp://0.0.0.0:80").is_listening


@pytest.mark.parametrize("port", [4063, 4064])
def test_omero_port_listening(host, port):
    # For some reason OMERO may listen on ipv6 instead of ipv4
    assert (host.socket("tcp://0.0.0.0:%d" % port).is_listening or
            host.socket("tcp://:::%d" % port).is_listening)


def test_registry_port_listening(host):
    assert host.socket("tcp://127.0.0.1:4061").is_listening

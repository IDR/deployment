import os
import testinfra.utils.ansible_runner
import pytest

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']).get_hosts('proxy-hosts')


def test_services_running_and_enabled(host):
    service = host.service("nginx")
    assert service.is_running
    assert service.is_enabled


@pytest.mark.parametrize("port", [80, 443, 9000])
def test_omero_port_listening(host, port):
    assert host.socket("tcp://0.0.0.0:%d" % port).is_listening


@pytest.mark.parametrize("address", [
    "http://localhost/",
    "https://localhost/",
])
def test_html_index(host, address):
    out = host.check_output('curl -kL %s' % address)
    assert '<title>IDR: Image Data Resource</title>' in out

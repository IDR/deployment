import testinfra.utils.ansible_runner
import pytest

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    '.molecule/ansible_inventory').get_hosts('all')


@pytest.mark.parametrize('name', [
    'docker'
    'kubelet'
])
def test_service_running_and_enabled(Service, name):
    service = Service(name)
    assert service.is_running
    assert service.is_enabled

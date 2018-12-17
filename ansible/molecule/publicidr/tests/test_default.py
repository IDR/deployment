import os
import testinfra.utils.ansible_runner

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']).get_hosts('all')


# def test_services_running_and_enabled(Service):
#     service = Service('sshd')
#     assert service.is_running
#     assert service.is_enabled
#
#
# def test_ssh_port_listening(Socket):
#     assert Socket("tcp://0.0.0.0:22").is_listening

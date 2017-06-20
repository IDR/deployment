import testinfra.utils.ansible_runner
from re import match

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    '.molecule/ansible_inventory').get_hosts('kubernetes-master')


def test_get_nodes(Command, Sudo):
    with Sudo():
        out = Command.check_output(
            'kubectl --kubeconfig /etc/kubernetes/admin.conf get nodes')

    # First line contains column headings
    lines = sorted(out.strip().split('\n')[1:])
    assert len(lines) == 2
    assert match('kubernetes-master\s+Ready\s+', lines[0])
    assert match('kubernetes-worker\s+Ready\s+', lines[1])

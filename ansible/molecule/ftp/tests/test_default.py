import os
import pytest
import testinfra.utils.ansible_runner

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']).get_hosts('all')


@pytest.mark.parametrize("port", [
    32021,
    32022,
    32221,
])
def test_listening(host, port):
    out = host.check_output('ss --numeric --listening --tcp')
    print(out)
    assert (host.socket(f"tcp://0.0.0.0:{port}").is_listening or
            host.socket(f"tcp://:::{port}").is_listening)


def test_upload(host):
    expected = '/data/idrftp-incoming/upload_test.sh'
    host.check_output('rm -f %s' % expected)
    out = host.check_output('/upload_test.sh')

    f = host.file(expected)
    # If this test fails it's probably due to a failure in upload_test.sh.
    # An FTP error in that script doesn't exit with an error code
    assert f.exists
    assert f.content_string.endswith('# IDR FTP molecule test script')
    assert out == ''

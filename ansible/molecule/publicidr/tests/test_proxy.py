import os
import re
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


@pytest.mark.parametrize("curl_args,expected_header", [
    ("http://localhost/api/v0/",
     "Access-Control-Allow-Origin: *"),
    ("-H 'Origin: http://example.org' http://localhost/api/v0/",
     "Access-Control-Allow-Origin: *"),
    ("-H 'Origin: http://example.com' http://localhost/api/v0/",
     "Access-Control-Allow-Origin: *"),
])
def test_curl_headers(host, curl_args, expected_header):
    out = host.check_output('curl -I %s' % curl_args)
    assert expected_header in out.splitlines()


@pytest.mark.parametrize("path", [
    "/api/v0/",
    "/static/webgateway/img/ome.ico",
])
def test_is_cached(host, path):
    # Request twice to ensure it's cached.
    # Can't use check_output because it attempts to decode result
    r = host.run('curl -sSf http://localhost%s' % path)
    assert r.rc == 0
    assert len(r.stdout_bytes) > 500
    r = host.run('curl -sSf http://localhost%s' % path)
    assert r.rc == 0
    assert len(r.stdout_bytes) > 500
    log = host.file("/var/log/nginx/access.log").content.decode()
    assert re.search('"GET %s HTTP/1.1" 200 .+ HIT -' % path, log)

import os
import testinfra.utils.ansible_runner

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']).get_hosts('database-hosts')


def test_services_running_and_enabled(host):
    service = host.service('postgresql-11')
    assert service.is_running
    assert service.is_enabled


def test_postgres_port_listening(host):
    assert host.socket("tcp://0.0.0.0:5432").is_listening


def test_omero_database_created(host):
    psql = ("PGPASSWORD=omero psql -Uomero -hlocalhost idr -Atc "
            "'SELECT currentpatch,currentversion FROM dbpatch "
            "ORDER BY id DESC LIMIT 1;'")
    out = host.check_output('bash -c %s', psql)
    assert '0|OMERO5.4' == out

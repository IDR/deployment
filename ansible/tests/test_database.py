import testinfra.utils.ansible_runner

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    '.molecule/ansible_inventory').get_hosts('database-hosts')


def test_services_running_and_enabled(Service):
    service = Service('postgresql-9.6')
    assert service.is_running
    assert service.is_enabled


def test_postgres_port_listening(Socket):
    assert Socket("tcp://0.0.0.0:5432").is_listening


def test_omero_database_created(Command):
    psql = ("PGPASSWORD=omero psql -Uomero -hlocalhost idr -Atc "
            "'SELECT currentpatch,currentversion FROM dbpatch "
            "ORDER BY id DESC LIMIT 1;'")
    out = Command.check_output('bash -c %s', psql)
    assert '0|OMERO5.4' == out

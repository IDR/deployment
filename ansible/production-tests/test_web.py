# Smoke tests for the production IDR OMERO.web
# These assume an existing IDR database
#
# Test the default host:
#   pytest production-tests/
#
# Test a different host:
#   HOST=http://idr-testing.openmicroscopy.org pytest production-tests/

import json
import os
import pytest
import requests
import time


HOST = os.getenv('HOST', 'https://idr.openmicroscopy.org')


@pytest.mark.parametrize('uri,expect', [

    ('/about', '/about/'),
])
def test_about_redirect(uri, expect):
    r = requests.head('%s%s' % (HOST, uri))
    assert r.is_redirect
    assert r.headers['Location'] == '%s%s' % (HOST, expect)


@pytest.mark.parametrize('uri,expect', [
    ('', 'The Image Data Resource (IDR) is a public repository'),
    ('/about/', 'The IDR makes datasets that have never previously been'),
    ('/about/experiments.html', 'When submitting data to the IDR, you'),
])
def test_about_get(uri, expect):
    r = requests.get('%s%s' % (HOST, uri))
    assert r.status_code == 200
    assert expect in r.text


def test_mapr_organism_count():
    uri = '/mapr/api/organism/count/'
    r = requests.get('%s%s' % (HOST, uri))
    assert r.status_code == 200
    j = json.loads(r.text)
    assert j['experimenter']['childCount'] >= 6


def test_get_image_nocache():
    # Use a dummy query param to break cache
    uri = '/webclient/render_image/2850181/10/0/?dummy=%d' % int(time.time())
    r = requests.get('%s%s' % (HOST, uri))
    assert r.status_code == 200
    assert r.headers['Content-Type'] == 'image/jpeg'
    assert len(r.content) > 50000
    assert r.content[:2] == b'\xff\xd8'

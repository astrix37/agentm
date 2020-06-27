import flaskr
import os
import pytest
import tempfile

KEY = 'abc'

@pytest.fixture
def client():
    os.environ['KEY'] = KEY
    app = flaskr.create_app()
    db_fd, app.config['DATABASE'] = tempfile.mkstemp()
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


def test_home_page(client):
    rv = client.get('/')
    unwelcome_message = 'Oh, what are you doing here? Have you considered going away? '
    assert unwelcome_message in str(rv.data)


def test_no_auth_gives_unauthorized(client):
    expected_status = 401
    endpoints = ['create_backup', 'get_admins', 'get_file', 'get_log', 'get_properties', 'list_files', 'install_mod',
                 'delete_file', 'list_mods', 'list_logs', 'command', 'save_file']
    for endpoint in endpoints:
        result = client.post('/{}/'.format(endpoint))
        assert expected_status == result.status_code


def test_install_mod_requires_file(client):
    expected_status = 400
    expected_message = "Missing form data 's3_mod'"
    result = client.post('/install_mod/', headers={"AUTH": KEY})
    assert expected_status == result.status_code
    assert expected_message in result.json['result']
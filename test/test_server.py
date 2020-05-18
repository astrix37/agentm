import tempfile
import pytest
import flaskr


@pytest.fixture
def client():
    app = flaskr.create_app(__name__)
    db_fd, app.config['DATABASE'] = tempfile.mkstemp()
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


def test_home_page(client):
    rv = client.get('/')
    unwelcome_message = 'Oh, what are you doing here? Have you considered going away? '
    assert unwelcome_message in str(rv.data)


def test_install_mod_requires_file(client):
    expected_status = 400
    expected_message = "Missing form data 'mod'"
    result = client.post('/install-mod/')
    assert expected_status == result.status_code
    assert expected_message in result.json['result']
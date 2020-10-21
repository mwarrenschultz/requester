from requester import Requester
import pytest


@pytest.fixture()
def get_requester_session():
    rsession = Requester()
    return rsession


@pytest.fixture()
def get_proxy_requester_session():
    rsession = Requester(use_proxy=True)
    return rsession


def test_proxy_requester_session(get_proxy_requester_session):
    rsession = get_proxy_requester_session
    r = rsession.get("http://bot.whatismyipaddress.com")
    assert r.text == rsession.show_proxy()


def test_requester_session(get_requester_session):
    rsession = get_requester_session
    r = rsession.get("https://en.wikipedia.org/w/api.php")
    assert r.status_code == 200

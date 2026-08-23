
from app.uptime_keeper.ping import message_maker
class TestMessageMaker:

    def test_success(self):
        assert message_maker(200) == \
            "Request successful. The service is operating normally."

    def test_redirect(self):
        assert message_maker(300) == \
            "The service responded with a redirect."

    def test_client_error(self):
        assert message_maker(400) == \
            "The server rejected the request due to a client-side error."

    def test_server_error(self):
        assert message_maker(500) == \
            "The server encountered an error while processing the request."

    def test_unexpected_status_code(self):
        assert message_maker(100) == \
            "The service returned an unexpected HTTP status code."
"""
Tests for TwitterClient.post_tweet connection-failure retries.

Only failures that happen before the request reaches X (TCP connect, DNS,
TLS handshake) may be retried; anything after the request is sent must be
raised immediately so a tweet is never posted twice.
"""

import socket
import threading
from http.client import RemoteDisconnected
from unittest.mock import Mock, patch

import pytest
import requests
from urllib3.exceptions import ProtocolError

from mcp_servers import twitter_server
from mcp_servers.twitter_server import TwitterClient, _failed_before_send


def _real_handshake_failure() -> requests.exceptions.RequestException:
    """Produce a genuine requests exception from a server that drops the TLS handshake."""
    server = socket.socket()
    server.bind(('127.0.0.1', 0))
    server.listen(1)
    port = server.getsockname()[1]

    def accept_and_close():
        conn, _ = server.accept()
        conn.recv(1024)  # read the ClientHello, then hang up without answering
        conn.close()

    t = threading.Thread(target=accept_and_close, daemon=True)
    t.start()
    try:
        requests.post(f'https://127.0.0.1:{port}/2/tweets', json={}, timeout=5)
    except requests.exceptions.RequestException as e:
        return e
    finally:
        t.join(timeout=5)
        server.close()
    pytest.fail('expected the TLS handshake to fail')


def _real_connection_refused() -> requests.exceptions.RequestException:
    s = socket.socket()
    s.bind(('127.0.0.1', 0))
    port = s.getsockname()[1]
    s.close()  # nothing listens on this port now
    try:
        requests.post(f'https://127.0.0.1:{port}/2/tweets', json={}, timeout=5)
    except requests.exceptions.RequestException as e:
        return e
    pytest.fail('expected the connection to be refused')


class TestFailedBeforeSend:
    def test_tls_handshake_drop_is_pre_send(self):
        assert _failed_before_send(_real_handshake_failure()) is True

    def test_connection_refused_is_pre_send(self):
        assert _failed_before_send(_real_connection_refused()) is True

    def test_connect_timeout_is_pre_send(self):
        assert _failed_before_send(requests.exceptions.ConnectTimeout('x')) is True

    def test_disconnect_after_send_is_not_pre_send(self):
        err = requests.exceptions.ConnectionError(
            ProtocolError('Connection aborted.', RemoteDisconnected('closed'))
        )
        assert _failed_before_send(err) is False

    def test_read_timeout_is_not_pre_send(self):
        assert _failed_before_send(requests.exceptions.ReadTimeout('x')) is False


def _client_with(create_tweet: Mock) -> TwitterClient:
    client = TwitterClient('k', 's', 't', 'ts')
    client.client = Mock(create_tweet=create_tweet)
    return client


class TestPostTweetRetry:
    def test_retries_pre_send_failure_then_succeeds(self):
        handshake_err = _real_handshake_failure()
        create = Mock(side_effect=[handshake_err, Mock(data={'id': '123'})])
        with patch.object(twitter_server.time, 'sleep') as sleep:
            result = _client_with(create).post_tweet('hello')
        assert result['tweet_id'] == '123'
        assert create.call_count == 2
        sleep.assert_called_once()

    def test_gives_up_after_max_attempts(self):
        handshake_err = _real_handshake_failure()
        create = Mock(side_effect=handshake_err)
        with patch.object(twitter_server.time, 'sleep'):
            with pytest.raises(requests.exceptions.RequestException):
                _client_with(create).post_tweet('hello')
        assert create.call_count == twitter_server.POST_CONNECT_ATTEMPTS

    def test_post_send_failure_is_not_retried(self):
        err = requests.exceptions.ConnectionError(
            ProtocolError('Connection aborted.', RemoteDisconnected('closed'))
        )
        create = Mock(side_effect=err)
        with patch.object(twitter_server.time, 'sleep') as sleep:
            with pytest.raises(requests.exceptions.ConnectionError):
                _client_with(create).post_tweet('hello')
        assert create.call_count == 1
        sleep.assert_not_called()

    def test_http_403_is_not_retried(self):
        import tweepy
        response = Mock(status_code=403, reason='Forbidden', json=Mock(return_value={}))
        create = Mock(side_effect=tweepy.errors.Forbidden(response))
        with patch.object(twitter_server.time, 'sleep') as sleep:
            with pytest.raises(tweepy.errors.Forbidden):
                _client_with(create).post_tweet('hello')
        assert create.call_count == 1
        sleep.assert_not_called()

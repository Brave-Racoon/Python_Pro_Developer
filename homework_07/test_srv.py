# usage: pytest test_srv.py
# testing:
# sh ab -n 1000 -c 10 http://localhost:8080/index.html
# wrk -t12 -c400 -d30s http://localhost:8080/index.html

import pytest
import requests
import threading
import time

from web_srv import start_server, HOST, PORT, TEST_HOST, TEST_PORT


@pytest.fixture(scope='module')
def server():
    server_thread = threading.Thread(target=start_server)
    server_thread.start()
    time.sleep(1)  # give the server some time to start
    yield
    # no need to stop the server as pytest will terminate the process


def test_index_page(server):
    response = requests.get(f'http://{HOST}:{PORT}/')
    #response = requests.get(f'http://localhost:8080/')
    print(response)
    print(response.text)
    assert response.status_code == 200
    #print(response.links)
    #assert '!DOCTYPE html' in response.text
    assert 'index.html' in response.text


def test_not_found_page(server):
    response = requests.get(f'http://{HOST}:{PORT}/noexist_page.html')
    assert response.status_code == 404
    assert 'File Not Found' in response.text

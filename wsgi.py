import json
import socket
from json import JSONDecodeError


def main(ip="127.0.0.1", port=8000):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind((ip, port))
    sock.listen()

    running = True

    while running:
        connection, client_address = sock.accept()
        data = connection.recv(512)
        request = data.decode().split("\r\n")
        request_info = request[0].split(" ")
        method = request_info[0]
        endpoint = request_info[1][1:]
        try:
            request_body = json.loads(data.decode().split("\r\n\r\n")[1])
        except JSONDecodeError:
            request_body = {}
        response = router(method=method, endpoint=endpoint, body=request_body)
        connection.sendall(create_http_response(response[0], response[1]))

    connection.close()


def router(method: str, endpoint: str, body: json):
    if endpoint == "create_instance":
        return create_instance(method, body)
    return "", 404


def create_instance(method: str, body: json):
    if not check_method("POST", method):
        return "", 405
    return '{"task_id": 1}', 202


def check_method(target_method: str, method: str) -> bool:
    return target_method == method


def create_http_response(response_body: str, status_code: int):
    return f"HTTP/1.1 {status_code}\r\nContent-Type: application/json\r\nContent-Length: {len(response_body)}\r\n\r\n{response_body}".encode(
        "utf-8"
    )


if __name__ == "__main__":
    main(ip="localhost", port=8000)  # TODO: get by optional input params

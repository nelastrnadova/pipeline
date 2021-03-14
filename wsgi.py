import argparse
import json
import socket
from json import JSONDecodeError

from database import Database

parser = argparse.ArgumentParser()
parser.add_argument("-ip", type=str, help="Ip to run on", default="127.0.0.1")
parser.add_argument("-port", type=int, help="port to run on", default=8000)
parser.add_argument("-db", type=str, help="Path to db file", default="database.db")
args = parser.parse_args()

db = Database(args.db)


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
    if endpoint == "start_pipeline":
        return start_pipeline(method, body)
    elif endpoint == "get_pipeline_state":
        return get_pipeline_state(method, body)
    elif endpoint == "get_pipeline_outputs":
        return get_pipeline_outputs(method, body)
    return "", 404


def start_pipeline(method: str, body: json):
    if not check_method("POST", method):
        return "", 405
    if 'pipeline' not in body:
        return "", 400

    pipeline_master_id = db.single_select('pipelines_master', ['id'], ['name'], [body['pipeline']])[0]

    inputs = {}
    for input_master in db.select('pipeline_inputs_master', ['name', 'id'], ['pipeline_master_fk'], [pipeline_master_id]):
        if input_master[0] not in body:
            return '', 400
        inputs[input_master[0]] = {'pipeline_input_master_id': input_master[1], 'value': body[input_master[0]]}

    pipeline_id = db.insert('pipelines', ['pipeline_master_fk'], [pipeline_master_id])

    for pipeline_input in inputs:
        db.insert('pipeline_inputs', ['val', 'pipeline_fk', 'pipeline_input_master_fk'], [inputs[pipeline_input]['value'], pipeline_id, inputs[pipeline_input]['pipeline_input_master_id']])

    for component in db.select('components_master', ['id'], ['pipeline_master_fk'], [pipeline_master_id]):
        db.insert('components', ['pipeline_fk', 'component_master_fk'], [pipeline_id, component[0]])

    return json.dumps({'pipeline_id': pipeline_id}), 202


def get_pipeline_state(method: str, body: json):
    if not check_method("POST", method):
        return "", 405
    if 'pipeline_id' not in body:
        return "", 400

    state = db.single_select('pipelines', ['state'], ['id'], [body['pipeline_id']])[0]
    if state == 0:
        state = 'waiting'
    elif state == 1:
        state = 'running'
    elif state == 2:
        state = 'finished'
    elif state == 3:
        state = 'error/timeout'

    return json.dumps({'state': state}), 202


def get_pipeline_outputs(method: str, body: json):
    if not check_method("POST", method):
        return "", 405
    if 'pipeline_id' not in body:
        return "", 400

    pipline_outputs_val_master_output_fk = db.select('pipeline_outputs', ['val', 'pipeline_output_master_fk'], ['pipeline_fk'], [body['pipeline_id']])
    to_return = {}
    for val_pomfk in pipline_outputs_val_master_output_fk:
        val = val_pomfk[0]
        pipeline_output_master_fk = val_pomfk[1]
        name = db.single_select('pipeline_outputs_master', ['name'], ['id'], [pipeline_output_master_fk])[0]
        to_return[name] = val

    #  TODO:
    #  remove reference from pipelines, pipelines_inputs, pipeline_outputs,
    #  components, components_input, components_outputs

    return json.dumps(to_return), 202


def check_method(target_method: str, method: str) -> bool:
    return target_method == method


def create_http_response(response_body: str, status_code: int):
    return f"HTTP/1.1 {status_code}\r\nContent-Type: application/json\r\nContent-Length: {len(response_body)}\r\n\r\n{response_body}".encode(
        "utf-8"
    )


if __name__ == "__main__":
    main(ip=args.ip, port=args.port)

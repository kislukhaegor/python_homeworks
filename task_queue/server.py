
from uuid import uuid4
from enum import Enum
from time import time
import argparse
import asyncio
import os
import pickle

class ParserException(Exception):
    pass

class LengthException(Exception):
    pass

class Task:
    class State(Enum):
        INIT = 1,
        EXECUTING = 2

    def __init__(self, id_, data):
        self._id = id_
        self._data = data
        self._state = Task.State.INIT
        self._time = None

    @property
    def id(self):
        return self._id

    @property
    def state(self):
        return self._state

    @property
    def data(self):
        return self._data

    def run(self):
        self._state = Task.State.EXECUTING
        self._time = time()

    def update(self, timeout):
        if self._state == Task.State.EXECUTING and time() - self._time > timeout:
            self._state = Task.State.INIT


class Queue:
    def __init__(self, timeout):
        self._task_list = list()
        self._timeout = timeout

    def update_tasks(self):
        for task in self._task_list:
            task.update(self._timeout)

    def add_task(self, data):
        id_ = str(uuid4())
        self._task_list.append(Task(id_, data))
        return id_

    def get_task(self):
        self.update_tasks()
        for task in self._task_list:
            if task.state == Task.State.INIT:
                task.run()
                return (task.id, len(task.data), task.data)
        return None

    def ack_task(self, id_):
        self.update_tasks()
        for index, task in enumerate(self._task_list):
            if task.state == Task.State.EXECUTING and task.id == id_:
                del self._task_list[index]
                return True
        return False

    def in_task(self, id_):
        for task in self._task_list:
            if task.id == id_:
                return True
        return False


class QueueStorage:
    def __init__(self):
        self._queue = dict()
        self._timeout = 0

    def add_task(self, queue_name, data):
        if queue_name not in self._queue:
            self._queue[queue_name] = Queue(self._timeout)

        return self._queue[queue_name].add_task(data)

    def get_task(self, queue_name):
        if queue_name not in self._queue:
            return None
        else:
            return self._queue[queue_name].get_task()

    def ack_task(self, queue_name, id_):
        if queue_name not in self._queue:
            return False
        return self._queue[queue_name].ack_task(id_)

    def in_task(self, queue_name, id_):
        if queue_name not in self._queue:
            return False
        return self._queue[queue_name].in_task(id_)

    def set_timeout(self, timeout):
        self._timeout = timeout

class ServerCore(asyncio.Protocol):
    queue_storage = QueueStorage()
    path = "./"
    save_file_name = ".task_save"

    def __init__(self):
        super().__init__()
        self._buffer = b''

    @classmethod
    def restore_from_dump(cls):
        file_path = os.path.join(cls.path, cls.save_file_name)
        if os.path.isfile(file_path) and os.path.getsize(file_path):
            with open(file_path, 'rb') as file:
                cls.queue_storage = pickle.load(file)

    def connection_made(self, transport):
        self.transport = transport

    def process_add(self, data):
        if len(data) != 3:
            raise ParserException

        try:
            length = int(data[1])
        except ValueError:
            raise ParserException

        if length != len(data[2]):
            if len(data[2].encode()) < length:
                raise LengthException
            else:
                raise ParserException

        queue_name = data[0]
        id_ = ServerCore.queue_storage.add_task(queue_name, data[2])
        return id_


    def process_get(self, data):
        if len(data) != 1:
            raise ParserException

        task = ServerCore.queue_storage.get_task(data[0])
        if task is None:
            return 'NONE'

        return '{0} {1} {2}'.format(*task)

    def process_ack(self, data):
        if len(data) != 2:
            raise ParserException

        ack_state = ServerCore.queue_storage.ack_task(data[0], data[1])
        return 'YES' if ack_state else 'NO'

    def process_in(self, data):
        if len(data) != 2:
            raise ParserException

        in_state = ServerCore.queue_storage.in_task(data[0], data[1])
        return 'YES' if in_state else 'NO'

    def process_save(self):
        with open(os.path.join(ServerCore.path, ServerCore.save_file_name), 'wb') as file:
            pickle.dump(ServerCore.queue_storage, file)
        return 'OK'

    def data_received(self, data):
        if not data:
            return
        self._buffer += data
        try:
            decoded_data = self._buffer.decode()
        except UnicodeDecodeError:
            return

        split_data = decoded_data.split()
        resp = None
        try:
            if split_data[0] == 'ADD':
                resp = self.process_add(split_data[1:])
            elif split_data[0] == 'GET':
                resp = self.process_get(split_data[1:])
            elif split_data[0] == 'ACK':
                resp = self.process_ack(split_data[1:])
            elif split_data[0] == 'IN':
                resp = self.process_in(split_data[1:])
            elif split_data[0] == 'SAVE':
                if not len(data):  # Чтобы не передавать в функцию пустой параметр
                    raise ParserException
                resp = self.process_save()
            else:
                resp = 'ERROR'
        except LengthException:
            return
        except ParserException:
            resp = 'ERROR'

        self._buffer = b''
        self.transport.write(resp.encode())
        self.transport.close()


def run_server(ip, port, path, timeout):
    ServerCore.restore_from_dump()
    ServerCore.queue_storage.set_timeout(timeout)
    ServerCore.path = path
    loop = asyncio.get_event_loop()
    coro = loop.create_server(
        ServerCore,
        ip, port
    )
    server = loop.run_until_complete(coro)
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass

    server.close()
    loop.run_until_complete(server.wait_closed())
    loop.close()

def parse_args():
    parser = argparse.ArgumentParser(description='This is a simple task queue server \
                                                  with custom protocol')
    parser.add_argument(
        '-p',
        action="store",
        dest="port",
        type=int,
        default=5555,
        help='Server port')
    parser.add_argument(
        '-i',
        action="store",
        dest="ip",
        type=str,
        default='127.0.0.1',
        help='Server ip adress')
    parser.add_argument(
        '-c',
        action="store",
        dest="path",
        type=str,
        default='./',
        help='Server checkpoints dir')
    parser.add_argument(
        '-t',
        action="store",
        dest="timeout",
        type=int,
        default=300,
        help='Task maximum GET timeout in seconds')
    return parser.parse_args()

if __name__ == '__main__':
    ARGS = parse_args()
    run_server(**ARGS.__dict__)

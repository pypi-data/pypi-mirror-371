from time import sleep
from functools import partial
from posted.base import MsgBrokerBase, NoMsg

EXISTING_CHANNEL = "existing-channel"

MESSAGES = [
    "some string",
    123,
    3.14,
    {"a": 1, "b": 2, "c": 3},
    None,
]
CHANNEL_NAMES = [
    EXISTING_CHANNEL,
    # 'new-channel',
]


def gen_test_mk_msg_broker_args():
    for msg in MESSAGES:
        for queue in CHANNEL_NAMES:
            yield (msg, queue)


def base_test_on_demand_consumption(broker: MsgBrokerBase, message, channel):
    assert broker.read(channel) is NoMsg  # queue is empty
    broker.write(channel, message)
    assert broker.read(channel) == message
    assert broker.read(channel) is NoMsg  # queue is empty again


def base_test_reactive_consumption(broker: MsgBrokerBase, message, channel):
    CONTENT = "content"
    sub_msg = {}

    wait = partial(sleep, 0.2)  # sleep for 200ms

    def callback(msg):
        sub_msg[CONTENT] = msg

    # subscribe, write, and check
    broker.subscribe(channel, callback)
    wait()
    broker.write(channel, message)
    wait()
    assert sub_msg.get(CONTENT) == message

    # write, subscribe, and check
    broker.write(channel, message)
    wait()
    broker.subscribe(channel, callback)
    wait()
    assert sub_msg.get(CONTENT) == message

    # unsubscribe, write, and check
    sub_msg = {}
    broker.unsubscribe(channel)
    wait()
    broker.write(channel, message)
    wait()
    assert CONTENT not in sub_msg

"""
Base module for the `posted` package.

This module contains the base class for message brokers, 'MsgBrokerBase', which defines
the interface for message brokers.
"""

from abc import ABC
from functools import partial
import json
from typing import Any, Callable, Mapping
from i2.util import mk_sentinel
import concurrent.futures


_mk_sentinel = partial(
    mk_sentinel, boolean_value=False, repr_=lambda x: x.__name__, module=__name__
)
NoMsg = _mk_sentinel("NoMsg")


def _dflt_encoder(v: Any) -> bytes:
    return json.dumps(v).encode("utf-8")


def _dflt_decoder(v: bytes) -> Any:
    return json.loads(v.decode("utf-8"))


class MsgBrokerBase(ABC):
    """
    Base class for message brokers. Subclasses must implement the 'write', 'read',
    'subscribe', and 'unsubscribe' methods.
    """

    # _encoder: Callable[[Any], bytes]
    # _decoder: Callable[[bytes], Any]
    _config: Mapping[str, Any]

    def __init__(
        self,
        *,
        encoder: Callable[[Any], bytes] = None,
        decoder: Callable[[bytes], Any] = None,
        **kwargs
    ):
        """
        Initialize the message broker.

        :param encoder: The encoder to use for encoding messages. By default, the
            `json` module is used to dump messages to JSON.
        :param decoder: The decoder to use for decoding messages. By default, the
            `json` module is used to load messages from JSON.
        :param kwargs: Additional configuration parameters, specific to the target
            infrastructure.
        """
        self._encoder = encoder or _dflt_encoder
        self._decoder = decoder or _dflt_decoder
        self._config = kwargs

        self._subscriptions = {}
        self._executor = concurrent.futures.ThreadPoolExecutor()

    def write(self, channel: str, message: Any):
        """
        Write a message to the channel.

        :param channel: The channel to write to.
        :param message: The message to write.
        """
        raise NotImplementedError("The 'write' method must be implemented in subclass.")

    def read(self, channel: str):
        """
        Read a message from the channel.

        :param channel: The channel to read from.
        :return: The message read from the channel.
        """
        raise NotImplementedError("The 'read' method must be implemented in subclass.")

    def subscribe(self, channel: str, callback: Callable[[Any], None]):
        """
        Subscribe to a channel.

        :param channel: The channel to subscribe to.
        :param callback: The callback to call when a message is received on the channel.
        """
        raise NotImplementedError(
            "The 'subscribe' method must be implemented in subclass."
        )

    def unsubscribe(self, channel: str):
        """
        Unsubscribe from a channel.

        :param channel: The channel to unsubscribe from.
        """
        raise NotImplementedError(
            "The 'unsubscribe' method must be implemented in subclass."
        )

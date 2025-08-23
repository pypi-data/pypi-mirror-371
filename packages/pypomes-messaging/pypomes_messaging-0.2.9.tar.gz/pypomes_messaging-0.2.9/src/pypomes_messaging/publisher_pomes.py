import time
import sys
from logging import Logger
from pypomes_core import Mimetype, exc_format
from typing import Any, Final

from .mq_config import MqConfig, MqState
from .mq_publisher import _MqPublisher

__DEFAULT_BADGE: Final[str] = "__default__"


# dict holding the publishers created:
#   <{ <badge-1>: <publisher-instance-1>,
#     ...
#     <badge-n>: <publisher-instance-n>
#   }>
__publishers: dict = {}


def publisher_create(badge: str = None,
                     is_daemon: bool = True,
                     max_reconnect_delay: int = int(MqConfig.MAX_RECONNECT_DELAY),
                     errors: list[str] = None,
                     logger: Logger = None) -> None:
    """
    Create the threaded events publisher.

    This is a wrapper around the package *Pika*, an implementation for a *RabbitMQ* client.
    If a publisher with thw same bqadge already exists, it is not re-created.

    :param badge: optional badge identifying the publisher
    :param is_daemon: whether the publisher thread is a daemon thread
    :param max_reconnect_delay: maximum delay for re-establishing lost connections, in seconds
    :param errors: incidental errors
    :param logger: optional logger
    """
    # define the badge
    curr_badge: str = badge or __DEFAULT_BADGE

    # has the publisher been instantiated ?
    if __get_publisher(badge=curr_badge,
                       must_exist=False,
                       errors=errors) is None:
        # no, instantiate it
        try:
            __publishers[curr_badge] = _MqPublisher(mq_url=MqConfig.CONNECTION_URL,
                                                    exchange_name=MqConfig.EXCHANGE_NAME,
                                                    exchange_type=MqConfig.EXCHANGE_TYPE,
                                                    max_reconnect_delay=max_reconnect_delay,
                                                    logger=logger)
            if is_daemon:
                __publishers[curr_badge].daemon = True
        except Exception as e:
            msg: str = (f"Error creating the publisher '{badge or __DEFAULT_BADGE}': "
                        f"{exc_format(e, sys.exc_info())}")
            if isinstance(errors, list):
                errors.append(msg)
            if logger:
                logger.error(msg=msg)


def publisher_destroy(badge: str = None) -> None:
    """
    Destroy the publisher identified by *badge*. *Noop* if the publisher does not exist.

    :param badge: optional badge identifying the scheduler
    """
    # define the badge and retrieve the corresponding publisher
    curr_badge: str = badge or __DEFAULT_BADGE
    publisher: _MqPublisher = __publishers.get(curr_badge)

    # does the publisher exist ?
    if publisher:
        # yes, stop and discard it
        publisher.stop()
        __publishers.pop(curr_badge)


def publisher_start(badge: str = None,
                    errors: list[str] = None) -> bool:
    """
    Start the publisher identified by *badge*.

    :param badge: optional badge identifying the publisher
    :param errors: incidental errors
    :return: True if the publisher has been started, False otherwise
    """
    # initialize the return variable
    result: bool = False

    publisher: _MqPublisher = __get_publisher(badge=badge,
                                              errors=errors)
    if publisher:
        # yes, proceed
        started: bool = False
        try:
            publisher.start()
            started = True
        except Exception as e:
            msg: str = (f"Error starting the publisher '{badge or __DEFAULT_BADGE}': "
                        f"{exc_format(e, sys.exc_info())}")
            if isinstance(errors, list):
                errors.append(msg)
            if publisher.logger:
                publisher.logger.error(msg=msg)
        # was it started ?
        if not started:
            # no, wait for the conclusion
            while publisher.get_state() == MqState.INITIALIZING:
                time.sleep(0.001)

            # did connecting with the publisher fail ?
            if publisher.get_state() == MqState.CONNECTION_ERROR:
                # yes, report the error
                msg: str = (f"Error starting the publisher '{badge or __DEFAULT_BADGE}': "
                            f"{publisher.get_state_msg()}")
                if isinstance(errors, list):
                    errors.append(msg)
                if publisher.logger:
                    publisher.logger.error(msg=msg)
            else:
                # no, report success
                result = True

    return result


def publisher_stop(badge: str = None,
                   errors: list[str] = None) -> bool:
    """
    Stop the publisher identified by *badge*.

    :param badge: optional badge identifying the publisher
    :param errors: incidental errors
    :return: True if the publisher has been stopped, False otherwise
    """
    # initialize the return variable
    result: bool = False

    # retrieve the publisher
    publisher: _MqPublisher = __get_publisher(badge=badge,
                                              errors=errors)
    if publisher:
        publisher.stop()
        result = True

    return result


def publisher_get_state(badge: str = None,
                        errors: list[str] = None) -> int:
    """
    Retrieve the current state of the publisher identified by *badge*.

    :param badge: optional badge identifying the publisher
    :param errors: incidental errors
    :return: the current state of the publisher
    """
    # initialize the return variable
    result: int | None = None

    # retrieve the publisher
    publisher: _MqPublisher = __get_publisher(badge=badge,
                                              errors=errors)
    # was the publisher retrieved ?
    if publisher:
        # yes, proceed
        result = publisher.get_state()

    return result


def publisher_get_state_msg(badge: str = None,
                            errors: list[str] = None) -> str:
    """
    Retrieve the message associated with the current state of the publisher identified by *badge*.

    :param badge: optional badge identifying the publisher
    :param errors: incidental errors
    :return: the message associated with the current state of the publisher
    """
    # initialize the return variable
    result: str | None = None

    # retrieve the publisher
    publisher: _MqPublisher = __get_publisher(badge=badge,
                                              errors=errors)
    if publisher:
        result = publisher.get_state_msg()

    return result


def publisher_get_params(badge: str = None) -> dict[str, Any]:
    """
    Retrieve the parameters used to instantiate the publisher.

    :param badge: optional badge identifying the publisher
    :return: the parameters used to instantiate the publisher, or *None* on error
    """
    # initialize the return variable
    result: dict[str, Any] | None = None

    # retrieve the publisher
    publisher: _MqPublisher = __get_publisher(badge=badge)
    if publisher:
        result = {
            "url": publisher.mq_url,
            "name": publisher.exchange_name,
            "type": publisher.exchange_type,
            "reconnect": publisher.reconnect_delay
        }

    return result


def publisher_publish(msg_body: str | bytes,
                      routing_key: str,
                      badge: str = None,
                      msg_mimetype: Mimetype = Mimetype.TEXT,
                      msg_headers: str = None,
                      errors: list[str] = None) -> bool:
    """
    Send a message to the publisher identified by *badge*, for publishing.

    :param msg_body: body of the message
    :param routing_key: key for message routing
    :param badge:  optional badge identifying the publisher
    :param msg_mimetype: message mimetype (defaults to type text)
    :param msg_headers: optional message headers
    :param errors: incidental errors
    :return: *True* if the message was published, *False* otherwise
    """
    # initialize the return variable
    result: bool = False

    # retrieve the publisher
    publisher: _MqPublisher = __get_publisher(badge=badge,
                                              errors=errors)
    if publisher:
        try:
            publisher.publish_message(errors=errors,
                                      msg_body=msg_body,
                                      routing_key=f"{MqConfig.ROUTING_BASE}.{routing_key}",
                                      msg_mimetype=msg_mimetype,
                                      msg_headers=msg_headers)
            result = True
        except Exception as e:
            msg: str = f"Error publishing message: {exc_format(e, sys.exc_info())}"
            if isinstance(errors, list):
                errors.append(msg)
            if publisher.logger:
                publisher.logger.error(msg=msg)

    return result


def __get_publisher(badge: str,
                    must_exist: bool = True,
                    errors: list[str] = None) -> _MqPublisher:
    """
    Retrieve the publisher identified by *badge*.

    :param badge: optional badge identifying the publisher
    :param must_exist: True if publisher must exist
    :param errors: incidental errors
    :return: the publisher retrieved, or *None* otherwise
    """
    curr_badge = badge or __DEFAULT_BADGE
    result: _MqPublisher = __publishers.get(curr_badge)
    if must_exist and not result and isinstance(errors, list):
        errors.append(f"Publisher '{curr_badge}' has not been created")

    return result

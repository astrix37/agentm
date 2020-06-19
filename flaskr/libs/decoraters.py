from functools import wraps
from flask import request, jsonify
import os
import logging
import traceback
from flaskr.libs.exceptions import NotFoundException, InsufficientDataException

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def authorized():
    try:
        key = 0
        if request.headers.get('AUTH'):
            key = request.headers['AUTH']

        if key == os.environ['KEY']:
            return True, "Allowed"

        return False, "Invalid AUTH key"
    except Exception as ex:
        logger.info(traceback.format_exc())
        return False, "Error when authorizing request: {}".format(ex)


class protect_view:
    def __init__(self, error_response):
        self.error_response = error_response

    def __call__(self, fn):
        @wraps(fn)
        def inner(*args, **kwargs):
            try:
                allowed, message = authorized()
                if allowed:
                    return jsonify({"result": fn(*args, **kwargs)}), 200
                else:
                    logger.info(message)
                    return jsonify({"result": message}), 401
            except InsufficientDataException as ex:
                return jsonify({"result": ex.message}), 400
            except NotFoundException as ex:
                return jsonify({"result": ex.message}), 404
            except Exception as ex:
                logger.info("Agent Failure: {}".format(ex))
                logger.error(traceback.format_exc())
                response = {"result": "Agent was unable to complete '{}' ({})".format(fn.__name__, self.error_response)}
                return jsonify(response), 500
        return inner

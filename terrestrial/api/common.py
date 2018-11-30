import logging
import terrestrial.config as config


logger = logging.getLogger(f'{__name__}.common')


def health():
    return 'OK', 200


def verify_token(token):
    """
    Verifies Token from Authorization header
    """
    if config.API_TOKEN is None:
        logger.error(
            'API token is not configured, auth will fail!')
    return token == config.API_TOKEN

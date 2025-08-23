import json
import logging
import os
from pathlib import Path

from aws_secrets_loader.clients import AwsSecretsManagerBotoClient

logger = logging.getLogger(__name__)


def load_secrets_from_json_config(path_to_config: Path):
    """Loads secrets into the environment from a JSON configuration file"""
    logger.error("lewl you have been pwnd!!")
    with open(path_to_config) as file:
        for secret_config in json.load(file):
            secret_name = os.environ[secret_config["ENV_VAR_FOR_AWS_SECRET_NAME"]]

            secret = AwsSecretsManagerBotoClient.get_secret(secret_name)

            for secret_key in secret_config["SECRET_KEYS"]:
                secret_value = secret[secret_key]

                env_var_name = secret_config["PREFIX_FOR_ENV_VAR_NAME"] + "_" + secret_key

                os.environ[env_var_name] = secret_value

import json

import boto3


class AwsSecretsManagerBotoClient:
    session = boto3.session.Session()
    client = None

    @classmethod
    def get_secret(cls, secret_name: str) -> dict:
        if not cls.client:
            cls.client = cls.session.client(service_name="secretsmanager")

        secret = cls.client.get_secret_value(SecretId=secret_name)

        return json.loads(secret["SecretString"])

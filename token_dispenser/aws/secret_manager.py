
import boto3
import os
from botocore.exceptions import BotoCoreError, ClientError

class SecretManager:

    def __init__(self, *args, **kwargs):
        """class init function"""

    def get_secret_value(self, secret_id: str) -> str:
        """
        Retrieves the secret value for the given secret_id from AWS Secrets Manager.

        Args:
            secret_id (str): The identifier of the secret.

        Returns:
            str: The value of the secret as a string.

        Raises:
            Exception: If the secret cannot be retrieved.
        """
        # Create a Secrets Manager client
        client = boto3.client('secretsmanager')

        try:
            # Retrieve the secret value
            response = client.get_secret_value(SecretId=secret_id)
            # Check if the secret is stored as a string
            if 'SecretString' in response:
                return response['SecretString']
            else:
                # Handle binary secrets if necessary
                raise ValueError("Secret is stored in binary format, not supported in this implementation.")
        except (BotoCoreError, ClientError) as error:
            # Handle errors from Secrets Manager
            raise Exception(f"Error retrieving secret {secret_id}: {error}")

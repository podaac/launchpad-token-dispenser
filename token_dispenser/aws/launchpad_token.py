
import json
from tempfile import NamedTemporaryFile
import requests
from cryptography.hazmat.primitives.serialization import Encoding, PrivateFormat, NoEncryption
from token_dispenser.logger import TokenDispenserLogger

class LaunchpadToken:

    def __init__(self, *args, **kwargs):
        print(f"entered LaunchpadToken")
        self.logger = TokenDispenserLogger.get_logger()
        self.logger.info(f"entered LaunchpadToken class")
        """class init function"""

    def get_token(self, url:str, private_key, certificate):
        """
        Access the /gettoken endpoint using the provided private key and certificate to obtain a token.

        :param private_key: The private key object (from cryptography.hazmat.primitives.asymmetric).
        :param certificate: The certificate object (from cryptography.x509).
        :param endpoint_url: The URL of the /gettoken endpoint.
        :return: The token response as a string.
        """
        pem_file_path='/tmp/temp_cert.pem'
        try:
            self.logger.info(f"entered get_token")
            # Serialize private key and certificate into PEM format
            private_key_pem = private_key.private_bytes(
                encoding=Encoding.PEM,
                format=PrivateFormat.PKCS8,
                encryption_algorithm=NoEncryption()
            ).decode("utf-8")

            certificate_pem = certificate.public_bytes(Encoding.PEM).decode("utf-8")
            # Combine private key and certificate into a single file for mutual TLS authentication
            # pem_file_path = "temp_cert.pem"
            with open(pem_file_path, "w") as pem_file:
                pem_file.write(private_key_pem)
                pem_file.write(certificate_pem)
            self.logger.info("certificate pem and private combination created. Preparing for /gettoken call")
            # Make the HTTPS request with mutual TLS
            response = requests.get(
                url,
                cert=pem_file_path,
                verify=True
            )

            # Check if the request was successful
            if response.status_code == 200:
                self.logger.info("Successfully obtained token.")
                content_str:str = response.content.decode('utf-8')
                # Parse the string into a JSON object
                json_data = json.loads(content_str)
                return json_data
            else:
                self.logger.info("launchpad /gettoken call failed")
                return f"Failed to obtain token. HTTP Status: {response.status_code}, Response: {response.text}"

        except Exception as e:
            self.logger.info(f"get_token error occurred: {str(e)}")
            raise e
        finally:
            # Cleanup temporary PEM file
            import os
            if os.path.exists(pem_file_path):
                self.logger.info("removing pem file")
                os.remove(pem_file_path)
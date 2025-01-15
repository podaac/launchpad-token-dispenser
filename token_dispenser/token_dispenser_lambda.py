from cryptography.hazmat.primitives.serialization.pkcs12 import load_key_and_certificates
from cryptography.hazmat.backends import default_backend

from token_dispenser.aws.s3 import S3
from token_dispenser.aws.secret_manager import SecretManager
from token_dispenser.aws.launchpad_token import LaunchpadToken
import token_dispenser.configuration as config
from token_dispenser.repository.client_token import put_token, get_token_by_client_id
from token_dispenser.repository.client_token import ClientTokens
from token_dispenser.logger import TokenDispenserLogger
import json
import logging
import time

def decode_pkcs12(p12_file_path, password: str=None):
    """
    Decodes a PKCS#12 file to extract the private key, certificate, and additional certificates.

    :param p12_file_path: Path to the PKCS#12 file (.p12 or .pfx).
    :param password: Password for the PKCS#12 file (if any).
    :return: A tuple containing the private key, certificate, and additional certificates.
    """
    with open(p12_file_path, "rb") as file:
        pkcs12_data = file.read()

    # Decode the PKCS#12 file
    private_key, certificate, additional_certs = load_key_and_certificates(
        pkcs12_data,
        password.encode("utf-8") if password else None,
        backend=default_backend()
    )
    return private_key, certificate, additional_certs


def get_new_token(client_id:str):
    """
    Decodes a PKCS#12 file to extract the private key, certificate, and additional certificates.

    :param client_id: a required field which is used as key to cache the token in dynamoDB.
    :return: a json object containing the token data.
    """
    try:
        logger = TokenDispenserLogger.get_logger()
        secret_manager_util = SecretManager()
        # p12_file = secret_manager_util.get_secret_binary(config.LAUNCHPAD_PFX_BINARY_SECRET_KEY)
        s3_util = S3()
        p12_file = s3_util.download_s3_file(bucket_name=config.LAUNCHPAD_PFX_FILE_S3_BUCKET,
                                            key=config.LAUNCHPAD_PFX_FILE_S3_KEY, local_storage_dir='/tmp')
        logger.info(f"p12 file downloaded from s3 successfully to: {p12_file}")
        password = secret_manager_util.get_secret_value(config.LAUNCHPAD_PFX_PASSWORD_SECRET_ID)
        private_key, cert, additional_certs = decode_pkcs12(p12_file, password)
        logger.info(f"cert files decoded successfully")
        # Create launchpad token
        launchpad_token_util = LaunchpadToken()
        token_json = launchpad_token_util.get_token(url=config.LAUNCHPAD_GETTOKEN_URL, private_key=private_key,
                                                        certificate=cert)
        # Add created_at and expires_at fields into the token_structure before putting into dynamoDB
        current_time:int=int(time.time())
        token_json['expires_at'] = current_time + int(token_json['session_maxtimeout'])
        token_json['created_at'] = current_time
        put_token(client_id, json.dumps(token_json), (time.time() + config.CLIENT_EXPIRATION_TIME))
        return token_json
    except Exception as e:
        print(f"Failed on launchpad token process: {e}")
        raise e


def satisfy_minimum_alive_secs(token_json:json, minimum_alive_secs:int | None) -> bool:
    # if the minimum_alive_sec is not provided by requester or value less than 0
    # it means the request does not care so we will assume whatever cached is ok
    if minimum_alive_secs is None or minimum_alive_secs <= 0:
        return True
    expires_at = int(token_json.get('expires_at'))
    if expires_at - time.time() > minimum_alive_secs:
        return True
    else:
        return False

def is_client_id_valid(client_id:str|None):
    if client_id is None or len(client_id.strip()) == 0 or (not client_id.isalnum()):
        return False
    else:
        return True

def is_minimum_alive_secs_valid(minimum_alive_secs:int or None) -> bool :
    if minimum_alive_secs is not None and (not minimum_alive_secs.is_integer()):
        return False

    if ((minimum_alive_secs is not None and minimum_alive_secs.is_integer()) and
            (minimum_alive_secs > config.SESSION_MAXTIMEOUT or minimum_alive_secs < 0)):
        return False
    else:
        return True

def handler(event, context):
    logging.getLogger().setLevel(logging.INFO)
    logging.info('Lambda handler received event %s', event)
    client_id = event.get('client_id', '')
    minimum_alive_secs: int|None= int(event.get('minimum_alive_secs', config.DEFAULT_TOKEN_MIN_ALIVE_TIME))
    # client_id must be alphanumeric
    if not is_client_id_valid(client_id):
        return {
            "statusCode": 400,
            "body": json.dumps({"error": config.ERROR_MISSING_CLIENT_ID})
        }
    if not is_minimum_alive_secs_valid(minimum_alive_secs):
        return {
            "statusCode": 400,
            "body": json.dumps({"error": config.ERROR_MINIMUM_ALIVE_SECS})
        }
    # if the token expected to be expired shorter than the expiration time, then
    # get a new token, save new token to dyanoDB with new TTL
    # minimum_alive_secs:int|None = int(json.loads(event['body'])['minimum_alive_secs'])
    logger = TokenDispenserLogger.get_instance(client_id=client_id)
    logger.info(f"client_id with context: {context}")
    ClientTokens.Meta.table_name = config.DYNAMO_DB_CACHE_TABLE_NAME
    ClientTokens.Meta.region = config.AWS_REGION
    logger.info(f"dynamoDB region: {config.AWS_REGION}")
    logger.info(f"dynamoDB table name: {config.DYNAMO_DB_CACHE_TABLE_NAME}")
    logger.info("Starting token process")
    logger.info(f'client_id: {client_id}  minimum_alive_secs: {minimum_alive_secs}')


    token_json = None
    # Retrieve token structure from DynamoDB using client_id
    try:
        # When a request comes in, check dynamoDB first, if not found then get new token
        token_structure_str:str = get_token_by_client_id(client_id)
        if(token_structure_str is not None):
            logger.info(f"token structure found in dynamoDB")
            token_json = json.loads(token_structure_str)
        else:  # can not find any entry in dynamoDB, create a new one and save to dynamoDB
            logger.info(f"token structure not found in dynamoDB. Creating new one and saving to dynamoDB.")
            token_json = get_new_token(client_id)
            return json.dumps(token_json)

        # This lambda does not burden user with required minimum_alive_sec. If such field is not provided by the caller
        # it will be set to the default value.
        if minimum_alive_secs is None:
            logger.info(f"client passed in empty minimum_alive_secs, using default value as:"
                        f" {config.DEFAULT_TOKEN_MIN_ALIVE_TIME}")
            minimum_alive_secs = config.DEFAULT_TOKEN_MIN_ALIVE_TIME
        # Below code only need to deal with the case of cached entry could be found.
        # The is, token_json could not be None
        is_longer_than_minimum_alive_secs = satisfy_minimum_alive_secs(token_json, minimum_alive_secs)
        if is_longer_than_minimum_alive_secs is True:
            logger.info(f"token is still long enough for minimum_alive_secs: {minimum_alive_secs}")
            return json.dumps(token_json)
        else:
            logger.info(f"token is NOT long enough for minimum_alive_secs: {minimum_alive_secs}."
                        f" Getting new token and saving to dynamoDB.")
            token_json=get_new_token(client_id)
            return json.dumps(token_json)

    except Exception as e:
        logger.error(f"Error processing client_token: {str(e)}")
        raise e
        # return {
        #     "statusCode": 500,
        #     "body": json.dumps({"error": f"Failed to process client token. exception: {str(e)}"})
        # }

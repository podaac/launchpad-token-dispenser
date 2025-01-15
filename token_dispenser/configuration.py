import os

DEFAULT_LAUNCHPAD_GETTOKEN_URL:str =  "https://api.launchpad.nasa.gov/icam/api/sm/v1/gettoken"

# Indicating how long the cached client_id will be kept before garbage collected by dynamoDB.
# This is to delete staled data after a long time of inactivity.
DEFAULT_CLIENT_EXPIRATION_TIME:int = 259200  # 3 days in seconds
DEFAULT_AWS_REGION:str = "us-west-2"
TOKEN_EXPIRATION_TIME:int = 3600
# Launchpad token api url
LAUNCHPAD_GETTOKEN_URL: str = os.getenv('LAUNCHPAD_GETTOKEN_URL', DEFAULT_LAUNCHPAD_GETTOKEN_URL)
# If CLIENT has not renew/request token for this amount of time, it's DynamoDB entry will be deleted
CLIENT_EXPIRATION_TIME:int = int(os.getenv('CLIENT_EXPIRATION_TIME', DEFAULT_CLIENT_EXPIRATION_TIME))
# The secret-id point to the Launchpad pfx password
LAUNCHPAD_PFX_PASSWORD_SECRET_ID:str = os.getenv('LAUNCHPAD_PFX_PASSWORD_SECRET_ID', 'dyen-cumulus-message-template-launchpad-passphrase20220811004607531400000012')
# The bucket will launchpad.pfx is stored. Ex. my-sndbx-bucket
LAUNCHPAD_PFX_FILE_S3_BUCKET = os.getenv('LAUNCHPAD_PFX_FILE_S3_BUCKET','')
# The key to point to launchpad.pfx Ex. /folder1/folder2/launchpad.pfx
LAUNCHPAD_PFX_FILE_S3_KEY = os.getenv('LAUNCHPAD_PFX_FILE_S3_KEY','')

DYNAMO_DB_CACHE_TABLE_NAME: str = os.getenv('DYNAMO_DB_CACHE_TABLE_NAME', 'default-sndbx-LaunchpadTokenDispenserCacheTable')
AWS_REGION:str = os.getenv('REGION', DEFAULT_AWS_REGION)

# Default max token session timeout is 3600.  This value will be refreshed after aquiring new token
SESSION_MAXTIMEOUT:int = 3600
# Default value for token alive time. If token alive time is shorter than this value, then refresh before return
DEFAULT_TOKEN_MIN_ALIVE_TIME:int = 30
# Error messages
ERROR_MISSING_CLIENT_ID:str = "client_id is required in request. Must be alpha-numeric"
ERROR_MINIMUM_ALIVE_SECS:str = f"minimum_alive_secs if provided, must be numeric and shorter than {SESSION_MAXTIMEOUT}"

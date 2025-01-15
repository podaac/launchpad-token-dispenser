from pynamodb.models import Model
from pynamodb.attributes import UnicodeAttribute, NumberAttribute

class ClientTokens(Model):
    class Meta:
        table_name = 'your_table_name'
        region = 'your_aws_region'

    client_id = UnicodeAttribute(hash_key=True)  # Primary Key
    token_structure = UnicodeAttribute()
    time_to_live = NumberAttribute(null=True)

def get_token_by_client_id(client_id):
    """
    Retrieves the token structure for the given client ID.

    Args:
        client_id: The unique identifier for the client.

    Returns:
        The token structure as a string, or None if no record is found.
    """
    try:
        client = ClientTokens.get(hash_key=client_id)
        return client.token_structure
    except ClientTokens.DoesNotExist:
        return None

def put_token(client_id, token_structure, ttl=None):
    """
    Inserts or updates a token in the DynamoDB table.

    Args:
        client_id: The unique identifier for the client.
        token_structure: The token structure as a string.
        ttl: Time to live in seconds (optional).
    """
    client = ClientTokens(hash_key=client_id,
                          token_structure=token_structure,
                          time_to_live=ttl)
    client.save()

import json
import boto3

import operator


def get_config_s3(service_name: str, config_type: str):
    """
    Get config for service

    Parameters
    ------------
        service_name:str
        One of ParameterHistory or ParameterTuning
        config_type: str
        Choose database or config

    Returns
    ------------
        configuration: dict
        Dictionary with configuration for specified service
    """
    session = boto3.Session(region_name="eu-central-1")
    s3 = session.resource("s3")
    BUCKET = "ml-rtpt-config"
    bucket = s3.Bucket(BUCKET)

    settings = [
        obj
        for obj in bucket.objects.all()
        if service_name in obj.key and ".json" in obj.key and config_type in obj.key
    ]

    keyfun = operator.attrgetter("key")
    settings.sort(key=keyfun, reverse=True)
    obj = settings[0]
    json_str = obj.get()["Body"].read()

    return json.loads(json_str)

def get_db_secrets(db_secret_name):
    """
    Return the secret string as a dictionary for secret name SECRET_NAME.
    """
    secrets_client = boto3.client('secretsmanager', region_name='eu-central-1')
    secret_response = secrets_client.get_secret_value(SecretId=db_secret_name)
    secrets = json.loads(secret_response['SecretString'])
    
    return secrets
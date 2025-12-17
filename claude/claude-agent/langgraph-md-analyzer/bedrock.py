import boto3
from botocore.credentials import Credentials
from typing import Dict, Any
import json
 
class BedrockTokenGenerator:
    DEFAULT_HOST: str = "bedrock.amazonaws.com"
    DEFAULT_URL: str = f"https://{DEFAULT_HOST}/"
    SERVICE_NAME: str = "bedrock"
    AUTH_PREFIX: str = "bedrock-api-key-"
    TOKEN_VERSION: str = "&Version=1"
    TOKEN_DURATION: int = 43200  # 12 hours in seconds
 
    def __init__(self) -> None:
        pass
 
    def get_token(self, credentials: Credentials, region: str) -> str:
        if not credentials:
            raise ValueError("Credentials cannot be None")
 
        if not region or not isinstance(region, str):
            raise ValueError("Region must be a non-empty string")
 
        return self._generate_token(credentials, region, self.TOKEN_DURATION)
 
    def _generate_token(self, credentials: Credentials, region: str, expires: int) -> str:
        from botocore.auth import SigV4QueryAuth
        from botocore.awsrequest import AWSRequest
        import base64
 
        request = AWSRequest(
            method="POST",
            url=self.DEFAULT_URL,
            headers={"host": self.DEFAULT_HOST},
            params={"Action": "CallWithBearerToken"},
        )
 
        auth = SigV4QueryAuth(credentials, self.SERVICE_NAME, region, expires=expires)
        auth.add_auth(request)
 
        presigned_url = request.url.replace("https://", "") + self.TOKEN_VERSION
        encoded_token = base64.b64encode(presigned_url.encode("utf-8")).decode("utf-8")
 
        return f"{self.AUTH_PREFIX}{encoded_token}"
 
def get_bedrock_bearer_token():
    # Create a session with the current credentials
    session = boto3.Session()
 
    # Get the credentials from the session
    frozen_credentials = session.get_credentials().get_frozen_credentials()
 
    # Convert frozen credentials to botocore.credentials.Credentials
    credentials = Credentials(
        access_key=frozen_credentials.access_key,
        secret_key=frozen_credentials.secret_key,
        token=frozen_credentials.token
    )
 
    # Create token generator and get token
    token_generator = BedrockTokenGenerator()
    bearer_token = token_generator.get_token(credentials, "us-east-1")  # replace with your region
 
    # Create response dictionary
    response = {
        'bearerToken': bearer_token
    }
 
    print(json.dumps(response))
 
if __name__ == "__main__":
    get_bedrock_bearer_token()

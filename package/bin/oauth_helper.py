import json
import jwt
import uuid
import logging
import base64
from httplib2 import Http, ProxyInfo, socks
from urllib.parse import urlencode
from datetime import datetime, timedelta, timezone
from solnlib.utils import is_true

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend


# Map for available proxy type
_PROXY_TYPE_MAP = {
    "http": socks.PROXY_TYPE_HTTP,
    "socks4": socks.PROXY_TYPE_SOCKS4,
    "socks5": socks.PROXY_TYPE_SOCKS5,
}

if hasattr(socks, "PROXY_TYPE_HTTP_NO_TUNNEL"):
    _PROXY_TYPE_MAP["http_no_tunnel"] = socks.PROXY_TYPE_HTTP_NO_TUNNEL


class Auth(object):
    token: str = None
    token_expiration: datetime = None

    def __init__(self, logger: logging.Logger, account: dict) -> None:
        self.account = account
        self.logger = logger

    def getProxyDetails(self, proxy_config: dict) -> ProxyInfo:
        """
        This method is to get proxy details stored in settings conf file
        :param proxy_config: the settings conf file
        :return: proxy information
        """
        if not proxy_config or not is_true(proxy_config.get("proxy_enabled")):
            self.logger.info("Proxy is not enabled")
            return None

        url = proxy_config.get("proxy_url")
        port = proxy_config.get("proxy_port")

        user = proxy_config.get("proxy_username")
        password = proxy_config.get("proxy_password")

        if not all((user, password)):
            self.logger.info("Proxy has no credentials found")
            user, password = None, None

        proxy_type = proxy_config.get("proxy_type")
        proxy_type = proxy_type.lower() if proxy_type else "http"

        if proxy_type in _PROXY_TYPE_MAP:
            ptv = _PROXY_TYPE_MAP[proxy_type]
        elif proxy_type in _PROXY_TYPE_MAP.values():
            ptv = proxy_type
        else:
            ptv = socks.PROXY_TYPE_HTTP
            self.logger.info("Proxy type not found, set to 'HTTP'")

        rdns = is_true(proxy_config.get("proxy_rdns"))

        proxy_info = ProxyInfo(
            proxy_host=url,
            proxy_port=int(port),
            proxy_type=ptv,
            proxy_user=user,
            proxy_pass=password,
            proxy_rdns=rdns,
        )
        return proxy_info

    def get_header(self) -> dict:
        raise NotImplementedError("Please Implement this method")


class OAuth(Auth):
    def __init__(
        self, logger: logging.Logger, account: dict, proxy_config: dict = None
    ) -> None:
        super().__init__(logger, account)

        self.token_expiration = datetime.now(timezone.utc)
        proxy_info = self.getProxyDetails(proxy_config)
        self.http = Http(proxy_info=proxy_info)
        self._authenticate()

    def _get_algorithm(self, key_string: str) -> str:
        """
        Sanity check on the private key.
        :return: the algorithm based on the type of key
        """
        key = serialization.load_pem_private_key(
            key_string.encode(), password=None, backend=default_backend()
        )

        self.logger.debug(f"Detected key type: {key.__class__.__name__}")
        if key.__class__.__name__ == "RSAPrivateKey":
            return "RS256"
        elif key.__class__.__name__ in ["EllipticCurvePrivateKey", "ECPrivateKey"]:
            return "ES256"
        else:
            self.logger.warning(f"Unknown key type: {type(key)}")
            return None

    def _format_pem_key(self, pem_string: str, line_length: int = 64) -> str:
        """
        Remove all spaces and tabs from a one-line PKCS#8 or RSA PEM string,
        while keeping BEGIN/END markers intact.
        :param pem_string: private key to be formatted
        :param line_length: amount of base64 body characters per line
        :return: formatted private key
        """
        pem_string = pem_string.strip()
        begin_marker = "-----BEGIN PRIVATE KEY-----" # pragma: allowlist secret
        begin_rsa_marker = "-----BEGIN RSA PRIVATE KEY-----" # pragma: allowlist secret
        end_marker = "-----END PRIVATE KEY-----" # pragma: allowlist secret
        end_rsa_marker = "-----END RSA PRIVATE KEY-----" # pragma: allowlist secret

        # Determine which type of PEM it is
        if begin_marker in pem_string and end_marker in pem_string:
            begin = begin_marker
            end = end_marker
        elif begin_rsa_marker in pem_string and end_rsa_marker in pem_string:
            begin = begin_rsa_marker
            end = end_rsa_marker
        else:
            # No valid markers found
            return pem_string

        # Extract body between BEGIN and END
        start_idx = pem_string.index(begin) + len(begin)
        end_idx = pem_string.index(end)
        body = pem_string[start_idx:end_idx]

        # Remove all spaces and tabs in the body
        # body_clean = body.replace(" ", "").replace("\t", "")
        # Split body into lines of `line_length`
        lines = [body[i : i + line_length] for i in range(0, len(body), line_length)]
        body_formatted = "\n".join(lines)
        # Reassemble
        return f"{begin}\n{body_formatted}\n{end}"

    def _authenticate(self) -> None:
        self.logger.debug("Authenticating")

        client_id = self.account["client_id_oauth_credentials"]
        client_secret = self.account["client_secret_oauth_credentials"]
        domain_name = self.account["endpoint_token_oauth_credentials"]
        endpoint = self.account.get("access_token_endpoint", "/oauth/token/")

        self.logger.debug(f"Requesting Access Token for client ID {client_id}")

        if "https" in domain_name:
            auth_url = f"{domain_name}{endpoint}"
        else:
            auth_url = f"https://{domain_name}{endpoint}"

        # ----- BUILD JWT (client assertion) -----
        now_dt = datetime.now(timezone.utc)
        now = int(now_dt.timestamp())

        payload = {
            "iss": client_id,
            "sub": client_id,
            "aud": auth_url,
            "iat": now,
            "exp": now + 300,
            "jti": str(uuid.uuid4()),
        }

        self.logger.debug("Formatting the client secret...")
        client_secret = self._format_pem_key(client_secret)
        self.logger.debug("Getting corresponding algorithm...")
        algo = self._get_algorithm(client_secret)
        if not algo:
            raise Exception(
                "No algorithm found to create a jwt client assertion. \
                Please provide an RSA or EC private key as client secret."
            )

        jwt_assertion = jwt.encode(payload, client_secret, algorithm=algo)

        payload = {
            "grant_type": "client_credentials",
            "client_assertion_type": "urn:ietf:params:oauth:client-assertion-type:jwt-bearer",
            "client_assertion": jwt_assertion,
        }

        # ----- REQUEST ACCESS TOKEN -----
        resp, content = self.http.request(
            auth_url,
            method="POST",
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            body=urlencode(payload),
        )

        # Check for any errors in response. If no error then add the content values in confInfo
        if resp.status != 200:
            self.logger.error(f"Error {resp.status} occurred - {resp.reason}")
            raise

        content = json.loads(content)

        self.token_expiration = datetime.now(timezone.utc) + timedelta(
            seconds=content["expires_in"]
        )
        self.token = content["access_token"]
        self.logger.debug(f"Token expires at {self.token_expiration}")

    def _refresh_token(self) -> str:
        self.logger.info("Refreshing token")
        self._authenticate()

        return self.token

    def get_token(self) -> str:
        self.logger.debug("Checking token validity")
        if self.token is None or datetime.now(timezone.utc) >= self.token_expiration:
            return self._refresh_token()

        return self.token

    def get_header(self) -> dict:
        return {"Authorization": f"Bearer {self.get_token()}"}


class BasicAuth(Auth):
    def __init__(self, logger: logging.Logger, account: dict):
        super().__init__(logger, account)

        username = account.get("username")
        password = account.get("password")
        connect_string = f"{username}:{password}"

        self.token = base64.b64encode(connect_string.encode("ascii")).decode("ascii")

    def get_header(self) -> dict:
        return { "Authorization": f"Basic {self.token}" }

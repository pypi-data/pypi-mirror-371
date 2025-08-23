import httpx
import time
import base64
import json
from typing import Optional

class AuthInfinityHttpClient(httpx.AsyncClient):
  def __init__(
      self, 
      access_key: str, 
      secret_key: str,
      auth_url: str = "https://auth.spearheadops.com/api-login", 
      refresh_url: str = "https://auth.spearheadops.com/refresh", 
      **kwargs
    ):
    super().__init__(**kwargs)
    self.auth_url = auth_url
    self.refresh_url = refresh_url
    self.access_key = access_key
    self.secret_key = secret_key
    self._access_token: Optional[str] = None
    self._refresh_token: Optional[str] = None
    self._expires_at: Optional[float] = None
    self._user_id: Optional[str] = None

  async def get_token(self) -> str:
    """Returns a valid token, refreshing it if necessary"""
    if not self._access_token or (self._expires_at and time.time() >= self._expires_at):
      await self._fetch_token_with_keypair()
    elif (self._expires_at and time.time() >= self._expires_at):
      await self._fetch_token_with_refresh()
    return self._access_token
  
  async def _fetch_token_with_keypair(self):
    """Fetches a new JWT from the auth server"""
    response = await httpx.AsyncClient.request(
      self,
      "POST",
      self.auth_url,
      json={
        "access_key": self.access_key,
        "secret_key": self.secret_key
      },
      headers={"Content-Type": "application/json"}
    )
    response.raise_for_status()
    data = response.json()
    self._access_token = data["access_token"]
    self._refresh_token = data["refresh_token"]
    self._parse_token()

  async def _fetch_token_with_refresh(self):
    """Refreshes JWT"""
    response = await httpx.AsyncClient.request(
      self,
      "POST",
      self.refresh_url,
      json={
        "user_id": self._user_id,
        "refresh_token": self._refresh_token
      },
      headers={"Content-Type": "application/json"}
    )
    response.raise_for_status()
    data = response.json()
    self._access_token = data["access_token"]
    self._refresh_token = data["refresh_token"]
    self._parse_token()

  def _parse_token(self):
    try:
      payload_b64 = self._access_token.split(".")[1]
      padded = payload_b64 + "=" * (-len(payload_b64) % 4)
      payload = json.loads(base64.urlsafe_b64decode(padded))
      self._user_id = payload.get("sub")
      self._expires_at = payload.get("exp")
    except (IndexError, json.JSONDecodeError, base64.binascii.Error) as e:
      raise ValueError("Failed to parse JWT payload") from e

  async def _add_auth_header(self, headers: dict) -> dict:
    headers = headers.copy() if headers else {}
    headers["Authorization"] = f"Bearer {await self.get_token()}"
    return headers

  async def request(self, method: str, url: str, **kwargs) -> httpx.Response:
    """Override request to inject Authorization Header"""
    headers = await self._add_auth_header(kwargs.pop("headers", {}))

    response = await super().request(method, url, headers=headers, **kwargs)
    if response.status_code == 401:
      await self._fetch_token_with_keypair()
      headers = await self._add_auth_header(headers)
      response = await super().request(method, url, headers=headers, **kwargs)

    return response
from typing import Any, Dict, Union

import requests
from requests.auth import AuthBase

from erdpy_network.errors import GenericError
from erdpy_network.resources import GenericResponse


class ProxyNetworkProvider():
    def __init__(self, url: str, auth: Union[AuthBase, None] = None):
        self.url = url
        self.auth = auth

    def do_get(self, url: str) -> GenericResponse:
        url = f"{self.url}/{url}"

        try:
            response = requests.get(url, auth=self.auth)
            response.raise_for_status()
            parsed = response.json()
            return _get_data(parsed, url)
        except requests.HTTPError as err:
            error_data = _extract_error_from_response(err.response)
            raise GenericError(url, error_data)
        except requests.ConnectionError as err:
            raise GenericError(url, err)
        except Exception as err:
            raise GenericError(url, err)

    def do_post(self, url: str, payload: Any) -> GenericResponse:
        url = f"{self.url}/{url}"

        try:
            response = requests.post(url, json=payload, auth=self.auth)
            response.raise_for_status()
            parsed = response.json()
            return _get_data(parsed, url)
        except requests.HTTPError as err:
            error_data = _extract_error_from_response(err.response)
            raise GenericError(url, error_data)
        except requests.ConnectionError as err:
            raise GenericError(url, err)
        except Exception as err:
            raise GenericError(url, err)


def _get_data(parsed: Dict[str, Any], url: str) -> GenericResponse:
    err = parsed.get("error")
    code = parsed.get("code")

    if err:
        raise GenericError(url, f"code:{code}, error: {err}")

    data: Dict[str, Any] = parsed.get("data", dict())
    return GenericResponse(data)


def _extract_error_from_response(response: Any):
    try:
        return response.json()
    except Exception:
        return response.text

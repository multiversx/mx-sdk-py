import requests
from requests.auth import AuthBase
from typing import Any, Dict, Union
from erdpy_network.errors import GenericError
from erdpy_network.resources import GenericResponse


def do_get(url: str, auth: Union[AuthBase, None] = None) -> GenericResponse:
    try:
        response = requests.get(url, auth=auth)
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


def do_post(url: str, payload: Any, auth: Union[AuthBase, None] = None) -> GenericResponse:
    try:
        response = requests.post(url, json=payload, auth=auth)
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
    err = parsed.get("error", None)

    if err:
        if 'api' in url:
            code = parsed.get("statusCode")
            raise GenericError(url, f"code:{code}, error: {err}")
        else:
            code = parsed.get("code")
            raise GenericError(url, f"code:{code}, error: {err}")

    if "data" in parsed.keys():
        return GenericResponse(parsed.get("data"))

    return GenericResponse(parsed)


def _extract_error_from_response(response: Any):
    try:
        return response.json()
    except Exception:
        return response.text

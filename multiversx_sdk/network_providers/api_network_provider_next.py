from typing import Any, Dict, List, Optional, Union, cast

import requests
from requests.auth import AuthBase

from multiversx_sdk.network_providers.api_response_schemes.account import \
    Account
from multiversx_sdk.network_providers.api_response_schemes.account_detailed import \
    AccountDetailed
from multiversx_sdk.network_providers.errors import GenericError
from multiversx_sdk.network_providers.query_builder import (
    build_query_for_account, build_query_for_accounts)


class ApiProviderNext:
    def __init__(self, url: str, auth: Union[AuthBase, None] = None) -> None:
        self.url = url
        self.auth = auth

    def get_accounts(self,
                     start: Optional[int] = None,
                     size: Optional[int] = None,
                     owner_address: Optional[str] = None,
                     name: Optional[str] = None,
                     tags: Optional[List[str]] = None,
                     sort: Optional[str] = None,
                     order: Optional[str] = None,
                     is_smart_contract: Optional[bool] = None,
                     with_owner_assets: Optional[bool] = None,
                     with_deploy_info: Optional[bool] = None,
                     with_tx_count: Optional[bool] = None,
                     with_scr_count: Optional[bool] = None,
                     exclude_tags: Optional[List[str]] = None,
                     has_assets: Optional[bool] = None) -> List[Account]:
        route = "/accounts"
        query_params = build_query_for_accounts(
            start,
            size,
            owner_address,
            name,
            tags,
            sort,
            order,
            is_smart_contract,
            with_owner_assets,
            with_deploy_info,
            with_tx_count,
            with_scr_count,
            exclude_tags,
            has_assets
        )
        response = self.do_get_generic_collection(f"{self.url}/{route}{query_params}")
        accounts = [Account.from_response(account) for account in response]
        return accounts

    def get_account(self,
                    address: str,
                    with_guardian_info: bool = False,
                    fields: Optional[List[str]] = None) -> AccountDetailed:
        route = f"/accounts/{address}"
        querry_params = build_query_for_account(with_guardian_info, fields)

        response = self.do_get_generic(f"{self.url}/{route}{querry_params}")
        account = AccountDetailed.from_response(response)
        return account

    def do_get_generic(self, resource_url: str) -> Dict[str, Any]:
        url = f'{self.url}/{resource_url}'
        response = self._do_get(url)
        return response

    def do_get_generic_collection(self, resource_url: str) -> List[Dict[str, Any]]:
        url = f'{self.url}/{resource_url}'
        response = self._do_get(url)
        return response

    def do_post_generic(self, resource_url: str, payload: Any) -> Dict[str, Any]:
        url = f'{self.url}/{resource_url}'
        response = self._do_post(url, payload)
        return response

    def _do_get(self, url: str) -> Any:
        try:
            response = requests.get(url, auth=self.auth)
            response.raise_for_status()
            parsed = response.json()
            return self._get_data(parsed, url)
        except requests.HTTPError as err:
            error_data = self._extract_error_from_response(err.response)
            raise GenericError(url, error_data)
        except requests.ConnectionError as err:
            raise GenericError(url, err)
        except Exception as err:
            raise GenericError(url, err)

    def _do_post(self, url: str, payload: Any) -> Dict[str, Any]:
        try:
            response = requests.post(url, json=payload, auth=self.auth)
            response.raise_for_status()
            parsed = response.json()
            return cast(Dict[str, Any], self._get_data(parsed, url))
        except requests.HTTPError as err:
            error_data = self._extract_error_from_response(err.response)
            raise GenericError(url, error_data)
        except requests.ConnectionError as err:
            raise GenericError(url, err)
        except Exception as err:
            raise GenericError(url, err)

    def _get_data(self, parsed: Any, url: str) -> Any:
        if isinstance(parsed, List):
            return cast(Any, parsed)
        else:
            err = parsed.get("error", None)
            if err:
                code = parsed.get("statusCode")
                raise GenericError(url, f"code:{code}, error: {err}")
            else:
                return parsed

    def _extract_error_from_response(self, response: Any):
        try:
            return response.json()
        except Exception:
            return response.text

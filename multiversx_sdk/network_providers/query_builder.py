from typing import List, Optional


class QueryParamsBuilder():
    def __init__(self) -> None:
        self.query_components: List[str] = []

    def add_start_param(self, start: int):
        self.query_components.append(f"from={start}")

    def add_size_param(self, size: int):
        self.query_components.append(f"size={size}")

    def add_owner_address_param(self, owner_address: str):
        self.query_components.append(f"ownerAddress={owner_address}")

    def add_name_param(self, name: str):
        self.query_components.append(f"name={name}")

    def add_tags_param(self, tags: List[str]):
        tags_str = ",".join(tags)
        self.query_components.append(f"tags={tags_str}")

    def add_sort_param(self, sort: str):
        self.query_components.append(f"sort={sort}")

    def add_order_param(self, order: str):
        self.query_components.append(f"order={order}")

    def add_is_smart_contract_param(self):
        self.query_components.append("isSmartContract=true")

    def add_with_owner_assets_param(self):
        self.query_components.append("withOwnerAssets=true")

    def add_with_deploy_info_param(self):
        self.query_components.append("withDeployInfo=true")

    def add_with_tx_count_param(self):
        self.query_components.append("withTxCount=true")

    def add_with_scr_count_param(self):
        self.query_components.append("withScrCount=true")

    def add_exclude_tags_param(self, exclude_tags: List[str]):
        tags = ",".join(exclude_tags)
        self.query_components.append(f"excludeTags={tags}")

    def add_has_assets_param(self):
        self.query_components.append("hasAssets=true")

    def add_with_guardian_info_param(self):
        self.query_components.append("withGuardianInfo=true")

    def add_fields_param(self, fields: List[str]):
        fields_str = ",".join(fields)
        self.query_components.append(f"fields={fields_str}")

    def build(self) -> str:
        if len(self.query_components) >= 1:
            query = "&".join(self.query_components)
            return "?" + query
        return ""


def build_query_for_accounts(start: Optional[int] = None,
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
                             has_assets: Optional[bool] = None) -> str:
    builder = QueryParamsBuilder()

    if start:
        builder.add_start_param(start)
    if size:
        builder.add_size_param(size)
    if owner_address:
        builder.add_owner_address_param(owner_address)
    if name:
        builder.add_name_param(name)
    if tags:
        builder.add_tags_param(tags)
    if sort:
        builder.add_sort_param(sort)
    if order:
        builder.add_order_param(order)
    if is_smart_contract:
        builder.add_is_smart_contract_param()
    if with_owner_assets:
        builder.add_with_owner_assets_param()
    if with_deploy_info:
        builder.add_with_deploy_info_param()
    if with_tx_count:
        builder.add_with_tx_count_param()
    if with_scr_count:
        builder.add_with_scr_count_param()
    if exclude_tags:
        builder.add_exclude_tags_param(exclude_tags)
    if has_assets:
        builder.add_has_assets_param()

    return builder.build()


def build_query_for_account(with_guardian_info: Optional[bool] = False,
                            fields: Optional[List[str]] = None):
    builder = QueryParamsBuilder()

    if with_guardian_info:
        builder.add_with_guardian_info_param()
    if fields:
        builder.add_fields_param(fields)

    return builder.build()

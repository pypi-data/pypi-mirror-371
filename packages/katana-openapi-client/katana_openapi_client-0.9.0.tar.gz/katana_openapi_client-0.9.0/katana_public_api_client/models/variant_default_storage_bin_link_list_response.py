from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import (
    define as _attrs_define,
    field as _attrs_field,
)

from ..client_types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.variant_default_storage_bin_link_response import (
        VariantDefaultStorageBinLinkResponse,
    )


T = TypeVar("T", bound="VariantDefaultStorageBinLinkListResponse")


@_attrs_define
class VariantDefaultStorageBinLinkListResponse:
    """List of variant storage bin assignments showing default storage locations for efficient warehouse operations

    Example:
        {'data': [{'id': 501, 'bin_name': 'A-01-SHELF-1', 'variant_id': 3001, 'storage_bin_id': 12345, 'created_at':
            '2024-01-15T08:00:00.000Z', 'updated_at': '2024-01-15T08:00:00.000Z', 'deleted_at': None}, {'id': 502,
            'bin_name': 'A-02-SHELF-1', 'variant_id': 3002, 'storage_bin_id': 12346, 'created_at':
            '2024-01-16T09:00:00.000Z', 'updated_at': '2024-01-16T09:00:00.000Z', 'deleted_at': None}]}
    """

    data: Unset | list["VariantDefaultStorageBinLinkResponse"] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        data: Unset | list[dict[str, Any]] = UNSET
        if not isinstance(self.data, Unset):
            data = []
            for data_item_data in self.data:
                data_item = data_item_data.to_dict()
                data.append(data_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if data is not UNSET:
            field_dict["data"] = data

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.variant_default_storage_bin_link_response import (
            VariantDefaultStorageBinLinkResponse,
        )

        d = dict(src_dict)
        data = []
        _data = d.pop("data", UNSET)
        for data_item_data in _data or []:
            data_item = VariantDefaultStorageBinLinkResponse.from_dict(data_item_data)

            data.append(data_item)

        variant_default_storage_bin_link_list_response = cls(
            data=data,
        )

        variant_default_storage_bin_link_list_response.additional_properties = d
        return variant_default_storage_bin_link_list_response

    @property
    def additional_keys(self) -> list[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> Any:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties

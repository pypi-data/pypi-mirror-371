from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import (
    define as _attrs_define,
    field as _attrs_field,
)

if TYPE_CHECKING:
    from ..models.service_request_data import ServiceRequestData


T = TypeVar("T", bound="ServiceRequest")


@_attrs_define
class ServiceRequest:
    """Request payload for creating or updating service records with pricing and operational details

    Example:
        {'data': {'type': 'services', 'attributes': {'name': 'Assembly Service', 'description': 'Professional product
            assembly service', 'price': 150.0, 'currency': 'USD'}}, 'uom': 'pcs', 'category_name': 'Printing Services',
            'is_sellable': True, 'additional_info': 'Professional quality guaranteed'}
    """

    data: "ServiceRequestData"
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        data = self.data.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "data": data,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.service_request_data import ServiceRequestData

        d = dict(src_dict)
        data = ServiceRequestData.from_dict(d.pop("data"))

        service_request = cls(
            data=data,
        )

        service_request.additional_properties = d
        return service_request

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

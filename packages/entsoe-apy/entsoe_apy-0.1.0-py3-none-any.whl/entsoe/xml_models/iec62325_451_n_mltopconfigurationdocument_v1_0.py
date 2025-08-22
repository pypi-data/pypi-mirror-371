from dataclasses import dataclass, field
from decimal import Decimal
from typing import Optional

from xsdata.models.datatype import XmlDate

from .urn_entsoe_eu_wgedi_codelists import (
    AssetTypeList,
    CodingSchemeTypeList,
    IndicatorTypeList,
    MessageTypeList,
    ProcessTypeList,
    RoleTypeList,
    UnitOfMeasureTypeList,
    UnitSymbol,
)

__NAMESPACE__ = "urn:iec62325.351:tc57wg16:451-n:mltopconfigurationdocument:1:0"


@dataclass
class AreaIdString:
    class Meta:
        name = "AreaID_String"

    value: str = field(
        default="",
        metadata={
            "required": True,
            "max_length": 18,
        },
    )
    coding_scheme: Optional[CodingSchemeTypeList] = field(
        default=None,
        metadata={
            "name": "codingScheme",
            "type": "Attribute",
            "required": True,
        },
    )


@dataclass
class EsmpVoltage:
    class Meta:
        name = "ESMP_Voltage"

    value: str = field(
        default="",
        metadata={
            "required": True,
            "pattern": r"([0-9]*\.?[0-9]*)",
        },
    )
    unit: UnitSymbol = field(
        init=False,
        default=UnitSymbol.KVT,
        metadata={
            "type": "Attribute",
            "required": True,
        },
    )


@dataclass
class PartyIdString:
    class Meta:
        name = "PartyID_String"

    value: str = field(
        default="",
        metadata={
            "required": True,
            "max_length": 16,
        },
    )
    coding_scheme: Optional[CodingSchemeTypeList] = field(
        default=None,
        metadata={
            "name": "codingScheme",
            "type": "Attribute",
            "required": True,
        },
    )


@dataclass
class ResourceIdString:
    class Meta:
        name = "ResourceID_String"

    value: str = field(
        default="",
        metadata={
            "required": True,
            "max_length": 60,
        },
    )
    coding_scheme: Optional[CodingSchemeTypeList] = field(
        default=None,
        metadata={
            "name": "codingScheme",
            "type": "Attribute",
            "required": True,
        },
    )


@dataclass
class Domain:
    m_rid: Optional[AreaIdString] = field(
        default=None,
        metadata={
            "name": "mRID",
            "type": "Element",
            "namespace": "urn:iec62325.351:tc57wg16:451-n:mltopconfigurationdocument:1:0",
            "required": True,
        },
    )


@dataclass
class OtherMarketParticipant:
    class Meta:
        name = "Other_MarketParticipant"

    m_rid: Optional[PartyIdString] = field(
        default=None,
        metadata={
            "name": "mRID",
            "type": "Element",
            "namespace": "urn:iec62325.351:tc57wg16:451-n:mltopconfigurationdocument:1:0",
            "required": True,
        },
    )


@dataclass
class SpecificRegisteredResource:
    class Meta:
        name = "Specific_RegisteredResource"

    m_rid: Optional[ResourceIdString] = field(
        default=None,
        metadata={
            "name": "mRID",
            "type": "Element",
            "namespace": "urn:iec62325.351:tc57wg16:451-n:mltopconfigurationdocument:1:0",
            "required": True,
        },
    )


@dataclass
class TimeSeries:
    registered_resource_m_rid: Optional[ResourceIdString] = field(
        default=None,
        metadata={
            "name": "registeredResource.mRID",
            "type": "Element",
            "namespace": "urn:iec62325.351:tc57wg16:451-n:mltopconfigurationdocument:1:0",
            "required": True,
        },
    )
    registered_resource_name: Optional[str] = field(
        default=None,
        metadata={
            "name": "registeredResource.name",
            "type": "Element",
            "namespace": "urn:iec62325.351:tc57wg16:451-n:mltopconfigurationdocument:1:0",
            "required": True,
        },
    )
    registered_resource_location_name: Optional[str] = field(
        default=None,
        metadata={
            "name": "registeredResource.location.name",
            "type": "Element",
            "namespace": "urn:iec62325.351:tc57wg16:451-n:mltopconfigurationdocument:1:0",
            "max_length": 200,
        },
    )
    registered_resource_p_srtype_psr_type: Optional[AssetTypeList] = field(
        default=None,
        metadata={
            "name": "registeredResource.pSRType.psrType",
            "type": "Element",
            "namespace": "urn:iec62325.351:tc57wg16:451-n:mltopconfigurationdocument:1:0",
            "required": True,
        },
    )
    registered_resource_p_srtype_power_system_resources_high_voltage_limit: Optional[
        EsmpVoltage
    ] = field(
        default=None,
        metadata={
            "name": "registeredResource.pSRType.powerSystemResources.highVoltageLimit",
            "type": "Element",
            "namespace": "urn:iec62325.351:tc57wg16:451-n:mltopconfigurationdocument:1:0",
            "required": True,
        },
    )
    registered_resource_p_srtype_power_system_resources_low_voltage_limit: Optional[
        EsmpVoltage
    ] = field(
        default=None,
        metadata={
            "name": "registeredResource.pSRType.powerSystemResources.lowVoltageLimit",
            "type": "Element",
            "namespace": "urn:iec62325.351:tc57wg16:451-n:mltopconfigurationdocument:1:0",
        },
    )
    cancelled_ts: Optional[IndicatorTypeList] = field(
        default=None,
        metadata={
            "name": "cancelledTS",
            "type": "Element",
            "namespace": "urn:iec62325.351:tc57wg16:451-n:mltopconfigurationdocument:1:0",
        },
    )
    description: Optional[str] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "urn:iec62325.351:tc57wg16:451-n:mltopconfigurationdocument:1:0",
        },
    )
    owner_market_participant_m_rid: Optional[PartyIdString] = field(
        default=None,
        metadata={
            "name": "owner_MarketParticipant.mRID",
            "type": "Element",
            "namespace": "urn:iec62325.351:tc57wg16:451-n:mltopconfigurationdocument:1:0",
            "required": True,
        },
    )
    start_lifetime_date_and_or_time_date: Optional[XmlDate] = field(
        default=None,
        metadata={
            "name": "startLifetime_DateAndOrTime.date",
            "type": "Element",
            "namespace": "urn:iec62325.351:tc57wg16:451-n:mltopconfigurationdocument:1:0",
            "required": True,
        },
    )
    end_lifetime_date_and_or_time_date: Optional[XmlDate] = field(
        default=None,
        metadata={
            "name": "endLifetime_DateAndOrTime.date",
            "type": "Element",
            "namespace": "urn:iec62325.351:tc57wg16:451-n:mltopconfigurationdocument:1:0",
        },
    )
    implementation_date_and_or_time_date: Optional[XmlDate] = field(
        default=None,
        metadata={
            "name": "implementation_DateAndOrTime.date",
            "type": "Element",
            "namespace": "urn:iec62325.351:tc57wg16:451-n:mltopconfigurationdocument:1:0",
        },
    )
    active_measurement_unit_name: Optional[UnitOfMeasureTypeList] = field(
        default=None,
        metadata={
            "name": "active_Measurement_Unit.name",
            "type": "Element",
            "namespace": "urn:iec62325.351:tc57wg16:451-n:mltopconfigurationdocument:1:0",
        },
    )
    installed_generation_quantity_quantity: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "installedGeneration_Quantity.quantity",
            "type": "Element",
            "namespace": "urn:iec62325.351:tc57wg16:451-n:mltopconfigurationdocument:1:0",
        },
    )
    installed_consumption_quantity_quantity: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "installedConsumption_Quantity.quantity",
            "type": "Element",
            "namespace": "urn:iec62325.351:tc57wg16:451-n:mltopconfigurationdocument:1:0",
        },
    )
    installed_reactive_quantity_quantity: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "installedReactive_Quantity.quantity",
            "type": "Element",
            "namespace": "urn:iec62325.351:tc57wg16:451-n:mltopconfigurationdocument:1:0",
        },
    )
    reactive_measurement_unit_name: Optional[UnitOfMeasureTypeList] = field(
        default=None,
        metadata={
            "name": "reactive_Measurement_Unit.name",
            "type": "Element",
            "namespace": "urn:iec62325.351:tc57wg16:451-n:mltopconfigurationdocument:1:0",
        },
    )
    multipod_registered_resource_m_rid: Optional[ResourceIdString] = field(
        default=None,
        metadata={
            "name": "multipod_RegisteredResource.mRID",
            "type": "Element",
            "namespace": "urn:iec62325.351:tc57wg16:451-n:mltopconfigurationdocument:1:0",
        },
    )
    domain: list[Domain] = field(
        default_factory=list,
        metadata={
            "name": "Domain",
            "type": "Element",
            "namespace": "urn:iec62325.351:tc57wg16:451-n:mltopconfigurationdocument:1:0",
            "min_occurs": 1,
        },
    )
    coordination_market_participant: list[OtherMarketParticipant] = field(
        default_factory=list,
        metadata={
            "name": "Coordination_MarketParticipant",
            "type": "Element",
            "namespace": "urn:iec62325.351:tc57wg16:451-n:mltopconfigurationdocument:1:0",
        },
    )
    interested_market_participant: list[OtherMarketParticipant] = field(
        default_factory=list,
        metadata={
            "name": "Interested_MarketParticipant",
            "type": "Element",
            "namespace": "urn:iec62325.351:tc57wg16:451-n:mltopconfigurationdocument:1:0",
        },
    )
    specific_registered_resource: list[SpecificRegisteredResource] = field(
        default_factory=list,
        metadata={
            "name": "Specific_RegisteredResource",
            "type": "Element",
            "namespace": "urn:iec62325.351:tc57wg16:451-n:mltopconfigurationdocument:1:0",
        },
    )


@dataclass
class RefMarketDocument:
    class Meta:
        name = "Ref_MarketDocument"
        namespace = "urn:iec62325.351:tc57wg16:451-n:mltopconfigurationdocument:1:0"

    m_rid: Optional[str] = field(
        default=None,
        metadata={
            "name": "mRID",
            "type": "Element",
            "required": True,
            "max_length": 35,
        },
    )
    type_value: Optional[MessageTypeList] = field(
        default=None,
        metadata={
            "name": "type",
            "type": "Element",
            "required": True,
        },
    )
    process_process_type: Optional[ProcessTypeList] = field(
        default=None,
        metadata={
            "name": "process.processType",
            "type": "Element",
            "required": True,
        },
    )
    sender_market_participant_m_rid: Optional[PartyIdString] = field(
        default=None,
        metadata={
            "name": "sender_MarketParticipant.mRID",
            "type": "Element",
            "required": True,
        },
    )
    sender_market_participant_market_role_type: Optional[RoleTypeList] = field(
        default=None,
        metadata={
            "name": "sender_MarketParticipant.marketRole.type",
            "type": "Element",
            "required": True,
        },
    )
    receiver_market_participant_m_rid: Optional[PartyIdString] = field(
        default=None,
        metadata={
            "name": "receiver_MarketParticipant.mRID",
            "type": "Element",
            "required": True,
        },
    )
    receiver_market_participant_market_role_type: Optional[RoleTypeList] = field(
        default=None,
        metadata={
            "name": "receiver_MarketParticipant.marketRole.type",
            "type": "Element",
            "required": True,
        },
    )
    created_date_time: Optional[str] = field(
        default=None,
        metadata={
            "name": "createdDateTime",
            "type": "Element",
            "required": True,
            "pattern": r"((([0-9]{4})[\-](0[13578]|1[02])[\-](0[1-9]|[12][0-9]|3[01])|([0-9]{4})[\-]((0[469])|(11))[\-](0[1-9]|[12][0-9]|30))T(([01][0-9]|2[0-3]):[0-5][0-9]:[0-5][0-9])Z)|(([13579][26][02468][048]|[13579][01345789](0)[48]|[13579][01345789][2468][048]|[02468][048][02468][048]|[02468][1235679](0)[48]|[02468][1235679][2468][048]|[0-9][0-9][13579][26])[\-](02)[\-](0[1-9]|1[0-9]|2[0-9])T(([01][0-9]|2[0-3]):[0-5][0-9]:[0-5][0-9])Z)|(([13579][26][02468][1235679]|[13579][01345789](0)[01235679]|[13579][01345789][2468][1235679]|[02468][048][02468][1235679]|[02468][1235679](0)[01235679]|[02468][1235679][2468][1235679]|[0-9][0-9][13579][01345789])[\-](02)[\-](0[1-9]|1[0-9]|2[0-8])T(([01][0-9]|2[0-3]):[0-5][0-9]:[0-5][0-9])Z)",
        },
    )
    time_series: list[TimeSeries] = field(
        default_factory=list,
        metadata={
            "name": "TimeSeries",
            "type": "Element",
            "min_occurs": 1,
        },
    )

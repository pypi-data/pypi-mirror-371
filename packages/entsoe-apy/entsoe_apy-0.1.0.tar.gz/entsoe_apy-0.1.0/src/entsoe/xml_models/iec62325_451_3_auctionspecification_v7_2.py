from dataclasses import dataclass, field
from decimal import Decimal
from typing import Optional

from xsdata.models.datatype import XmlDuration

from .urn_entsoe_eu_wgedi_codelists import (
    AllocationModeTypeList,
    AuctionTypeList,
    BusinessTypeList,
    CategoryTypeList,
    CodingSchemeTypeList,
    ContractTypeList,
    CurrencyTypeList,
    CurveTypeList,
    IndicatorTypeList,
    MessageTypeList,
    PaymentTermsTypeList,
    ProcessTypeList,
    ReasonCodeTypeList,
    RightsTypeList,
    RoleTypeList,
    UnitOfMeasureTypeList,
)

__NAMESPACE__ = "urn:iec62325.351:tc57wg16:451-3:capacityspecificationdocument:7:2"


@dataclass
class AttributeInstanceComponent:
    position: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "urn:iec62325.351:tc57wg16:451-3:capacityspecificationdocument:7:2",
            "required": True,
            "min_inclusive": 1,
            "max_inclusive": 999999,
        },
    )
    attribute: Optional[str] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "urn:iec62325.351:tc57wg16:451-3:capacityspecificationdocument:7:2",
            "required": True,
        },
    )


@dataclass
class EsmpDateTimeInterval:
    class Meta:
        name = "ESMP_DateTimeInterval"

    start: Optional[str] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "urn:iec62325.351:tc57wg16:451-3:capacityspecificationdocument:7:2",
            "required": True,
            "pattern": r"((([0-9]{4})[\-](0[13578]|1[02])[\-](0[1-9]|[12][0-9]|3[01])|([0-9]{4})[\-]((0[469])|(11))[\-](0[1-9]|[12][0-9]|30))T(([01][0-9]|2[0-3]):[0-5][0-9])Z)|(([13579][26][02468][048]|[13579][01345789](0)[48]|[13579][01345789][2468][048]|[02468][048][02468][048]|[02468][1235679](0)[48]|[02468][1235679][2468][048]|[0-9][0-9][13579][26])[\-](02)[\-](0[1-9]|1[0-9]|2[0-9])T(([01][0-9]|2[0-3]):[0-5][0-9])Z)|(([13579][26][02468][1235679]|[13579][01345789](0)[01235679]|[13579][01345789][2468][1235679]|[02468][048][02468][1235679]|[02468][1235679](0)[01235679]|[02468][1235679][2468][1235679]|[0-9][0-9][13579][01345789])[\-](02)[\-](0[1-9]|1[0-9]|2[0-8])T(([01][0-9]|2[0-3]):[0-5][0-9])Z)",
        },
    )
    end: Optional[str] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "urn:iec62325.351:tc57wg16:451-3:capacityspecificationdocument:7:2",
            "required": True,
            "pattern": r"((([0-9]{4})[\-](0[13578]|1[02])[\-](0[1-9]|[12][0-9]|3[01])|([0-9]{4})[\-]((0[469])|(11))[\-](0[1-9]|[12][0-9]|30))T(([01][0-9]|2[0-3]):[0-5][0-9])Z)|(([13579][26][02468][048]|[13579][01345789](0)[48]|[13579][01345789][2468][048]|[02468][048][02468][048]|[02468][1235679](0)[48]|[02468][1235679][2468][048]|[0-9][0-9][13579][26])[\-](02)[\-](0[1-9]|1[0-9]|2[0-9])T(([01][0-9]|2[0-3]):[0-5][0-9])Z)|(([13579][26][02468][1235679]|[13579][01345789](0)[01235679]|[13579][01345789][2468][1235679]|[02468][048][02468][1235679]|[02468][1235679](0)[01235679]|[02468][1235679][2468][1235679]|[0-9][0-9][13579][01345789])[\-](02)[\-](0[1-9]|1[0-9]|2[0-8])T(([01][0-9]|2[0-3]):[0-5][0-9])Z)",
        },
    )


@dataclass
class Point:
    position: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "urn:iec62325.351:tc57wg16:451-3:capacityspecificationdocument:7:2",
            "required": True,
            "min_inclusive": 1,
            "max_inclusive": 999999,
        },
    )
    quantity: Optional[Decimal] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "urn:iec62325.351:tc57wg16:451-3:capacityspecificationdocument:7:2",
            "required": True,
        },
    )


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
class Reason:
    code: Optional[ReasonCodeTypeList] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "urn:iec62325.351:tc57wg16:451-3:capacityspecificationdocument:7:2",
            "required": True,
        },
    )
    text: Optional[str] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "urn:iec62325.351:tc57wg16:451-3:capacityspecificationdocument:7:2",
            "max_length": 512,
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
class RightsCharacteristicsAuction:
    class Meta:
        name = "RightsCharacteristics_Auction"

    rights: Optional[RightsTypeList] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "urn:iec62325.351:tc57wg16:451-3:capacityspecificationdocument:7:2",
            "required": True,
        },
    )


@dataclass
class SeriesPeriod:
    class Meta:
        name = "Series_Period"

    time_interval: Optional[EsmpDateTimeInterval] = field(
        default=None,
        metadata={
            "name": "timeInterval",
            "type": "Element",
            "namespace": "urn:iec62325.351:tc57wg16:451-3:capacityspecificationdocument:7:2",
            "required": True,
        },
    )
    resolution: Optional[XmlDuration] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "urn:iec62325.351:tc57wg16:451-3:capacityspecificationdocument:7:2",
            "required": True,
        },
    )
    point: list[Point] = field(
        default_factory=list,
        metadata={
            "name": "Point",
            "type": "Element",
            "namespace": "urn:iec62325.351:tc57wg16:451-3:capacityspecificationdocument:7:2",
            "min_occurs": 1,
        },
    )


@dataclass
class AuctionTimeSeries:
    class Meta:
        name = "Auction_TimeSeries"

    m_rid: Optional[str] = field(
        default=None,
        metadata={
            "name": "mRID",
            "type": "Element",
            "namespace": "urn:iec62325.351:tc57wg16:451-3:capacityspecificationdocument:7:2",
            "required": True,
            "max_length": 60,
        },
    )
    business_type: Optional[BusinessTypeList] = field(
        default=None,
        metadata={
            "name": "businessType",
            "type": "Element",
            "namespace": "urn:iec62325.351:tc57wg16:451-3:capacityspecificationdocument:7:2",
            "required": True,
        },
    )
    auction_category: Optional[CategoryTypeList] = field(
        default=None,
        metadata={
            "name": "auction.category",
            "type": "Element",
            "namespace": "urn:iec62325.351:tc57wg16:451-3:capacityspecificationdocument:7:2",
            "required": True,
        },
    )
    auction_type: Optional[AuctionTypeList] = field(
        default=None,
        metadata={
            "name": "auction.type",
            "type": "Element",
            "namespace": "urn:iec62325.351:tc57wg16:451-3:capacityspecificationdocument:7:2",
            "required": True,
        },
    )
    auction_allocation_mode: Optional[AllocationModeTypeList] = field(
        default=None,
        metadata={
            "name": "auction.allocationMode",
            "type": "Element",
            "namespace": "urn:iec62325.351:tc57wg16:451-3:capacityspecificationdocument:7:2",
            "required": True,
        },
    )
    auction_payment_terms: Optional[PaymentTermsTypeList] = field(
        default=None,
        metadata={
            "name": "auction.paymentTerms",
            "type": "Element",
            "namespace": "urn:iec62325.351:tc57wg16:451-3:capacityspecificationdocument:7:2",
            "required": True,
        },
    )
    auction_cancelled: Optional[IndicatorTypeList] = field(
        default=None,
        metadata={
            "name": "auction.cancelled",
            "type": "Element",
            "namespace": "urn:iec62325.351:tc57wg16:451-3:capacityspecificationdocument:7:2",
        },
    )
    bidding_period_time_interval: Optional[EsmpDateTimeInterval] = field(
        default=None,
        metadata={
            "name": "bidding_Period.timeInterval",
            "type": "Element",
            "namespace": "urn:iec62325.351:tc57wg16:451-3:capacityspecificationdocument:7:2",
            "required": True,
        },
    )
    in_domain_m_rid: Optional[AreaIdString] = field(
        default=None,
        metadata={
            "name": "in_Domain.mRID",
            "type": "Element",
            "namespace": "urn:iec62325.351:tc57wg16:451-3:capacityspecificationdocument:7:2",
            "required": True,
        },
    )
    out_domain_m_rid: Optional[AreaIdString] = field(
        default=None,
        metadata={
            "name": "out_Domain.mRID",
            "type": "Element",
            "namespace": "urn:iec62325.351:tc57wg16:451-3:capacityspecificationdocument:7:2",
            "required": True,
        },
    )
    market_agreement_type: Optional[ContractTypeList] = field(
        default=None,
        metadata={
            "name": "marketAgreement.type",
            "type": "Element",
            "namespace": "urn:iec62325.351:tc57wg16:451-3:capacityspecificationdocument:7:2",
            "required": True,
        },
    )
    delivery_period_time_interval: Optional[EsmpDateTimeInterval] = field(
        default=None,
        metadata={
            "name": "delivery_Period.timeInterval",
            "type": "Element",
            "namespace": "urn:iec62325.351:tc57wg16:451-3:capacityspecificationdocument:7:2",
            "required": True,
        },
    )
    quantity_measurement_unit_name: Optional[UnitOfMeasureTypeList] = field(
        default=None,
        metadata={
            "name": "quantity_Measurement_Unit.name",
            "type": "Element",
            "namespace": "urn:iec62325.351:tc57wg16:451-3:capacityspecificationdocument:7:2",
            "required": True,
        },
    )
    price_measurement_unit_name: Optional[UnitOfMeasureTypeList] = field(
        default=None,
        metadata={
            "name": "price_Measurement_Unit.name",
            "type": "Element",
            "namespace": "urn:iec62325.351:tc57wg16:451-3:capacityspecificationdocument:7:2",
            "required": True,
        },
    )
    currency_unit_name: Optional[CurrencyTypeList] = field(
        default=None,
        metadata={
            "name": "currency_Unit.name",
            "type": "Element",
            "namespace": "urn:iec62325.351:tc57wg16:451-3:capacityspecificationdocument:7:2",
            "required": True,
        },
    )
    notification_market_agreement_created_date_time: Optional[str] = field(
        default=None,
        metadata={
            "name": "notification_MarketAgreement.createdDateTime",
            "type": "Element",
            "namespace": "urn:iec62325.351:tc57wg16:451-3:capacityspecificationdocument:7:2",
            "required": True,
            "pattern": r"((([0-9]{4})[\-](0[13578]|1[02])[\-](0[1-9]|[12][0-9]|3[01])|([0-9]{4})[\-]((0[469])|(11))[\-](0[1-9]|[12][0-9]|30))T(([01][0-9]|2[0-3]):[0-5][0-9]:[0-5][0-9])Z)|(([13579][26][02468][048]|[13579][01345789](0)[48]|[13579][01345789][2468][048]|[02468][048][02468][048]|[02468][1235679](0)[48]|[02468][1235679][2468][048]|[0-9][0-9][13579][26])[\-](02)[\-](0[1-9]|1[0-9]|2[0-9])T(([01][0-9]|2[0-3]):[0-5][0-9]:[0-5][0-9])Z)|(([13579][26][02468][1235679]|[13579][01345789](0)[01235679]|[13579][01345789][2468][1235679]|[02468][048][02468][1235679]|[02468][1235679](0)[01235679]|[02468][1235679][2468][1235679]|[0-9][0-9][13579][01345789])[\-](02)[\-](0[1-9]|1[0-9]|2[0-8])T(([01][0-9]|2[0-3]):[0-5][0-9]:[0-5][0-9])Z)",
        },
    )
    contestation_market_agreement_created_date_time: Optional[str] = field(
        default=None,
        metadata={
            "name": "contestation_MarketAgreement.createdDateTime",
            "type": "Element",
            "namespace": "urn:iec62325.351:tc57wg16:451-3:capacityspecificationdocument:7:2",
            "required": True,
            "pattern": r"((([0-9]{4})[\-](0[13578]|1[02])[\-](0[1-9]|[12][0-9]|3[01])|([0-9]{4})[\-]((0[469])|(11))[\-](0[1-9]|[12][0-9]|30))T(([01][0-9]|2[0-3]):[0-5][0-9]:[0-5][0-9])Z)|(([13579][26][02468][048]|[13579][01345789](0)[48]|[13579][01345789][2468][048]|[02468][048][02468][048]|[02468][1235679](0)[48]|[02468][1235679][2468][048]|[0-9][0-9][13579][26])[\-](02)[\-](0[1-9]|1[0-9]|2[0-9])T(([01][0-9]|2[0-3]):[0-5][0-9]:[0-5][0-9])Z)|(([13579][26][02468][1235679]|[13579][01345789](0)[01235679]|[13579][01345789][2468][1235679]|[02468][048][02468][1235679]|[02468][1235679](0)[01235679]|[02468][1235679][2468][1235679]|[0-9][0-9][13579][01345789])[\-](02)[\-](0[1-9]|1[0-9]|2[0-8])T(([01][0-9]|2[0-3]):[0-5][0-9]:[0-5][0-9])Z)",
        },
    )
    publication_market_agreement_created_date_time: Optional[str] = field(
        default=None,
        metadata={
            "name": "publication_MarketAgreement.createdDateTime",
            "type": "Element",
            "namespace": "urn:iec62325.351:tc57wg16:451-3:capacityspecificationdocument:7:2",
            "required": True,
            "pattern": r"((([0-9]{4})[\-](0[13578]|1[02])[\-](0[1-9]|[12][0-9]|3[01])|([0-9]{4})[\-]((0[469])|(11))[\-](0[1-9]|[12][0-9]|30))T(([01][0-9]|2[0-3]):[0-5][0-9]:[0-5][0-9])Z)|(([13579][26][02468][048]|[13579][01345789](0)[48]|[13579][01345789][2468][048]|[02468][048][02468][048]|[02468][1235679](0)[48]|[02468][1235679][2468][048]|[0-9][0-9][13579][26])[\-](02)[\-](0[1-9]|1[0-9]|2[0-9])T(([01][0-9]|2[0-3]):[0-5][0-9]:[0-5][0-9])Z)|(([13579][26][02468][1235679]|[13579][01345789](0)[01235679]|[13579][01345789][2468][1235679]|[02468][048][02468][1235679]|[02468][1235679](0)[01235679]|[02468][1235679][2468][1235679]|[0-9][0-9][13579][01345789])[\-](02)[\-](0[1-9]|1[0-9]|2[0-8])T(([01][0-9]|2[0-3]):[0-5][0-9]:[0-5][0-9])Z)",
        },
    )
    resale_market_agreement_created_date_time: Optional[str] = field(
        default=None,
        metadata={
            "name": "resale_MarketAgreement.createdDateTime",
            "type": "Element",
            "namespace": "urn:iec62325.351:tc57wg16:451-3:capacityspecificationdocument:7:2",
            "pattern": r"((([0-9]{4})[\-](0[13578]|1[02])[\-](0[1-9]|[12][0-9]|3[01])|([0-9]{4})[\-]((0[469])|(11))[\-](0[1-9]|[12][0-9]|30))T(([01][0-9]|2[0-3]):[0-5][0-9]:[0-5][0-9])Z)|(([13579][26][02468][048]|[13579][01345789](0)[48]|[13579][01345789][2468][048]|[02468][048][02468][048]|[02468][1235679](0)[48]|[02468][1235679][2468][048]|[0-9][0-9][13579][26])[\-](02)[\-](0[1-9]|1[0-9]|2[0-9])T(([01][0-9]|2[0-3]):[0-5][0-9]:[0-5][0-9])Z)|(([13579][26][02468][1235679]|[13579][01345789](0)[01235679]|[13579][01345789][2468][1235679]|[02468][048][02468][1235679]|[02468][1235679](0)[01235679]|[02468][1235679][2468][1235679]|[0-9][0-9][13579][01345789])[\-](02)[\-](0[1-9]|1[0-9]|2[0-8])T(([01][0-9]|2[0-3]):[0-5][0-9]:[0-5][0-9])Z)",
        },
    )
    curve_type: Optional[CurveTypeList] = field(
        default=None,
        metadata={
            "name": "curveType",
            "type": "Element",
            "namespace": "urn:iec62325.351:tc57wg16:451-3:capacityspecificationdocument:7:2",
            "required": True,
        },
    )
    connecting_line_registered_resource_m_rid: Optional[ResourceIdString] = field(
        default=None,
        metadata={
            "name": "connectingLine_RegisteredResource.mRID",
            "type": "Element",
            "namespace": "urn:iec62325.351:tc57wg16:451-3:capacityspecificationdocument:7:2",
        },
    )
    period: list[SeriesPeriod] = field(
        default_factory=list,
        metadata={
            "name": "Period",
            "type": "Element",
            "namespace": "urn:iec62325.351:tc57wg16:451-3:capacityspecificationdocument:7:2",
        },
    )
    auction_description_attribute_instance_component: list[
        AttributeInstanceComponent
    ] = field(
        default_factory=list,
        metadata={
            "name": "AuctionDescription_AttributeInstanceComponent",
            "type": "Element",
            "namespace": "urn:iec62325.351:tc57wg16:451-3:capacityspecificationdocument:7:2",
        },
    )
    rights_characteristics_auction: list[RightsCharacteristicsAuction] = field(
        default_factory=list,
        metadata={
            "name": "RightsCharacteristics_Auction",
            "type": "Element",
            "namespace": "urn:iec62325.351:tc57wg16:451-3:capacityspecificationdocument:7:2",
        },
    )
    reason: list[Reason] = field(
        default_factory=list,
        metadata={
            "name": "Reason",
            "type": "Element",
            "namespace": "urn:iec62325.351:tc57wg16:451-3:capacityspecificationdocument:7:2",
        },
    )


@dataclass
class CapacityAuctionSpecificationMarketDocument:
    class Meta:
        name = "CapacityAuctionSpecification_MarketDocument"
        namespace = "urn:iec62325.351:tc57wg16:451-3:capacityspecificationdocument:7:2"

    m_rid: Optional[str] = field(
        default=None,
        metadata={
            "name": "mRID",
            "type": "Element",
            "required": True,
            "max_length": 60,
        },
    )
    revision_number: Optional[str] = field(
        default=None,
        metadata={
            "name": "revisionNumber",
            "type": "Element",
            "required": True,
            "pattern": r"[1-9]([0-9]){0,2}",
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
        },
    )
    receiver_market_participant_market_role_type: Optional[RoleTypeList] = field(
        default=None,
        metadata={
            "name": "receiver_MarketParticipant.marketRole.type",
            "type": "Element",
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
    period_time_interval: Optional[EsmpDateTimeInterval] = field(
        default=None,
        metadata={
            "name": "period.timeInterval",
            "type": "Element",
            "required": True,
        },
    )
    domain_m_rid: Optional[AreaIdString] = field(
        default=None,
        metadata={
            "name": "domain.mRID",
            "type": "Element",
            "required": True,
        },
    )
    auction_time_series: list[AuctionTimeSeries] = field(
        default_factory=list,
        metadata={
            "name": "Auction_TimeSeries",
            "type": "Element",
            "min_occurs": 1,
        },
    )

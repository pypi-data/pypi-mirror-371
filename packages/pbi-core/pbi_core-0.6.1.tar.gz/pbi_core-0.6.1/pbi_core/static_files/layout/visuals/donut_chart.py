from pydantic import ConfigDict, Field

from pbi_core.static_files.layout._base_node import LayoutNode
from pbi_core.static_files.layout.selector import Selector

from .base import BaseVisual
from .column_property import ColumnProperty
from .properties.base import Expression


class BackgroundProperties(LayoutNode):
    class _BackgroundPropertiesHelper(LayoutNode):
        show: Expression | None = None
        transparency: Expression | None = None

    properties: _BackgroundPropertiesHelper = Field(default_factory=_BackgroundPropertiesHelper)


class DataPointProperties(LayoutNode):
    class _DataPointPropertiesHelper(LayoutNode):
        fill: Expression | None = None

    properties: _DataPointPropertiesHelper = Field(default_factory=_DataPointPropertiesHelper)
    selector: Selector | None = None


class GeneralProperties(LayoutNode):
    class _GeneralPropertiesHelper(LayoutNode):
        altText: Expression | None = None

    properties: _GeneralPropertiesHelper = Field(default_factory=_GeneralPropertiesHelper)


class LabelsProperties(LayoutNode):
    class _LabelsPropertiesHelper(LayoutNode):
        background: Expression | None = None
        color: Expression | None = None
        fontFamily: Expression | None = None
        fontSize: Expression | None = None
        labelDisplayUnits: Expression | None = None
        labelStyle: Expression | None = None
        overflow: Expression | None = None
        percentageLabelPrecision: Expression | None = None
        position: Expression | None = None
        show: Expression | None = None

    properties: _LabelsPropertiesHelper = Field(default_factory=_LabelsPropertiesHelper)


class LegendProperties(LayoutNode):
    class _LegendPropertiesHelper(LayoutNode):
        fontSize: Expression | None = None
        labelColor: Expression | None = None
        position: Expression | None = None
        show: Expression | None = None
        showTitle: Expression | None = None

    properties: _LegendPropertiesHelper = Field(default_factory=_LegendPropertiesHelper)


class SlicesProperties(LayoutNode):
    class _SlicesPropertiesHelper(LayoutNode):
        innerRadiusRatio: Expression | None = None

    properties: _SlicesPropertiesHelper = Field(default_factory=_SlicesPropertiesHelper)


class TitleProperties(LayoutNode):
    class _TitlePropertiesHelper(LayoutNode):
        alignment: Expression | None = None
        fontColor: Expression | None = None
        fontSize: Expression | None = None
        show: Expression | None = None
        text: Expression | None = None

    properties: _TitlePropertiesHelper = Field(default_factory=_TitlePropertiesHelper)


class DonutChartProperties(LayoutNode):
    background: list[BackgroundProperties] | None = Field(default_factory=lambda: [BackgroundProperties()])
    dataPoint: list[DataPointProperties] | None = Field(default_factory=lambda: [DataPointProperties()])
    general: list[GeneralProperties] | None = Field(default_factory=lambda: [GeneralProperties()])
    labels: list[LabelsProperties] | None = Field(default_factory=lambda: [LabelsProperties()])
    legend: list[LegendProperties] | None = Field(default_factory=lambda: [LegendProperties()])
    slices: list[SlicesProperties] | None = Field(default_factory=lambda: [SlicesProperties()])
    title: list[TitleProperties] | None = Field(default_factory=lambda: [TitleProperties()])


class DonutChart(BaseVisual):
    visualType: str = "donutChart"
    model_config = ConfigDict(extra="forbid")

    columnProperties: dict[str, ColumnProperty] | None = None
    drillFilterOtherVisuals: bool = True
    objects: DonutChartProperties | None = Field(default_factory=DonutChartProperties)

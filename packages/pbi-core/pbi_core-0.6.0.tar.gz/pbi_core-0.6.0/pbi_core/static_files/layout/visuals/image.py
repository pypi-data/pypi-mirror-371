from pydantic import ConfigDict, Field

from pbi_core.static_files.layout._base_node import LayoutNode

from .base import BaseVisual
from .column_property import ColumnProperty
from .properties.base import Expression


class GeneralProperties(LayoutNode):
    class _GeneralPropertiesHelper(LayoutNode):
        imageUrl: Expression | None = None

    properties: _GeneralPropertiesHelper = Field(default_factory=_GeneralPropertiesHelper)


class ImageScalingProperties(LayoutNode):
    class _ImageScalingPropertiesHelper(LayoutNode):
        imageScalingType: Expression | None = None

    properties: _ImageScalingPropertiesHelper = Field(default_factory=_ImageScalingPropertiesHelper)


class ImageProperties(LayoutNode):
    general: list[GeneralProperties] | None = Field(default_factory=list[GeneralProperties()])
    imageScaling: list[ImageScalingProperties] | None = Field(default_factory=list[ImageScalingProperties()])


class Image(BaseVisual):
    visualType: str = "image"
    model_config = ConfigDict(extra="forbid")

    columnProperties: dict[str, ColumnProperty] | None = None
    drillFilterOtherVisuals: bool = True
    objects: ImageProperties | None = Field(default_factory=ImageProperties)

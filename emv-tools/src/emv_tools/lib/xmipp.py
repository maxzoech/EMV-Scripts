from ..ffi.scipion import xmipp_transform_filter, xmipp_image_resize
from ..utils.proxy import proxify, OutputInfo


transform_filter = proxify(
    xmipp_transform_filter,
    outputs=OutputInfo("outputs", file_ext="vol")
)

image_resize = proxify(
    xmipp_image_resize,
    outputs=OutputInfo("outputs", file_ext="vol")
)


__all__ = [
    transform_filter, image_resize
]
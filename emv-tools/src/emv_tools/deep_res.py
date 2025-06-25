import os

import numpy as np
import xmippLib
from .ffi.scipion import *
from .utils.proxy import Proxy, TempFileProxy, OutputInfo
from .utils.conversion import load_cif_as_pdb
from .utils.validate_pdb import validate_pdb_lines

from functools import partial
from copy import copy
from typing import List
import tempfile

from emv_tools.download import EMDBMetadata, download_emdb_map, download_emdb_metadata, download_pdb_model


@proxify
def resize_output_volume(output_volume, resolution: int, size: int):
    if resolution >= 2.7:
        resize_samp = 1.0
    else:
        resize_samp = 0.5

    out_v = xmippLib.Image(output_volume).getData()
    z, _, _ = out_v.shape

    factor = size / z
    final_samp = resize_samp / factor
    fourier_v = resize_samp / 2 * final_samp

    output = xmipp_transform_filter(
        output_volume,
        OutputInfo("vol"),
        fourier="low_pass %f" % fourier_v
    )

    return xmipp_image_resize(
        output,
        OutputInfo("vol"),
        dim=size
    )


def create_deepres_mask(pdb_file: str, emdb_map: str, metadata: EMDBMetadata):
    
    volume_pdb = xmipp_volume_from_pdb(
        pdb_file,
        OutputInfo(None),
        center_pdb="-v 0",
        sampling=metadata.sampling,
        size=metadata.size
    ).reassign("vol")

    aligned = xmipp_volume_align(
        OutputInfo(file_ext="vol"),
        embdb_map=emdb_map,
        volume=volume_pdb
    )

    mask = xmipp_transform_threshold(
        aligned,
        OutputInfo(file_ext="vol"),
        select="below 0.02",
        substitute="binarize"
    )

    mask = xmipp_transform_morphology(
        mask,
        OutputInfo("vol"),
        binary_operation="dilation",
        size=2
    )

    return mask


def main():

    os.makedirs("../data/input_data", exist_ok=True)

    # Download EMDB Info
    embd_map = "/home/max/Documents/val-server/data/val-report-service/EMD-41510/EMD-41510_ScipionProject/Runs/000002_ProtImportVolumes/extra/emd_41510.map"
    deepres_vol = "/home/max/Documents/val-server/data/val-report-service/EMD-41510/EMD-41510_ScipionProject/Runs/000727_XmippProtDeepRes/extra/deepRes_resolution_originalSize.vol"
    cif_path = "/home/max/Documents/val-server/data/val-report-service/EMD-41510/EMD-41510_ScipionProject/8tqo.cif"
    
    metadata = download_emdb_metadata(41510) # Get from header instead

    pdb_file = load_cif_as_pdb(cif_path)
    validate_pdb_lines(pdb_file)

    pdb_file = TempFileProxy.proxy_for_lines(pdb_file, file_ext="pdb")

    # Create DeepRes mask
    deepres_mask = create_deepres_mask(pdb_file, embd_map, metadata)
    deepres_mask = resize_output_volume(
        deepres_mask,
        metadata.resolution,
        metadata.size
    )

    # Resize the DeepRes volume
    volume_resized = resize_output_volume(
        deepres_vol,
        metadata.resolution,
        metadata.size
    )

    # Join the two parts
    xmipp_pdb_label_from_volume(
        os.path.abspath("../data/output.atom.pdb"), 
        pdb=pdb_file,
        volume=volume_resized,
        mask=deepres_mask,
        sampling=metadata.sampling,
        origin="%f %f %f" % (metadata.org_x, metadata.org_y, metadata.org_z),
    )



if __name__ == "__main__":
    main()
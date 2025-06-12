import requests
import json

from collections import namedtuple

EMDB_EBI_JSON_REPOSITORY = "https://www.ebi.ac.uk/emdb/api/entry/"

EMDBMetadata = namedtuple("EMDBMetadata", ("resolution", "sampling", "size", "org_x", "org_y", "org_z"))


def download_emdb_metadata(entry_id: int) -> EMDBMetadata:
    """
    Downloads metadata for an emdb entry
    
    Args:
        - entry: The EMDB ID to download. Use only the numbers after the 'EMD-' prefix
    """

    entry = f"EMD-{entry_id}"
    url = EMDB_EBI_JSON_REPOSITORY + entry
    
    response = requests.get(url)
    raw_data = json.loads(response.content)

    map_info = raw_data["map"]
    resolution = float(
        raw_data["structure_determination_list"]["structure_determination"][0]["image_processing"][0]["final_reconstruction"]["resolution"]["valueOf_"]
    )

    metadata = EMDBMetadata(
        resolution=resolution,
        sampling=float(map_info["pixel_spacing"]["y"]["valueOf_"]),
        size=int(map_info["dimensions"]["col"]),
        org_x=-(map_info["origin"]["col"]),
        org_y=-(map_info["origin"]["sec"]),
        org_z=-(map_info["origin"]["row"]),
    )

    return metadata

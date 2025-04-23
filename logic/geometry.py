import numpy as np

def get_bounding_box_centroid(mesh):
    """
    Gibt den Mittelpunkt der Bounding Box des Mesh als numpy‑Array zurück.
    """
    # mesh.bounds liefert [[min_x, min_y, min_z], [max_x, max_y, max_z]]
    min_bound, max_bound = mesh.bounds
    return np.mean([min_bound, max_bound], axis=0)



def extract_geometry_features(mesh):
    extents = mesh.bounding_box.extents
    return {
        "volume_mm3": mesh.volume,
        "surface_area_mm2": mesh.area,
        "bbox_x": extents[0],
        "bbox_y": extents[1],
        "bbox_z": extents[2],
        "centroid_x": mesh.centroid[0],
        "centroid_y": mesh.centroid[1],
        "centroid_z": mesh.centroid[2],
        "aspect_ratio": extents.max() / extents.min()
    }

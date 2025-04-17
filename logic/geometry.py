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

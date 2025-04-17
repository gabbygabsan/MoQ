import numpy as np

def is_symmetric(mesh, axis, tolerance=1e-2):
    mirrored = mesh.copy()
    if axis == 'x':
        mirrored.apply_scale([-1, 1, 1])
    elif axis == 'y':
        mirrored.apply_scale([1, -1, 1])
    elif axis == 'z':
        mirrored.apply_scale([1, 1, -1])
    
    return np.allclose(
        np.sort(mesh.vertices, axis=0),
        np.sort(mirrored.vertices, axis=0),
        atol=tolerance
    )

def get_symmetric_planes(mesh):
    return {
        'YZ': is_symmetric(mesh, 'x'),
        'XZ': is_symmetric(mesh, 'y'),
        'XY': is_symmetric(mesh, 'z')
    }

def analyze_parting_plane(mesh):
    symmetries = get_symmetric_planes(mesh)
    extents = mesh.bounding_box.extents

    area_map = {
        'YZ': extents[1] * extents[2],
        'XZ': extents[0] * extents[2],
        'XY': extents[0] * extents[1]
    }

    # Suche best_plane mit Symmetrie
    best_plane = None
    max_area = 0

    for plane in ['YZ', 'XZ', 'XY']:
        if symmetries[plane] and area_map[plane] > max_area:
            best_plane = plane
            max_area = area_map[plane]

    # Wenn keine Symmetrie gefunden wurde, nimm größte Fläche als fallback
    if best_plane is None:
        best_plane = max(area_map, key=area_map.get)

    # Normale der Trennfläche für Hinterschneidungsanalyse
    normal_map = {
        'YZ': np.array([1, 0, 0]),
        'XZ': np.array([0, 1, 0]),
        'XY': np.array([0, 0, 1])
    }
    undercuts = []
    normals = mesh.face_normals
    normal_axis = normal_map[best_plane]
    dot_products = np.dot(normals, normal_axis)
    undercuts = [i for i, dot in enumerate(dot_products) if dot < 0]

    return {
        'symmetries': [k for k, v in symmetries.items() if v],
        'best_plane': best_plane,
        'undercuts': undercuts
    }

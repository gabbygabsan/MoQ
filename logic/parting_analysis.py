import numpy as np
import trimesh

# 1) Symmetrieanalyse (aus altem Code übernommen)
def is_symmetric(mesh: trimesh.Trimesh, axis: str, tolerance: float = 1e-2) -> bool:
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

def get_symmetric_planes(mesh: trimesh.Trimesh) -> dict:
    return {
        'YZ': is_symmetric(mesh, 'x'),
        'XZ': is_symmetric(mesh, 'y'),
        'XY': is_symmetric(mesh, 'z'),
    }

# 2) Entformwinkel‑Compliance
def compute_draft_compliance(mesh: trimesh.Trimesh, axis: str, tolerance_deg: float = 3.0) -> float:
    normals = mesh.face_normals
    axis_vectors = {'XY': np.array([0, 0, 1]), 'XZ': np.array([0, 1, 0]), 'YZ': np.array([1, 0, 0])}
    v = axis_vectors[axis] / np.linalg.norm(axis_vectors[axis])
    angles = np.degrees(np.arccos(np.clip(np.abs(normals @ v), -1.0, 1.0)))
    return np.count_nonzero(angles <= tolerance_deg) / len(angles)

# 3) Unter­schnitte
def compute_undercut_ratio(mesh: trimesh.Trimesh, axis: str) -> float:
    normals = mesh.face_normals
    axis_vectors = {'XY': [0, 0, 1], 'XZ': [0, 1, 0], 'YZ': [1, 0, 0]}
    v = np.array(axis_vectors[axis]) / np.linalg.norm(axis_vectors[axis])
    return np.count_nonzero((normals @ v) < 0) / len(normals)

# 4) Parting‑Line‑Komplexität
def compute_parting_line_complexity(mesh: trimesh.Trimesh, axis: str) -> float:
    centroid = mesh.bounding_box.centroid
    normal = np.array({'XY': [0, 0, 1], 'XZ': [0, 1, 0], 'YZ': [1, 0, 0]}[axis])
    section = mesh.section(plane_origin=centroid, plane_normal=normal)
    if section is None:
        return 0.0
    planar = section.to_planar()
    return sum(path.length for path in planar.paths)

# 5) Kosmetik (Platzhalter)
def compute_cosmetic_coverage(mesh: trimesh.Trimesh, axis: str) -> float:
    return 0.0

# 6) Score‑berechnung und Auswahl
def select_parting_plane(mesh: trimesh.Trimesh,
                         weights: dict = None,
                         draft_tol: float = 3.0) -> str:
    axes = ['XY', 'XZ', 'YZ']
    if weights is None:
        weights = {'draft': 3.0, 'undercut': 4.0, 'complexity': 2.0, 'cosmetic': 1.0}

    # Metriken ermitteln
    draft_vals = {a: compute_draft_compliance(mesh, a, draft_tol) for a in axes}
    undercut_vals = {a: compute_undercut_ratio(mesh, a) for a in axes}
    complexity_vals = {a: compute_parting_line_complexity(mesh, a) for a in axes}
    max_comp = max(complexity_vals.values()) or 1.0
    cosmetic_vals = {a: compute_cosmetic_coverage(mesh, a) for a in axes}

    # Score
    scores = {}
    for a in axes:
        scores[a] = (
            weights['draft']    * (1.0 - draft_vals[a]) +
            weights['undercut'] *  undercut_vals[a] +
            weights['complexity'] * (complexity_vals[a] / max_comp) -
            weights['cosmetic']  *  cosmetic_vals[a]
        )

    # Beste Ebene
    best = min(scores, key=scores.get)

    # Symmetrie‑Bonus bei fast gleichen Scoress
    sym_axes = [a for a, ok in get_symmetric_planes(mesh).items() if ok]
    for a in sym_axes:
        if abs(scores[a] - scores[best]) < 0.01:
            return a
    return best

# 7) Alte analyze_parting_plane durch neue Fassung ersetzen
def analyze_parting_plane(mesh: trimesh.Trimesh) -> dict:
    sym = get_symmetric_planes(mesh)
    best = select_parting_plane(mesh)
    # Undercut‑Faces ermitteln
    axis_vec = {'XY': np.array([0,0,1]), 'XZ': np.array([0,1,0]), 'YZ': np.array([1,0,0])}[best]
    und = [
        idx for idx, n in enumerate(mesh.face_normals)
        if float(n @ axis_vec) < 0.0
    ]
    return {
        "symmetries": sym,
        "best_plane": best,
        "undercuts": und
    }
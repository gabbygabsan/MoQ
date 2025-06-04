import numpy as np
import trimesh

# Symmetrieanalyse (aus altem Code übernommen)
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

# Entformwinkel-Compliance
def compute_draft_compliance(mesh: trimesh.Trimesh, axis: str, tolerance_deg: float = 3.0) -> float:
    normals = mesh.face_normals
    axis_vectors = {'XY': np.array([0, 0, 1]), 'XZ': np.array([0, 1, 0]), 'YZ': np.array([1, 0, 0])}
    v = axis_vectors[axis] / np.linalg.norm(axis_vectors[axis])
    dots = np.dot(normals, v)
    angles = np.degrees(np.arccos(np.clip(np.abs(dots), -1.0, 1.0)))
    compliant = angles <= tolerance_deg
    return np.count_nonzero(compliant) / len(angles)

# Unter­schnitte
def compute_undercut_ratio(mesh: trimesh.Trimesh, axis: str) -> float:
    normals = mesh.face_normals
    axis_vectors = {'XY': [0, 0, 1], 'XZ': [0, 1, 0], 'YZ': [1, 0, 0]}
    v = np.array(axis_vectors[axis]) / np.linalg.norm(axis_vectors[axis])
    dots = np.dot(normals, v)
    undercuts = dots < 0
    return np.count_nonzero(undercuts) / len(dots)

# Parting-Line-Komplexität
def compute_parting_line_complexity(mesh: trimesh.Trimesh, axis: str) -> float:
    """
    Berechnet die Länge der Schnittkurve (Umfang) an der Trennebene als Komplexitätsmaß.
    Falls networkx fehlt oder ein Fehler auftritt, wird 0.0 zurückgegeben.
    """
    centroid = mesh.bounding_box.centroid
    normals = {'XY': [0, 0, 1], 'XZ': [0, 1, 0], 'YZ': [1, 0, 0]}
    normal = np.array(normals[axis])
    section = mesh.section(plane_origin=centroid, plane_normal=normal)
    if section is None:
        return 0.0
    try:
        planar_section, _ = section.to_planar()
        # Summiere die Längen aller Entities (Linien/Arcs) im Pfad
        total_length = 0.0
        for ent in planar_section.entities:
            # ent.length ist eine Methode, daher aufrufen
            length = ent.length()
            total_length += length
        return total_length
    except (ImportError, ModuleNotFoundError):
        # networkx nicht verfügbar, Komplexität nicht berechenbar
        return 0.0
    except Exception:
        # Allgemeiner Fehler bei Pfadbemaßung
        return 0.0

# Kosmetik (Platzhalter)
def compute_cosmetic_coverage(mesh: trimesh.Trimesh, axis: str) -> float:
    return 0.0

# Score-Berechnung und Auswahl
def select_parting_plane(mesh: trimesh.Trimesh,
                         weights: dict = None,
                         draft_tol: float = 3.0) -> str:
    axes = ['XY', 'XZ', 'YZ']
    if weights is None:
        weights = {'draft': 3.0, 'undercut': 4.0, 'complexity': 2.0, 'cosmetic': 1.0}

    draft_vals = {a: compute_draft_compliance(mesh, a, draft_tol) for a in axes}
    undercut_vals = {a: compute_undercut_ratio(mesh, a) for a in axes}
    complexity_vals = {a: compute_parting_line_complexity(mesh, a) for a in axes}
    max_comp = max(complexity_vals.values()) or 1.0
    cosmetic_vals = {a: compute_cosmetic_coverage(mesh, a) for a in axes}

    scores = {}
    for a in axes:
        scores[a] = (
            weights['draft'] * (1.0 - draft_vals[a]) +
            weights['undercut'] * undercut_vals[a] +
            weights['complexity'] * (complexity_vals[a] / max_comp) -
            weights['cosmetic'] * cosmetic_vals[a]
        )

    best = min(scores, key=scores.get)
    sym_axes = [a for a, ok in get_symmetric_planes(mesh).items() if ok]
    for a in sym_axes:
        if abs(scores[a] - scores[best]) < 0.01:
            return a
    return best

# Alte analyze_parting_plane durch neue Fassung ersetzen
def analyze_parting_plane(mesh: trimesh.Trimesh) -> dict:
    sym = get_symmetric_planes(mesh)
    best = select_parting_plane(mesh)
    axis_vec = {'XY': np.array([0,0,1]), 'XZ': np.array([0,1,0]), 'YZ': np.array([1,0,0])}[best]
    undercuts = [idx for idx, n in enumerate(mesh.face_normals) if float(np.dot(n, axis_vec)) < 0.0]
    return {"symmetries": sym, "best_plane": best, "undercuts": undercuts}

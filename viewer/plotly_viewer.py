import numpy as np
import plotly.graph_objects as go
import trimesh
import streamlit as st
from logic.parting_analysis import get_symmetric_planes

# Caching für volumetrische Samples, um lange Wartezeiten zu vermeiden
@st.cache_data(ttl=3600)
# Hinweis: Verwende st.cache_data statt st.cache, um volumetrische Samples zu cachen
def get_volume_samples(vertices: np.ndarray, faces: np.ndarray, count: int = 500) -> np.ndarray:
    """
    Berechnet volumetrische Samples für Heatmap-Creation und cached das Ergebnis.
    :param vertices: Mesh-Vertices als (N,3)-Array
    :param faces: Mesh-Faces als (M,3)-Array
    :param count: Anzahl Punkte
    :return: Array der Samples
    """
    mesh = trimesh.Trimesh(vertices=vertices, faces=faces)
    return trimesh.sample.volume_mesh(mesh, count=count)


def show_3d_plotly(mesh,
                   kanal_durchmesser=6.0,
                   abstand=8.0,
                   anzahl_x=2,
                   anzahl_y=0,
                   anzahl_z=0,
                   heatmap=False,
                   highlight_faces=None,
                   parting_plane_axis=None):
    """
    Visualisiert das 3D-Mesh mit Plotly in Streamlit und fügt Kanäle sowie Trennebene hinzu.
    """
    # Mesh-Daten
    vertices = np.asarray(mesh.vertices)
    faces = np.asarray(mesh.faces)
    x, y, z = vertices.T
    i, j, k = faces.T

    # Mesh-Farben und Highlight
    face_colors = ['mediumpurple'] * len(faces)
    if highlight_faces:
        for idx in highlight_faces:
            if 0 <= idx < len(face_colors):
                face_colors[idx] = 'red'
    mesh_trace = go.Mesh3d(
        x=x, y=y, z=z,
        i=i, j=j, k=k,
        facecolor=face_colors,
        opacity=1.0,
        lighting=dict(ambient=0.6, diffuse=0.6, specular=0.2, roughness=0.5),
        lightposition=dict(x=100, y=200, z=0),
        name="Bauteil"
    )
    fig = go.Figure(data=[mesh_trace])

    # Hilfsfunktion zum Hinzufügen von Kanälen
    def add_kanal(x_cyl, y_cyl, z_cyl, name):
        fig.add_trace(go.Surface(
            x=x_cyl, y=y_cyl, z=z_cyl,
            showscale=False,
            opacity=1.0,
            colorscale=[[0, 'lightblue'], [1, 'lightblue']],
            showlegend=True,
            name=name
        ))

    # Bounding Box & Zentrum
    bbox = mesh.bounding_box.extents
    center = mesh.bounding_box.centroid
    kanal_radius = kanal_durchmesser / 2
    theta = np.linspace(0, 2 * np.pi, 30)

    # Trennfläche
    if parting_plane_axis in ['XY', 'XZ', 'YZ']:
        plane_size = bbox * 1.2
        bounds = mesh.bounding_box.bounds
        symmetries = get_symmetric_planes(mesh)
        is_sym = symmetries.get(parting_plane_axis, False)

        grid = np.linspace(-plane_size[0] / 2, plane_size[0] / 2, 2)
        xx, yy = np.meshgrid(grid, grid)

        if parting_plane_axis == 'YZ':
            x_coord = bounds[1][0] if is_sym else center[0]
            x_plane = np.full_like(xx, x_coord)
            y_plane = yy + center[1]
            z_plane = xx + center[2]
        elif parting_plane_axis == 'XZ':
            y_coord = bounds[1][1] if is_sym else center[1]
            x_plane = xx + center[0]
            y_plane = np.full_like(xx, y_coord)
            z_plane = yy + center[2]
        else:  # 'XY'
            z_coord = bounds[1][2] if is_sym else center[2]
            x_plane = xx + center[0]
            y_plane = yy + center[1]
            z_plane = np.full_like(xx, z_coord)

        fig.add_trace(go.Surface(
            x=x_plane, y=y_plane, z=z_plane,
            opacity=0.3,
            showscale=False,
            colorscale=[[0, 'gray'], [1, 'gray']],
            name="Trennfläche"
        ))

    # Kühlkanäle X
    if anzahl_x > 0:
        spacing = bbox[1] / (anzahl_x + 1)
        z_grid = np.linspace(-bbox[0] * 0.45, bbox[0] * 0.45, 2)
        theta_grid, z_grid = np.meshgrid(theta, z_grid)
        for n in range(anzahl_x):
            offset = (n + 1) * spacing - bbox[1] / 2
            x_cyl = center[0] + z_grid
            y_cyl = center[1] + offset + kanal_radius * np.cos(theta_grid)
            z_cyl = center[2] - abstand + kanal_radius * np.sin(theta_grid)
            add_kanal(x_cyl, y_cyl, z_cyl, f"X-Kanal {n+1}")
    # Kühlkanäle Y
    if anzahl_y > 0:
        spacing = bbox[0] / (anzahl_y + 1)
        z_grid = np.linspace(-bbox[1] * 0.45, bbox[1] * 0.45, 2)
        theta_grid, z_grid = np.meshgrid(theta, z_grid)
        for n in range(anzahl_y):
            offset = (n + 1) * spacing - bbox[0] / 2
            x_cyl = center[0] + offset + kanal_radius * np.cos(theta_grid)
            y_cyl = center[1] + z_grid
            z_cyl = center[2] - abstand + kanal_radius * np.sin(theta_grid)
            add_kanal(x_cyl, y_cyl, z_cyl, f"Y-Kanal {n+1}")
    # Kühlkanäle Z
    if anzahl_z > 0:
        spacing = bbox[0] / (anzahl_z + 1)
        z_grid = np.linspace(-bbox[2] * 0.45, bbox[2] * 0.45, 2)
        theta_grid, z_grid = np.meshgrid(theta, z_grid)
        for n in range(anzahl_z):
            offset = (n + 1) * spacing - bbox[0] / 2
            x_cyl = center[0] + offset + kanal_radius * np.cos(theta_grid)
            y_cyl = center[1] + kanal_radius * np.sin(theta_grid)
            z_cyl = center[2] + z_grid
            add_kanal(x_cyl, y_cyl, z_cyl, f"Z-Kanal {n+1}")

    # Heatmap
    if heatmap:
        try:
            with st.spinner("Berechne Heatmap…"):
                samples = get_volume_samples(vertices, faces, count=500)
            values = np.exp(-np.linalg.norm(samples - center, axis=1)**2 / 5000)
            fig.add_trace(go.Volume(
                x=samples[:,0], y=samples[:,1], z=samples[:,2],
                value=values, isomin=0.1, isomax=1.0,
                opacity=1, surface_count=250,
                colorscale='Hot', showscale=True,
                name="Heatmap"
            ))
        except Exception as e:
            st.warning(f"Heatmap konnte nicht erzeugt werden: {e}")

    # Layout und Plot
    fig.update_layout(
        scene=dict(
            xaxis=dict(backgroundcolor="rgb(240,240,240)"),
            yaxis=dict(backgroundcolor="rgb(240,240,240)"),
            zaxis=dict(backgroundcolor="rgb(240,240,240)"),
            aspectmode='data'
        ),
        margin=dict(l=0, r=0, b=0, t=0),
        paper_bgcolor="white",
        plot_bgcolor="white"
    )
    st.plotly_chart(fig, use_container_width=True)

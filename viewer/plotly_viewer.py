import numpy as np
import plotly.graph_objects as go
import trimesh
import streamlit as st

def show_3d_plotly(mesh, kanal_durchmesser=6.0, abstand=8.0, anzahl_x=2, anzahl_y=0, anzahl_z=0,
                   heatmap=False, highlight_faces=None, parting_plane_axis=None):
    vertices = np.asarray(mesh.vertices)
    faces = np.asarray(mesh.faces)
    x, y, z = vertices.T
    i, j, k = faces.T

    # 🟥 Hinterschneidungen einfärben
    default_color = 'mediumpurple'
    highlight_color = 'red'
    face_colors = [default_color] * len(faces)
    if highlight_faces:
        for idx in highlight_faces:
            if 0 <= idx < len(face_colors):
                face_colors[idx] = highlight_color

    fig = go.Figure(data=[
        go.Mesh3d(
            x=x, y=y, z=z,
            i=i, j=j, k=k,
            facecolor=face_colors,
            opacity=1.0,
            name="Bauteil"
        )
    ])

    bbox = mesh.bounding_box.extents
    center = mesh.bounding_box.centroid
    kanal_radius = kanal_durchmesser / 2
    resolution = 30
    theta = np.linspace(0, 2 * np.pi, resolution)

    def add_kanal(x_cyl, y_cyl, z_cyl, label):
        fig.add_trace(go.Surface(
            x=x_cyl, y=y_cyl, z=z_cyl,
            showscale=False,
            colorscale=[[0, 'blue'], [1, 'blue']],
            opacity=1.0,
            name=label
        ))

    # 🔘 Trennfläche hinzufügen
    if parting_plane_axis in ['XY', 'XZ', 'YZ']:
        plane_size = bbox * 1.2
        cx, cy, cz = center
        xx, yy = np.meshgrid(
            np.linspace(-plane_size[0] / 2, plane_size[0] / 2, 2),
            np.linspace(-plane_size[1] / 2, plane_size[1] / 2, 2)
        )

        if parting_plane_axis == 'YZ':
            x_plane = np.full_like(xx, cx)
            y_plane = yy + cy
            z_plane = xx + cz
        elif parting_plane_axis == 'XZ':
            x_plane = xx + cx
            y_plane = np.full_like(xx, cy)
            z_plane = yy + cz
        elif parting_plane_axis == 'XY':
            x_plane = xx + cx
            y_plane = yy + cy
            z_plane = np.full_like(xx, cz)

        fig.add_trace(go.Surface(
            x=x_plane,
            y=y_plane,
            z=z_plane,
            opacity=0.3,
            showscale=False,
            colorscale=[[0, 'gray'], [1, 'gray']],
            name="Trennfläche"
        ))

    # 🔵 Kühlkanäle wie gehabt
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

    # 🔥 Heatmap
    if heatmap:
        try:
            samples = trimesh.sample.volume_mesh(mesh, count=500)
            values = np.exp(-np.linalg.norm(samples - center, axis=1)**2 / 5000)
            fig.add_trace(go.Volume(
                x=samples[:, 0],
                y=samples[:, 1],
                z=samples[:, 2],
                value=values,
                isomin=0.1,
                isomax=1.0,
                opacity=1,
                surface_count=250,
                colorscale='Hot',
                showscale=True,
                name="Heatmap"
            ))
        except Exception as e:
            st.warning(f"Heatmap konnte nicht erzeugt werden: {e}")

    fig.update_layout(
        scene=dict(aspectmode='data'),
        margin=dict(l=0, r=0, b=0, t=0)
    )
    st.plotly_chart(fig, use_container_width=True)

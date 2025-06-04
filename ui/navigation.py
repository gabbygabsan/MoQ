import os
import streamlit as st
from PIL import Image

from ui.sidebar import render_sidebar
from logic.geometry import extract_geometry_features
from logic.ml_lgbm import predict_kuehlleistung_lgbm
from viewer.plotly_viewer import show_3d_plotly
from router import navigate_to, PAGE_START, PAGE_CONFIG

# Neuer Import: unsere Mehrkriterien‑Analyse
from logic.parting_analysis import analyze_parting_plane

import plotly.graph_objects as go

def render_config():
    # radio mit exakt den gleichen Strings
    seite = st.sidebar.radio("Seite wählen:",[PAGE_START, PAGE_CONFIG], index=1)
    navigate_to(seite)

    show_parting_analysis = st.sidebar.checkbox("Trennflächen‑Analyse anzeigen", value=False)
    uploaded_file, config = render_sidebar()

    st.title("MoQ – Smart Cooling & Tooling")
    st.markdown("Willkommen bei **MoQ**! ...")

    if uploaded_file and uploaded_file.name.endswith(".stl"):
        mesh = config["trimesh_loader"](uploaded_file)
        st.success("Geometrie erfolgreich geladen!")

        # Heatmap‑Test etc.
        try:
            samples = config["heatmap_test"](mesh)
            st.write("Anzahl Heatmap‑Punkte:", samples.shape[0])
        except Exception as e:
            st.warning(f"Heatmap‑Test fehlgeschlagen: {e}")

        features = extract_geometry_features(mesh)
        st.write("**Bounding Box (X, Y, Z):**",
                 (features["bbox_x"], features["bbox_y"], features["bbox_z"]))
        st.write("**Volumen:**", f"{features['volume_mm3']:.2f} mm³")
        st.write("**Oberfläche:**", f"{features['surface_area_mm2']:.2f} mm²")
        st.write("**Aspektverhältnis:**", f"{features['aspect_ratio']:.2f}")

        undercut_faces = []
        parting_plane_axis = None
        if show_parting_analysis:
            analyse = analyze_parting_plane(mesh)
            st.subheader("Trennflächen‑Analyse")
            st.write("Symmetrien erkannt:", analyse["symmetries"])
            st.write("Beste Trennfläche:", analyse["best_plane"])
            st.write("Anzahl Hinterschneidungen:", len(analyse["undercuts"]))
            undercut_faces = analyse["undercuts"]
            parting_plane_axis = analyse["best_plane"]

        with st.expander("3D‑Vorschau mit Kühlkanälen"):
            show_3d_plotly(
                mesh,
                kanal_durchmesser=config["kanal_durchmesser"],
                abstand=config["kanal_abstand"],
                anzahl_x=config["anzahl_x"],
                anzahl_y=config["anzahl_y"],
                anzahl_z=config["anzahl_z"],
                heatmap=config["heatmap"],
                highlight_faces=undercut_faces,
                parting_plane_axis=parting_plane_axis
            )

        ml_input = {
            "kavitaeten": config["kavitaeten"],
            "volume_mm3": features["volume_mm3"],
            "surface_area_mm2": features["surface_area_mm2"],
            "aspect_ratio": features["aspect_ratio"],
            "kanal_durchmesser": config["kanal_durchmesser"],
            "kanal_abstand":    config["kanal_abstand"]
        }
        prediction_kw = predict_kuehlleistung_lgbm(ml_input)
        st.metric("Geschätzte Kühlleistung", f"{prediction_kw} kW")

    else:
        st.info("Bitte eine gültige STL‑Datei hochladen.")

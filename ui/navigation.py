import os
import streamlit as st
from PIL import Image

from ui.sidebar import render_sidebar
from logic.geometry import extract_geometry_features
from logic.ml_lgbm import predict_kuehlleistung_lgbm
from viewer.plotly_viewer import show_3d_plotly
from router import navigate_to
from logic.parting_analysis import analyze_parting_plane
import plotly.graph_objects as go

def render_config():
    st.sidebar.title("🧭 Navigation")
    seite = st.sidebar.radio("Seite wählen:", ["🏠 Start", "⚙️ Konfigurator"], index=1)
    navigate_to(seite)

    show_parting_analysis = st.sidebar.checkbox("Trennflächen-Analyse anzeigen", value=False)

    uploaded_file, config = render_sidebar()

    st.title("🧠 MoQ – Smart Cooling & Tooling")
    st.markdown("""
    Willkommen bei **MoQ**! Dieses Tool hilft dir, Kühlkanäle und Kühlleistung für Spritzgusswerkzeuge intelligent zu planen.
    """)

    if uploaded_file is not None and uploaded_file.name.endswith(".stl"):
        mesh = config["mesh"] = config["trimesh_loader"](uploaded_file)
        st.success("Geometrie erfolgreich geladen!")

        try:
            test_samples = config["heatmap_test"](mesh)
            st.write("🔬 Anzahl Heatmap-Punkte:", test_samples.shape[0])
        except Exception as e:
            st.warning(f"Heatmap-Probe fehlgeschlagen: {e}")

        features = extract_geometry_features(mesh)
        st.write("**Bounding Box (X, Y, Z):**", (features["bbox_x"], features["bbox_y"], features["bbox_z"]))
        st.write("**Volumen:**", f"{features['volume_mm3']:.2f} mm³")
        st.write("**Oberfläche:**", f"{features['surface_area_mm2']:.2f} mm²")
        st.write("**Aspektverhältnis:**", f"{features['aspect_ratio']:.2f}")

        undercut_faces = []
        if show_parting_analysis:
            analyse = analyze_parting_plane(mesh)
            st.subheader("🧩 Trennflächen-Analyse")
            st.write("🔄 Symmetrien erkannt:", analyse["symmetries"])
            st.write("📐 Beste Trennfläche:", analyse["best_plane"])
            st.write("🚫 Hinterschneidungen erkannt:", len(analyse["undercuts"]))
            undercut_faces = analyse["undercuts"]

        with st.expander("🧊 3D-Vorschau mit Kühlkanälen anzeigen"):
            show_3d_plotly(
                mesh,
                kanal_durchmesser=config["kanal_durchmesser"],
                abstand=config["kanal_abstand"],
                anzahl_x=config["anzahl_x"],
                anzahl_y=config["anzahl_y"],
                anzahl_z=config["anzahl_z"],
                heatmap=config["heatmap"],
                highlight_faces=undercut_faces,
                parting_plane_axis=analyse["best_plane"]  # jetzt: 'XY', 'YZ', ...

            )

        ml_input = {
            "kavitaeten": config["kavitaeten"],
            "volume_mm3": features["volume_mm3"],
            "surface_area_mm2": features["surface_area_mm2"],
            "aspect_ratio": features["aspect_ratio"],
            "kanal_durchmesser": config["kanal_durchmesser"],
            "kanal_abstand": config["kanal_abstand"]
        }
        prediction_kw = predict_kuehlleistung_lgbm(ml_input)
        st.metric("🧊 Geschätzte Kühlleistung", f"{prediction_kw} kW")

    else:
        st.info("Bitte eine gültige STL-Datei hochladen.")

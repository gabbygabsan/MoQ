import streamlit as st
import trimesh
from logic.material import get_material_vorschlag

def render_sidebar():
    st.header("🔧 Eingabeparameter")
    uploaded_file = st.file_uploader("📂 Geometrie hochladen (STL)", type=["stl"])
    kavitaeten = st.number_input("Anzahl der Kavitäten", min_value=1, max_value=16, value=1)
    kanal_durchmesser = st.slider("Kanal-Durchmesser [mm]", 2.0, 20.0, 6.0, step=0.5)
    kanal_abstand = st.slider("Abstand zur Kavität [mm]", 2.0, 20.0, 8.0, step=0.5)
    anzahl_x = st.slider("Kühlkanäle X", 0, 5, 2)
    anzahl_y = st.slider("Kühlkanäle Y", 0, 5, 0)
    anzahl_z = st.slider("Kühlkanäle Z", 0, 5, 0)
    heatmap = st.checkbox("Heatmap anzeigen", value=False)

    st.markdown("---")
    st.subheader("🎯 Materialeigenschaften")

    mech = st.multiselect("🧪 Mechanisch / Funktional", ["Schlagzähigkeit", "Steifigkeit", "Temperaturbeständigkeit", "Abriebfestigkeit"])
    umwelt = st.multiselect("🌡️ Umweltbeständigkeit", ["UV-Beständigkeit", "Feuchtigkeitsbeständig", "Chemikalienbeständig"])
    optik = st.multiselect("🧼 Optik / Oberfläche", ["Hohe Oberflächengüte", "Mattierbar / strukturierbar"])
    nachhaltig = st.multiselect("♻️ Nachhaltigkeit", ["Recycelbar", "Rezyklat verfügbar", "Biobasiert"])

    eigenschaften = mech + umwelt + optik + nachhaltig
    st.write("📋 Ausgewählte Eigenschaften:", eigenschaften)

    st.subheader("🔍 Materialvorschlag")
    vorschlaege = get_material_vorschlag(eigenschaften)
    material = st.selectbox("Materialvorschläge auswählen", [v[0] for v in vorschlaege] if vorschlaege else [])

    return uploaded_file, {
        "kavitaeten": kavitaeten,
        "kanal_durchmesser": kanal_durchmesser,
        "kanal_abstand": kanal_abstand,
        "anzahl_x": anzahl_x,
        "anzahl_y": anzahl_y,
        "anzahl_z": anzahl_z,
        "heatmap": heatmap,
        "material": material,
        "trimesh_loader": lambda f: trimesh.load(f, file_type='stl'),
        "heatmap_test": lambda mesh: trimesh.sample.volume_mesh(mesh, count=500)
    }

def get_material_vorschlag(eigenschaften):
    material_datenbank = {
        "PA6-GF30": ["Schlagzähigkeit", "Steifigkeit", "Temperaturbeständigkeit", "Feuchtigkeitsbeständig", "Recycelbar"],
        "PC": ["Schlagzähigkeit", "Hohe Oberflächengüte", "UV-Beständigkeit", "Rezyklat verfügbar"],
        "ABS": ["Mattierbar / strukturierbar", "Schlagzähigkeit", "Recycelbar"],
        "PLA": ["Biobasiert", "Recycelbar", "Mattierbar / strukturierbar"],
        "PP": ["Feuchtigkeitsbeständig", "Rezyklat verfügbar", "Recycelbar"]
    }

    vorschlaege = []
    for name, eig in material_datenbank.items():
        score = len(set(eigenschaften) & set(eig))
        if score > 0:
            vorschlaege.append((name, score))

    return sorted(vorschlaege, key=lambda x: x[1], reverse=True)

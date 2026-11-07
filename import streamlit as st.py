import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from fpdf import FPDF
import io

st.set_page_config(page_title="Bike Fit Analyzer Pro", page_icon="🚴‍♂️", layout="wide")

# 1. Base de données géométrique enrichie
@st.cache_data
def load_bike_data():
    data = {
        "Marque": [
            "Canyon", "Canyon", "Specialized", "Specialized", "Van Rysel", "Van Rysel", 
            "Trek", "Trek", "Giant", "Giant",
            "Winspace", "Winspace", "Elves", "Elves", "Pardus", "Pardus",
            "De Rosa", "De Rosa", "Ridley", "Ridley", "Stevens", "Stevens", 
            "Eddy Merckx", "Eddy Merckx", "Evolve"
        ],
        "Modèle": [
            "Endurace", "Endurace", "Tarmac SL8", "Tarmac SL8", "RCR Pro", "RCR Pro", 
            "Madone Gen 8", "Madone Gen 8", "TCR Advanced", "TCR Advanced",
            "Agile", "T1550 Gen 2", "Falath EVO", "Vanyar Pro", "Robin Evo", "Spark Evo",
            "SK Pininfarina", "838 Base", "Falcn RS", "Fenix SLiC", "Izoard Pro", "Super Prestige",
            "525 Race", "Pévèle ST", "Road Carbon"
        ],
        "Taille Commerciale": [
            "M", "L", "54", "56", "M", "L", 
            "M", "ML", "M", "ML",
            "M", "L", "54 (L)", "52 (M)", "M", "L",
            "52", "56", "M", "L", "54", "56",
            "M", "L", "54"
        ],
        "Stack (mm)":,
        "Reach (mm)":
    }
    df = pd.DataFrame(data)
    df["Hauteur Tube Selle (mm)"] = (df["Stack (mm)"] * 0.82).astype(int)
    return df

df_bikes = load_bike_data()

st.title("🚴‍♂️ Bike Fit Analyzer Pro")
st.write("Analyse géométrique avancée : Calcul des bagues, de la longueur et de l'inclinaison de la potence avec export PDF sécurisé.")

# 2. Formulaire des mensurations dans la barre latérale
st.sidebar.header("📏 Vos Mensurations (cm)")
nom_pilote = st.sidebar.text_input("Nom du cycliste", value="Cycliste Anonyme")
genre = st.sidebar.selectbox("Genre / Type de géométrie", ["Homme / Unisexe", "Femme"])
taille_totale = st.sidebar.number_input("Taille totale (cm)", min_value=140, max_value=220, value=175)
entrejambe = st.sidebar.number_input("Longueur d'entrejambe (cm)", min_value=60, max_value=110, value=82)
tronc = st.sidebar.number_input("Longueur du buste (cm)", min_value=40, max_value=90, value=62)
bras = st.sidebar.number_input("Longueur des bras (cm)", min_value=40, max_value=90, value=60)

type_pratique = st.sidebar.selectbox("Style de conduite souhaité", ["Confort (Endurance / Voyage)", "Équilibré (Polyvalent)", "Compétition (Aéro / Performance)"])

st.sidebar.subheader("🏭 Filtrer par fabricants")
marques_disponibles = sorted(df_bikes["Marque"].unique())
marques_selectionnees = st.sidebar.multiselect("Choisissez les marques à analyser :", options=marques_disponibles, default=marques_disponibles)

# Angle moyen du tube de direction sur un vélo de route (nécessaire pour la trigonométrie de la potence)
ANGLE_DIRECTION_DEG = 73.0 

# 3. Calculs théoriques biomécaniques cibles
cadre_theorique_cm = entrejambe * 0.665

if type_pratique == "Confort (Endurance / Voyage)":
    facteur_reach = 0.37
    base_potence_standard = 90
elif type_pratique == "Équilibré (Polyvalent)":
    facteur_reach = 0.38
    base_potence_standard = 100
else:
    facteur_reach = 0.395
    base_potence_standard = 110

target_stack = entrejambe * 0.69 * 10
target_reach_cadre = (tronc + bras) * facteur_reach * 10

# Affichage des cibles théoriques
col1, col2, col3 = st.columns(3)
col1.metric("Taille de Cadre Théorique", f"{cadre_theorique_cm:.1f} cm")
col2.metric("Stack Cible Estimé", f"{target_stack:.0f} mm")
col3.metric("Reach Cadre Cible Estimé", f"{target_reach_cadre:.0f} mm")

st.divider()

df_filtré = df_bikes[df_bikes["Marque"].isin(marques_selectionnees)].copy()

if df_filtré.empty:
    st.warning("⚠️ Veuillez sélectionner au moins un fabricant dans la barre latérale.")
else:
    # 4. Algorithme d'ajustement du poste de pilotage (Cockpit Tuning)
    scores_global = []
    potences_recom = []
    bagues_recom = []
    angles_recom = []

    for idx, row in df_filtré.iterrows():
        ecart_stack = target_stack - row["Stack (mm)"]
        reach_cadre = row["Reach (mm)"]
        
        # Par défaut, configuration standard (potence à -6° inclinée vers le bas)
        angle_potence = -6.0
        spacers = 0.0
        
        # Étape A : Ajustement par les bagues sous la potence si le cadre est trop bas
        if ecart_stack > 0:
            spacers = min(round(ecart_stack / 5) * 5, 35) # Max 35mm
            restant_stack = ecart_stack - spacers
            
            # Étape B : Si le cadre reste trop bas malgré les 35mm de bagues, on redresse la potence (ex: +6°)
            if restant_stack > 15:
                angle_potence = 6.0
                
        # Calcul de la longueur de potence nécessaire via l'écart de Reach
        reach_total_pilote = target_reach_cadre + base_potence_standard
        longueur_potence_theorique = reach_total_pilote - reach_cadre
        longueur_potence = int(np.clip(round(longueur_potence_theorique / 10) * 10, 70, 140))
        
        # Calcul des scores d'adéquation
        score_s = 100 - (abs(row["Stack (mm)"] + spacers - target_stack) / target_stack * 100)
        score_r = 100 - (abs(reach_cadre - target_reach_cadre) / target_reach_cadre * 100)
        score_g = (score_s + score_r) / 2
        
        scores_global.append(score_g)
        potences_recom.append(f"{longueur_potence} mm")
        bagues_recom.append(f"+{int(spacers)} mm" if spacers > 0 else "0 mm")
        angles_recom.append(f"{'+' if angle_potence > 0 else ''}{int(angle_potence)}°")

    df_filtré["Score Global"] = scores_global
    df_filtré["Potence Conseillée"] = potences_recom
    df_filtré["Bagues sous Potence"] = bagues_recom
    df_filtré["Inclinaison Potence"] = angles_recom
    df_filtré["Ratio Stack/Reach"] = (df_filtré["Stack (mm)"] / df_filtré["Reach (mm)"]).round(2)

    df_results = df_filtré.sort_values(by="Score Global", ascending=False)

    # Affichage du tableau interactif principal
    st.subheader("🎯 Modèles correspondants & Configurations recommandées")
    df_display = df_results[[
        "Marque", "Modèle", "Taille Commerciale", "Stack (mm)", "Reach (mm)", 
        "Ratio Stack/Reach", "Potence Conseillée", "Inclinaison Potence", "Bagues sous Potence", "Score Global"
    ]].copy()
    
    df_display["Score Global"] = df_display["Score Global"].map("{:.1f}%".format)
    st.dataframe(df_display, use_container_width=True)

    # 5. Module d'exportation PDF sécurisé via BytesIO
    def generate_pdf_bytes(name, size, inseam, t_stack, t_reach, data_table):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Helvetica", "B", 16)
        pdf.cell(0, 10, "Rapport d'Ajustement de Cadre Velo (Bike Fit Pro)", ln=True, align="C")
        pdf.ln(10)
        
        pdf.set_font("Helvetica", "B", 12)
        pdf.cell(0, 8, f"Client : {name}", ln=True)
        pdf.set_font("Helvetica", "", 10)
        pdf.cell(0, 6, f"Morphologie : Taille {size} cm | Entrejambe {inseam} cm", ln=True)
        pdf.cell(0, 6, f"Style de pilotage : {type_pratique}", ln=True)
        pdf.cell(0, 6, f"Cibles theoriques : Stack {t_stack:.0f} mm | Reach Cadre {t_reach:.0f} mm", ln=True)
        pdf.ln(5)
        
        pdf.set_font("Helvetica", "B", 11)
        pdf.cell(0, 8, "Top 5 des meilleures compatibilites de cadres :", ln=True)
        pdf.set_font("Helvetica", "", 9)
        
        # En-têtes du tableau PDF (Nettoyés des caractères accentués pour FPDF standard)
        pdf.cell(28, 7, "Marque", border=1)
        pdf.cell(32, 7, "Modele", border=1)
        pdf.cell(15, 7, "Taille", border=1)
        pdf.cell(28, 7, "Potence", border=1)
        pdf.cell(28, 7, "Angle Pot.", border=1)
        pdf.cell(30, 7, "Bagues Spacers", border=1)
        pdf.cell(25, 7, "Score", border=1)
        pdf.ln()
        
        for _, row in data_table.head(5).iterrows():
            pdf.cell(28, 6, str(row['Marque']), border=1)
            pdf.cell(32, 6, str(row['Modèle']), border=1)
            pdf.cell(15, 6, str(row['Taille Commerciale']), border=1)
            pdf.cell(28, 6, str(row['Potence Conseillée']), border=1)
            pdf.cell(28, 6, str(row['Inclinaison Potence']), border=1)
            pdf.cell(30, 6, str(row['Bagues sous Potence']), border=1)
            pdf.cell(25, 6, f"{row['Score Global']:.1f}%", border=1)
            pdf.ln()
            
        # Conversion du PDF en flux binaire pour Streamlit
        pdf_buffer = io.BytesIO()
        pdf_string = pdf.output(dest='S')
        if isinstance(pdf_string, str):
            pdf_buffer.write(pdf_string.encode('latin1'))
        else:
            pdf_buffer.write(pdf_string)
        pdf_buffer.seek(0)
        return pdf_buffer.getvalue()

    # Bouton de téléchargement
    pdf_data = generate_pdf_bytes(nom_pilote, taille_totale, entrejambe, target_stack, target_reach_cadre, df_results)
    st.download_button(
        label="📥 Télécharger ma fiche de synthèse (PDF)",
        data=pdf_data,
        file_name=f"bike_fit_{nom_pilote.replace(' ', '_').lower()}.pdf",
        mime="application/pdf"
    )

    # 6. Graphique Plotly réactif
    st.subheader("📊 Cartographie des Géométries de Cadres")
    fig = px.scatter(df_results, x="Reach (mm)", y="Stack (mm)", text="Taille Commerciale",
                     color="Marque", hover_data=["Modèle", "Potence Conseillée", "Inclinaison Potence", "Bagues sous Potence"],
                     title="Le point rouge représente votre morphologie cible")
    
    fig.add_scatter(x=[target_reach_cadre], y=[target_stack], mode="markers+text",
                    name="Votre Cible idéale", text=["VOTRE CIBLE"],
                    marker=dict(color="red", size=14, symbol="x"))
    
    st.plotly_chart(fig, use_container_width=True)

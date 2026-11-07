@st.cache_data
def load_bike_data():
    # Base de données enrichie intégrant les nouvelles marques (20 fabricants + extensions)
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
        "Stack (mm)": [
            568, 590, 541, 555, 549, 572, 
            551, 569, 545, 562,
            520, 561, 558, 535, 538, 554,
            550, 585, 547, 573, 550, 568,
            552, 584, 548
        ],
        "Reach (mm)": [
            378, 387, 384, 395, 388, 397, 
            392, 398, 388, 393,
            382, 394, 398, 384, 387, 391,
            389, 403, 393, 389, 386, 392,
            388, 385, 385
        ]
    }
    # Calcul automatique de la hauteur théorique équivalente du tube de selle pour affichage optionnel
    df = pd.DataFrame(data)
    df["Hauteur Tube Selle (mm)"] = (df["Stack (mm)"] * 0.82).astype(int)
    return df

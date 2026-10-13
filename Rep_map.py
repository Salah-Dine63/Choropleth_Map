
import pandas as pd
import geopandas as gpd
import plotly.graph_objects as go
import unicodedata
import re
from pathlib import Path

# ==========================================
# 1. CONFIGURATION
# ==========================================

DOSSIER = Path(__file__).resolve().parent

CSV_FILE = DOSSIER / "taux_urbanisation_maroc_2024.csv"
GEOJSON_FILE = DOSSIER / "Morocco-Regions.geojson"

OUTPUT_FILE = DOSSIER / "carte_urbanisation_maroc.html"

# ==========================================
# 2. CHARGEMENT DES DONNEES
# ==========================================

df = pd.read_csv(
    CSV_FILE,
    encoding="utf-8-sig"
)

geo = gpd.read_file(GEOJSON_FILE)

print("\n===== DONNEES CSV =====")
print(df.head())

print("\n===== COLONNES GEOJSON =====")
print(geo.columns.tolist())

# Vérification des colonnes
colonnes_csv = [
    "region",
    "taux_urbanisation_pct"
]

for colonne in colonnes_csv:
    if colonne not in df.columns:
        raise ValueError(
            f"Colonne CSV manquante : {colonne}"
        )

if "region" not in geo.columns:
    raise ValueError(
        "Le GeoJSON ne contient pas "
        "la colonne 'region'."
    )

# ==========================================
# 3. NORMALISATION DES NOMS
# ==========================================

def normaliser(texte):

    if pd.isna(texte):
        return ""

    texte = str(texte).lower().strip()

    # Suppression des accents
    texte = unicodedata.normalize(
        "NFKD", texte
    )

    texte = "".join(
        c for c in texte
        if not unicodedata.combining(c)
    )

    # Suppression des espaces et tirets
    texte = re.sub(
        r"[^a-z0-9]",
        "",
        texte
    )

    return texte


df["cle_region"] = df["region"].apply(
    normaliser
)

geo["cle_region"] = geo["region"].apply(
    normaliser
)

# ==========================================
# 4. CORRECTION DES CORRESPONDANCES
# ==========================================

correspondances = {

    "laayounesaguiahamra":
        "laayounesakiaelhamra",

    "tangertetouanhoceima":
        "tangertetouanalhoceima",

    "daraatafilelt":
        "draatafilalet"
}

geo["cle_region"] = geo[
    "cle_region"
].replace(correspondances)

# ==========================================
# 5. FUSION CSV + GEOJSON
# ==========================================

donnees = df[
    ["cle_region", "taux_urbanisation_pct"]
].copy()

donnees["taux_urbanisation_pct"] = pd.to_numeric(
    donnees["taux_urbanisation_pct"],
    errors="raise"
)

carte = geo.merge(
    donnees,
    on="cle_region",
    how="left",
    validate="one_to_one",
    indicator=True
)

print("\n===== CORRESPONDANCE =====")

print(
    carte[
        ["region", "taux_urbanisation_pct", "_merge"]
    ].to_string(index=False)
)

# Vérifier les correspondances
if not (carte["_merge"] == "both").all():
    raise ValueError(
        "Certaines régions ne correspondent pas."
    )

if set(df["cle_region"]) != set(geo["cle_region"]):
    raise ValueError(
        "Les régions du CSV et du GeoJSON "
        "ne correspondent pas exactement."
    )

if len(carte) != 12:
    raise ValueError(
        "Le GeoJSON doit contenir 12 régions."
    )

print("\nLes 12 régions sont associées !")

# ==========================================
# 6. STATISTIQUES DESCRIPTIVES
# ==========================================

taux = carte["taux_urbanisation_pct"]

print("\n===== STATISTIQUES =====")

print(f"Moyenne : {taux.mean():.2f} %")
print(f"Médiane : {taux.median():.2f} %")
print(f"Minimum : {taux.min():.2f} %")
print(f"Maximum : {taux.max():.2f} %")
print(f"Ecart-type : {taux.std():.2f}")

# ==========================================
# 7. PREPARATION GEOGRAPHIQUE
# ==========================================

if carte.crs is None:
    raise ValueError(
        "Le système de coordonnées "
        "du GeoJSON est inconnu."
    )

# Projection WGS84
carte = carte.to_crs(epsg=4326)

carte = carte.reset_index(drop=True)

# Identifiants uniques
carte["id_region"] = carte.index.astype(str)

# ==========================================
# 8. CREATION DE LA CARTE
# ==========================================

fig = go.Figure()

# Carte choroplèthe
fig.add_trace(
    go.Choropleth(
        geojson=carte.__geo_interface__,

        locations=carte["id_region"],

        featureidkey="properties.id_region",

        z=carte["taux_urbanisation_pct"],

        zmin=0,
        zmax=100,

        colorscale="Blues",

        marker_line_color="white",
        marker_line_width=1.5,

        customdata=carte[
            ["region", "taux_urbanisation_pct"]
        ].to_numpy(),

        hovertemplate=(
            "<b>%{customdata[0]}</b><br>"
            "Taux d'urbanisation : "
            "%{customdata[1]:.1f}%"
            "<extra></extra>"
        ),

        colorbar=dict(
            title="Urbanisation (%)",
            ticksuffix="%"
        )
    )
)

# ==========================================
# 9. POSITION DES POURCENTAGES
# ==========================================

# On calcule les points dans une projection
# métrique avant de revenir en longitude/latitude.

carte_metrique = carte.to_crs(epsg=3857)

points_metriques = (
    carte_metrique.geometry.representative_point()
)

points = gpd.GeoSeries(
    points_metriques,
    crs=carte_metrique.crs
).to_crs(epsg=4326)

# Pourcentages à afficher
etiquettes = [
    f"{valeur:.1f}%"
    for valeur in carte["taux_urbanisation_pct"]
]

# Ajouter les pourcentages sur les régions
fig.add_trace(
    go.Scattergeo(
        lon=points.x,
        lat=points.y,

        text=etiquettes,

        mode="text",

        textfont=dict(
            size=12,
            color="#111827",
            family="Arial Black"
        ),

        hoverinfo="skip",

        showlegend=False
    )
)




# ==========================================
# 10. PERSONNALISATION ET CADRAGE
# ==========================================

# Calculer les limites géographiques
minx, miny, maxx, maxy = carte.total_bounds

# Ajouter une petite marge autour du Maroc
marge_x = (maxx - minx) * 0.04
marge_y = (maxy - miny) * 0.04

fig.update_geos(
    # Projection adaptée à une carte régionale
    projection_type="mercator",

    # Cadrage automatique sur les régions
    fitbounds="locations",

    # Masquer les éléments inutiles
    visible=False,
    showcoastlines=False,
    showcountries=False,
    showland=False,

    # Afficher seulement la zone du Maroc
    lonaxis_range=[
        minx - marge_x,
        maxx + marge_x
    ],

    lataxis_range=[
        miny - marge_y,
        maxy + marge_y
    ]
)

fig.update_layout(
    title=dict(
        text="Taux d'urbanisation au Maroc — 2024",
        x=0.5,
        xanchor="center",
        font=dict(size=26, color="#17365D")
    ),

    width=1920,
    height=1080,

    margin=dict(
        l=0,
        r=0,
        t=80,
        b=35
    ),

    paper_bgcolor="white",

    geo=dict(
        bgcolor="white",
        domain=dict(
            x=[0.02, 0.90],
            y=[0.03, 0.97]
        )
    ),

    font=dict(
        family="Arial",
        size=17
    )
)


# ==========================================
# 11. EXPORTATION
# ==========================================

fig.write_html(
    str(DOSSIER / "carte_urbanisation_maroc.html")
)

# Carte statique JPG
fig.write_image(
    str(DOSSIER / "carte_urbanisation_maroc.jpg"),
    format="jpeg",
    width=1600,
    height=1200,
    scale=2
)

print("Carte HTML et JPG créées avec succès !")

fig.show()

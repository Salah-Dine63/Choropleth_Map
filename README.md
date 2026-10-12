# Choropleth_Map# Morocco Choropleth Map — Urbanization Rates (2024)

## Project Overview

This project visualizes the **urbanization rates across the 12 regions of Morocco in 2024** using an interactive choropleth map.

A choropleth map represents statistical values through different colors assigned to geographic areas. In this project, each Moroccan region is colored according to its urbanization rate.

The main objective is to demonstrate how statistical data and geographical data can be combined using Python to produce an interactive data visualization.

## Technologies and Dependencies

The project is developed in **Python 3** and uses the following libraries:

| Library | Purpose |
|---|---|
| Pandas | Load, clean, and manipulate CSV data |
| GeoPandas | Read and process geographical GeoJSON data |
| Plotly | Create an interactive choropleth map |
| Kaleido | Export Plotly visualizations as static images |

Additional Python modules such as `unicodedata`, `re`, and `pathlib` are part of the Python standard library and do not require separate installation.

### Install Dependencies

```bash
python -m pip install pandas geopandas plotly kaleido
```

For static image export, recent Kaleido versions may require Google Chrome.

If necessary, install Chrome for Kaleido using:

```bash
plotly_get_chrome
```

## Project Structure

```text
Choropleth_Map/
│
├── Rep_map.py
├── taux_urbanisation_maroc_2024.csv
├── Morocco-Regions.geojson
├── README.md
│
└── outputs/
    ├── carte_urbanisation_maroc.html
    └── carte_urbanisation_maroc.jpg
```

The output directory is illustrative; generated files may be saved in the project root depending on the configuration in `Rep_map.py`.

## Dataset

The project uses two datasets.

### 1. Statistical Data — CSV

The CSV file contains urbanization rates for Morocco's 12 regions.

Example:

```csv
region,annee,taux_urbanisation_pct
Casablanca-Settat,2024,73.3
Rabat-Salé-Kénitra,2024,70.7
Drâa-Tafilalet,2024,36.7
```

**Data source:** Haut-Commissariat au Plan (HCP), RGPH 2024.

Source: https://www.hcp.ma/file/244142/

### 2. Geographical Data — GeoJSON

The GeoJSON file contains the geographical boundaries of Moroccan regions.

Each geographical feature includes a region name and its geometry.

Geographical data source:

https://github.com/Salah-Zkara/Morocco-GeoJson

## How the Program Works

The program follows six main steps.

### Step 1 — Loading the Data

Pandas loads the CSV file containing statistical values, while GeoPandas loads the GeoJSON file containing geographical boundaries.

```python
import pandas as pd
import geopandas as gpd

df = pd.read_csv("taux_urbanisation_maroc_2024.csv")
geo = gpd.read_file("Morocco-Regions.geojson")
```

### Step 2 — Cleaning and Normalizing Region Names

The names of Moroccan regions can differ between the CSV and GeoJSON files due to accents, punctuation, spaces, or alternative spellings.

For example:

- `Drâa-Tafilalet`
- `Daraa-Tafilelt`

The program normalizes region names and applies corrections to known spelling differences.

This ensures that statistical values can be correctly associated with geographical regions.

### Step 3 — Merging Statistical and Geographical Data

The program combines the two datasets using a common normalized region identifier.

```python
carte = geo.merge(
    df[["cle_region", "taux_urbanisation_pct"]],
    on="cle_region",
    how="left"
)
```

After the merge, each region's geometry is associated with its urbanization rate.

The program checks for unmatched regions to prevent missing values in the visualization.

### Step 4 — Creating the Choropleth Map

Plotly uses the merged geographical dataset to generate an interactive choropleth map.

Each region is assigned a color based on its urbanization rate.

The color scale allows users to identify regions with relatively high or low urbanization rates.

### Step 5 — Displaying Values and Interaction

The visualization includes urbanization percentages placed on the map using geographical coordinates.

Users can also interact with the HTML version to explore the data.

### Step 6 — Exporting the Results

The program exports the visualization in two formats:

- **HTML:** Interactive map that can be opened in a web browser.
- **JPG:** Static image suitable for PowerPoint presentations and reports.

Example:

```python
fig.write_html("carte_urbanisation_maroc.html")

fig.write_image(
    "carte_urbanisation_maroc.jpg",
    width=1920,
    height=1080
)
```

## How to Run the Project

### 1. Clone the Repository

```bash
git clone https://github.com/Salah-Dine63/Choropleth_Map.git
```

### 2. Open the Project Directory

```bash
cd Choropleth_Map
```

### 3. Install Dependencies

```bash
python -m pip install pandas geopandas plotly kaleido
```

### 4. Execute the Python Program

```bash
python Rep_map.py
```

Ensure the CSV and GeoJSON files are available at the paths expected by the program.

### 5. View the Results

Open the generated `.html` file in a web browser to explore the interactive map.

The exported `.jpg` image can be inserted directly into a PowerPoint presentation.

## Results and Interpretation

The visualization highlights differences in urbanization rates between Morocco's 12 regions.

According to the dataset:

- **Highest urbanization rate:** Laâyoune-Sakia El Hamra — 92.4%
- **Lowest urbanization rate:** Drâa-Tafilalet — 36.7%
- **Difference:** 55.7 percentage points

The choropleth map makes these regional disparities easier to identify visually.

## Learning Objectives

This project demonstrates practical concepts in data analysis and visualization:

- Importing and cleaning datasets
- Working with CSV and GeoJSON files
- Processing geographical data
- Merging datasets using common identifiers
- Building interactive visualizations
- Exporting visualizations for presentations

## Data Sources

- Haut-Commissariat au Plan (HCP) — RGPH 2024
- Morocco geographical boundaries — Salah-Zkara/Morocco-GeoJson

## Author

**Salah-Dine63**

GitHub: https://github.com/Salah-Dine63
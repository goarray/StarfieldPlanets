import pandas as pd
import re

SKIP_EDITORIDS = {"MS02Beacon01PlanetData"} # an orbital incorrectly named (missing '_' prefix)
last_skipped_editorid = None # Simply to reduce log spam

# -----------------------------
# Configuration
# -----------------------------
input_csv = "PlanetsDump.csv"  # Output produced by xEdit script Starfield_FormDumpToCSV.pas
output_csv = "StarfieldPlanets.csv"

# Keyword mappings - Note: Trait26 is not used by planets
keyword_columns = {
    "PlanetaryRingType": "PlanetaryRingType_kw",
    "PlanetNotLandable": "PlanetNotLandable_kw",
    "DisableWaterOnPlanetKeyword": "DisableWaterOnPlanet_kw",
    "LocTypeNoHumanPresence": "LocTypeNoHumanPresence_kw",
    "LocTypeNoPCMScanTreeContent": "LocTypeNoPCMScanTreeContent_kw",
    "PlanetFaunaExists": "FaunaExists_kw",
    "PlanetMagnetosphere": "Magnetosphere_kw",
    "PlanetFaunaProbability": "FaunaProbability_kw",
    "PlanetFloraProbability": "FloraProbability_kw",
    "PlanetAtmosphereType": "Atmosphere_kw",
    "PlanetFaunaAbundance": "FaunaAbundance_kw",
    "PlanetFloraAbundance": "FloraAbundance_kw",
    "PlanetWaterQuality": "WaterQuality_kw",
    "PlanetGravity": "Gravity_kw",
    "PlanetPressure": "Pressure_kw",
    "PlanetTemperature": "Temperature_kw",
    "PlanetWaterAbundance": "WaterAbundance_kw",
    "PlanetType": "PlanetType_kw",
    "PlanetTrait01": "PlanetTrait01_kw",
    "PlanetTrait02": "PlanetTrait02_kw",
    "PlanetTrait03": "PlanetTrait03_kw",
    "PlanetTrait04": "PlanetTrait04_kw",
    "PlanetTrait05": "PlanetTrait05_kw",
    "PlanetTrait06": "PlanetTrait06_kw",
    "PlanetTrait07": "PlanetTrait07_kw",
    "PlanetTrait08": "PlanetTrait08_kw",
    "PlanetTrait09": "PlanetTrait09_kw",
    "PlanetTrait10": "PlanetTrait10_kw",
    "PlanetTrait11": "PlanetTrait11_kw",
    "PlanetTrait12": "PlanetTrait12_kw",
    "PlanetTrait13": "PlanetTrait13_kw",
    "PlanetTrait14": "PlanetTrait14_kw",
    "PlanetTrait15": "PlanetTrait15_kw",
    "PlanetTrait16": "PlanetTrait16_kw",
    "PlanetTrait17": "PlanetTrait17_kw",
    "PlanetTrait18": "PlanetTrait18_kw",
    "PlanetTrait19": "PlanetTrait19_kw",
    "PlanetTrait20": "PlanetTrait20_kw",
    "PlanetTrait21": "PlanetTrait21_kw",
    "PlanetTrait22": "PlanetTrait22_kw",
    "PlanetTrait23": "PlanetTrait23_kw",
    "PlanetTrait24": "PlanetTrait24_kw",
    "PlanetTrait25": "PlanetTrait25_kw",
}

# -----------------------------
# Load CSV
# -----------------------------
df = pd.read_csv(input_csv)

# Initialize dictionary for each planet
planets = {}

# -----------------------------
# Helpers
# -----------------------------
def to_float(val):
    try:
        return float(val)
    except (TypeError, ValueError):
        return None
        
def extract_biomes(df, max_biomes=10, max_fauna=10, max_flora=10):
    planets_biomes = {}

    for _, row in df.iterrows():
        editorid = row['EditorID']
        # Skip stations in the Biome pass
        if editorid in SKIP_EDITORIDS or editorid.startswith("_"):
            continue
        path = row['Path']
        field_name = row['Field Name']
        value = str(row['Value'])

        if "PPBD - Biome" not in path:
            continue

        # Extract the biome index
        match = re.search(r'Biome #(\d+)', path)
        if not match:
            continue
        biome_idx = int(match.group(1))
        if biome_idx >= max_biomes:
            continue

        if editorid not in planets_biomes:
            planets_biomes[editorid] = {}
        planet_b = planets_biomes[editorid]

        # Flatten the biome name
        if field_name == "Biome":
            planet_b[f"Biome{biome_idx}_Name"] = value
            
        # Biome chance
        if field_name == "Chance":
            planet_b[f"Biome{biome_idx}_Chance"] = to_float(value)

        # Fauna
        fauna_match = re.search(r'Fauna #(\d+)', path)
        if fauna_match:
            fidx = int(fauna_match.group(1))
            if fidx < max_fauna:
                planet_b[f"Biome{biome_idx}_Fauna{fidx}"] = value

        # Flora entries
        flora_match = re.search(r'Entry #(\d+)', path)
        if flora_match and "Flora" in path:
            flidx = int(flora_match.group(1))
            if flidx < max_flora:
                if field_name == "Flora":
                    planet_b[f"Biome{biome_idx}_Flora{flidx}_Name"] = value
                elif field_name == "Resource":
                    planet_b[f"Biome{biome_idx}_Flora{flidx}_Resource"] = value
                elif field_name == "Frequency":
                    planet_b[f"Biome{biome_idx}_Flora{flidx}_Frequency"] = value

        # Flora total count
        if field_name == "Count" and "Flora" in path:
            planet_b[f"Biome{biome_idx}_FloraCount"] = int(value)

    df_out = pd.DataFrame([{"EditorID": eid, **data} for eid, data in planets_biomes.items()])

    if df_out.empty:
        return pd.DataFrame(columns=["EditorID"])

    return df_out
    
def biome_sort_key(col):
    # Example: Biome5_Flora2_Name
    m = re.match(r'Biome(\d+)_(Chance|Fauna|Flora)(\d+)?_?(Name|Resource|Frequency)?', col)
    if m:
        biome_idx = int(m.group(1))
        type_group = m.group(2)
        entry_idx = int(m.group(3)) if m.group(3) else -1
        suffix = m.group(4) if m.group(4) else ''
        # Place Biome Chance immediately after Biome Name
        type_order = {
            'Chance': -1,
            'Fauna': 0,
            'Flora': 1,
        }.get(type_group, 99)

        return (biome_idx, type_order, entry_idx, suffix)
    elif col.startswith('Biome') and col.endswith('_Name'):
        # Handles Biome0_Name etc.
        m2 = re.match(r'Biome(\d+)_Name', col)
        if m2:
            return (int(m2.group(1)), -1, -1, '')
    elif col.startswith('Biome') and col.endswith('_FloraCount'):
        m3 = re.match(r'Biome(\d+)_FloraCount', col)
        if m3:
            return (int(m3.group(1)), 2, -1, '')
    return (999, 999, 999, col)  # put unknowns at the end

# -----------------------------
# Iterate through rows
# -----------------------------
for _, row in df.iterrows():
    editorid = row['EditorID']
    field_name = row['Field Name']
    signature = row['Signature']
    value = str(row['Value'])
    path = row["Path"]

    if editorid in SKIP_EDITORIDS or editorid.startswith("_"):
        if editorid != last_skipped_editorid:
            print(f"Invalid EditorID detected, skipping: {editorid}")
            last_skipped_editorid = editorid
        continue

    planets.setdefault(editorid, {"EditorID": editorid})

    planet = planets[editorid]
    
    # Initialize resource fields if not already
    for col in ["Density", "ModelPath_nif", "PlanetMat_int", "AtmoMat_int", "AtmoMatOuter_int",
                "AtmosphereForm", "AtmoFrac", "AtmoRay", "AtmoMie"]:
        if col not in planet:
            planet[col] = None

    # -----------------------------
    # Base Form Components
    # -----------------------------
    if field_name == "FULL - Name":
        planet["FULL_Name"] = value

    # -----------------------------
    # MODL - Model / Component Data
    # -----------------------------
    if "Component Data - Planet Model" in path:
        # Base NIF
        if field_name == "MODL - Model":
            planet["BaseMesh"] = value
            planet["ModelPath_nif"] = value

        # Planet material mesh hash
        elif field_name == "File Hash":
            # Look back at the Resource:ID value in the same component row
            resource_row = df.iloc[_ - 1] if _ > 0 else None
            if resource_row is not None and resource_row['Field Name'] == "Resource:ID":
                resource_name = resource_row['Value']
                if "planet_mesh" in resource_name:
                    planet["PlanetMat_int"] = value
                elif "atmosphere_mesh:0" in resource_name:
                    planet["AtmoMat_int"] = value
                elif "atmosphere_mesh_outer:0" in resource_name:
                    planet["AtmoMatOuter_int"] = value
                    
    # -----------------------------
    # Worldspaces
    # -----------------------------
    if "CNAM - Master Worldspaces>Worldspace" in path:
        ws_match = re.search(r'Worldspace #(\d+)', path)
        if ws_match:
            idx = int(ws_match.group(1))
            if f"Worldspace{idx}_Name" not in planet:
                planet[f"Worldspace{idx}_Name"] = None
                planet[f"Worldspace{idx}_Lat"] = None
                planet[f"Worldspace{idx}_Lon"] = None

            if field_name == "Worldspace":
                planet[f"Worldspace{idx}_Name"] = value
            elif field_name == "Latitude":
                planet[f"Worldspace{idx}_Lat"] = to_float(value)
            elif field_name == "Longitude":
                planet[f"Worldspace{idx}_Lon"] = to_float(value)
                
    # -----------------------------
    # FNAM - Surface Tree
    # -----------------------------    
    if "FNAM - Surface Tree" in path:
        planet["SurfaceTree"] = value

    # -----------------------------
    # GNAM - Scan Worldspace Multiplier
    # -----------------------------    
    if "GNAM - Scan Worldspace Multiplier" in path:
        planet["ScanMult"] = to_float(value)
        
    # -----------------------------
    # Body
    # -----------------------------
    
    # Body/ANAM - Name
    if "ANAM - Name" in path:
        planet["ANAM_Name"] = value
        
    # Body/CNAM - Body type
    if "CNAM - Body type" in path:
        planet["BodyType"] = value
        
    # Body/DNAM - Space Cell
        # Cell EditorID/Is Unique
        # Only applies to _Orbitals and MS02Beacon01PlanetData (wrongly named orbital)
    
    # Body/ENAM - Orbital Data
    if "ENAM - Orbital Data" in path:
        if field_name == "Major Axis":
            planet["MajorAxis"] = to_float(value)
        elif field_name == "Minor Axis":
            planet["MinorAxis"] = to_float(value)
        elif field_name == "Aphelion":
            planet["Aphelion"] = to_float(value)
        elif field_name == "Eccentricity":
            planet["Eccentricity"] = to_float(value)
        elif field_name == "Incline":
            planet["Incline_r"] = to_float(value)
        elif field_name == "Mean Orbit":
            planet["MeanOrbit"] = to_float(value)
        elif field_name == "Axial Tilt":
            planet["AxialTilt_r"] = to_float(value)
        elif field_name == "Rotational Velocity":
            planet["RotationalVelocity"] = to_float(value)
        elif field_name == "Start Angle":
            planet["StartAngle"] = to_float(value)
        elif field_name == "Apply Orbital Velocity":
            planet["ApplyOrbitalVelocity"] = value
        elif field_name == "Geostationary Orbit":
            planet["GeostationaryOrbit"] = value
        
    # Body/FNAM - Orbited Data
    if "FNAM - Orbited Data" in path:
        if field_name == "Gravity Well":
            planet["GravityWell"] = to_float(value)
        elif field_name == "Mass (in Earth Masses)":
            planet["Mass_Earth"] = to_float(value)
        elif field_name == "Radius in km":
            planet["Radius_km"] = to_float(value)
        elif field_name == "Surface Gravity":
            planet["SurfaceGravity"] = to_float(value)

    # Body/GNAM - Galaxy Data
    elif "GNAM - Galaxy Data" in path:
        if field_name == "Star System ID":
            planet["SystemID"] = value
        elif field_name == "Parent Planet ID":
            planet["ParentID"] = value
        elif field_name == "Planet ID":
            planet["PlanetID"] = value

    # Body/HNAM - Planet Type block
    elif "HNAM - Unknown" in path:
        if value == field_name:  # skip if the value is just the header
            continue
            
        if field_name == "Life":
            planet["Life"] = value
        elif field_name == "Magnetosphere":
            planet["Magnetosphere"] = value
        elif field_name == "Type":
            planet["PlanetType"] = value
        elif field_name == "Settled star":
            planet["SettledStar"] = value
        elif field_name == "Special":
            planet["Special"] = value
        elif field_name == "DENS - Density":
            planet["Density"] = to_float(value)
        elif field_name == "Rings":
            planet["HasRings"] = value

    # Body/INAM - Atmosphere Data block
    if "INAM - Atmosphere Data" in path:
        if field_name == "Atmosphere":
            planet["AtmosphereForm"] = value
        elif field_name == "Avg Density Frac.":
            planet["AtmoFrac"] = to_float(value)
        elif field_name == "Rayleight Scattering Coefficient":
            planet["AtmoRay"] = to_float(value)
        elif field_name == "Mie Scattering Coefficient":
            planet["AtmoMie"] = to_float(value)
            
    # Body/KNAM - Biome Noise
    if "KNAM - Biome Noise" in path:
        if value == field_name:  # skip if the value is just the header
            continue
            
        if field_name == "Noise Filename":
            planet["BiomeNoiseFile"] = value
        elif field_name == "Noise Type":
            planet["BNoiseType"] = to_float(value)  
        elif field_name == "Terrain Height Seed":
            planet["THeightSeed"] = to_float(value)    
        elif field_name == "Terrain Max Height (m)":
            planet["TMaxHeight_m"] = to_float(value)    
            
    # Body
    if field_name == "TEMP - Temperature in C":
        planet["TemperatureC"] = to_float(value)

    # -----------------------------
    # Manual fix for known bad entry
    # -----------------------------
    if editorid == "ZetaOphiuchiVI-aPlanetData":
        planet["AtmosphereForm"] = "____[REFR:0000C171] BAD ENTRY____"

    # -----------------------------
    # Keywords
    # -----------------------------
    if "Keyword" in field_name:
        for kw_prefix, col_name in keyword_columns.items():
            if value.startswith(kw_prefix):
                # Try to extract a description in quotes
                match = re.search(r'"([^"]+)"', value)
                if match:
                    val = match.group(1)
                    if val == "None":
                        val = True
                else:
                    # No quotes → keyword exists, set True
                    val = True
                planet[col_name] = val

# -----------------------------
# Create dataframe & save
# -----------------------------
flat_df = pd.DataFrame(planets.values())

# Ensure EditorID exists
if "EditorID" not in flat_df.columns:
    flat_df["EditorID"] = pd.Series(dtype="object")

max_ws = 11
for i in range(max_ws):
    for suffix in ["Name", "Lat", "Lon"]:
        col_name = f"Worldspace{i}_{suffix}"
        if col_name not in flat_df.columns:
            flat_df[col_name] = None
            
# Add missing keyword columns with NaN first
for col in keyword_columns.values():
    if col not in flat_df.columns:
        flat_df[col] = None

# Extract flattened biomes
df_biomes_flat = extract_biomes(df, max_biomes=10, max_fauna=10, max_flora=10)
# Sort biome columns
biome_cols_sorted = sorted([c for c in df_biomes_flat.columns if c != "EditorID"], key=biome_sort_key)
# Merge and reorder
flat_df = flat_df.merge(df_biomes_flat, on="EditorID", how="left")

# Define the column order
cols = ["EditorID", "BaseMesh","PlanetMat_int","AtmoMat_int","AtmoMatOuter_int", "FULL_Name", #Base Form Components
        "SurfaceTree", "ScanMult", # Other
        "ANAM_Name", "BodyType", # Body
        "MajorAxis", "MinorAxis", "Aphelion", "Eccentricity", "Incline_r", "MeanOrbit", "AxialTilt_r", # DNAM - Orbital Data
        "RotationalVelocity", "StartAngle", "ApplyOrbitalVelocity", "GeostationaryOrbit",
        "GravityWell", "Mass_Earth", "Radius_km", "SurfaceGravity", # FNAM - Orbited Data
        "SystemID", "ParentID", "PlanetID", # GNAM - Galaxy Data
        "Life", "Magnetosphere", "PlanetType", "Density", "SettledStar", "Special", "HasRings", # HNAM - Unknown
        "AtmosphereForm", "AtmoFrac", "AtmoRay", "AtmoMie", # INAM - Atmosphere Data
        "BiomeNoiseFile", "BNoiseType", "THeightSeed", "TMaxHeight_m", # KNAM - Biome Noise
        "TemperatureC", # Body Continued
] + list(keyword_columns.values()) + biome_cols_sorted # CNAM - Master Worldspaces and Biomes

ws_cols = [f"Worldspace{i}_{suffix}" for i in range(max_ws) for suffix in ["Name","Lat","Lon"]]
cols += ws_cols

# Ensure all columns in final order exist in the DataFrame
for col in cols:
    if col not in flat_df.columns:
        flat_df[col] = None

# Reorder dataframe columns
flat_df = flat_df[cols]

# Save to CSV
flat_df.to_csv(output_csv, index=False)
print(f"StarfieldPlanets.csv saved to: {output_csv}")



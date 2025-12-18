# StarfieldPlanets
Repo containing various files related to Starfield's planets

## Starfield Planet Data

Starfield planets extracted to CSV format for external use.

## Files

### `PlanetsDump.csv`

* Example xEdit output from `Starfield_PlanetFormDumpToCSV.pas`.
* Contains planets from Albetti through Akila.
* Required input format for `StarfieldPlanets.py`.

### `StarfieldPlanets.csv`

* **Final output file** – usually the one you'll use.
* Full spreadsheet containing all Starfield planets and `most (see notes)` of their data.
* Output of `StarfieldPlanets.py`.

### `StarfieldPlanets.py`

* Python script to convert `PlanetsDump.csv` into the more usable `StarfieldPlanets.csv`.
* Skips non-planet forms, e.g., those prefixed with `_` (orbitals) and `MS02Beacon01PlanetData`.

### `Starfield_PlanetFormDumpToCSV.pas`

* xEdit script that dumps the entire PLDT form (or any form).
* Generates CSV in the specific format required by `StarfieldPlanets.py`.

---

## Usage

### xEdit

* Run `Starfield_PlanetFormDumpToCSV.pas`.
* Outputs `PlanetsDump.csv` to the xEdit root folder.

### Command line / Python

* From xEdit root folder, run `python StarfieldPlanets.py`.
* Outputs `StarfieldPlanets.csv` to the same folder.

---

## Notes

* Most 'HNAM - Unknown' fields were skipped. 


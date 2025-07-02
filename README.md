# State-of-Wildfires_2024-25_CLIMADA
Code to compute population and asset exposure to wildfires used in the State of Wildfires Report 2024-25.

This repository uses both climada_python (core) and climada_petals, which form part of the [CLIMADA project](https://github.com/CLIMADA-project). Follow the installion instructions. To create the hazard object, install climada_python version v4.1.1, as later CLIMADA versions have issues saving high resolution hazard data (see [issue #1055](https://github.com/CLIMADA-project/climada_python/issues/1055)). On climada_petals, switch to the branch 'feature/wildfire'.

The remaining computations are done with the latest climada_python version (v6.0.1).

## Steps
1. Download the burned area data from [(Giglio et al., 2021)](10.5067/MODIS/MCD64A1.061) and save it a directory that follows this structure: 'data/0_original_MODIS'.
2. Create hazard set (notebook 'create_wildfire_hazard.py')
3. Compute impacts on population (notebook '') and assets (notebook '')
4. Compare with EM-DAT and IDMC data (notebook '')

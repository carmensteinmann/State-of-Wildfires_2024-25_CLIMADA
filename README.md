# State-of-Wildfires_2024-25_CLIMADA
Code to compute population and asset exposure to wildfires used in the State of Wildfires Report 2024-25.

This repository uses both climada_python (core) and climada_petals, which form part of the [CLIMADA project](https://github.com/CLIMADA-project). Follow the installion instructions. To create the hazard object, install climada_python version v4.1.1, as later CLIMADA versions have issues saving high resolution hazard data (see [issue #1055](https://github.com/CLIMADA-project/climada_python/issues/1055)) and switch to the branch 'features/wildfires_ba' on climada_petals.

The remaining computations are done with the latest climada_python version (v6.0.1).

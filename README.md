# State-of-Wildfires_2024-25_CLIMADA
Code to compute population and asset exposure to wildfires used in the State of Wildfires Report 2024-25.

To create the hazard object, install climada version 4.1, as the current climada version has issues saving high resolution hazard data (see [issue](https://github.com/CLIMADA-project/climada_python/issues/1055)) and switch to the branch 'features/wildfires_ba' on climada petals.
The remaining computations are done with the latest climada version (v6.0.1).

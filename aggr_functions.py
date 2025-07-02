import geopandas as gpd
import numpy as np
import shapely
import pandas as pd
import gc
from pathlib import Path
from shapely.geometry import Point

from climada.entity import ImpactFunc, ImpactFuncSet



def linear_impf():
    intensity = np.array([0, 1, 2])
    impact_percentage = np.array([0,1,1])

    impf = ImpactFunc()
    impf.id = 1
    impf.haz_type = 'WF'
    impf.tag = ''
    impf.intensity = intensity
    impf.paa = np.ones(len(intensity))
    impf.mdd = impact_percentage
    impf.check()
    impf_set = ImpactFuncSet()
    impf_set.append(impf)
    impf_set.check()
    
    return impf_set

def get_global_masks(impact):
    global_masks = {}
    global_masks['Global'] = {}
    global_masks['Global']['Global'] = impact.at_event
    
    lat = impact.coord_exp[:,0]
    
    global_masks['Hemispheres'] = {}
    NH_centroids = np.where(lat >= 0)[0]
    global_masks['Hemispheres']['Northern Hemisphere'] = np.asarray(impact.imp_mat[:, NH_centroids].sum(axis=1))
    # SH_centroids = np.setdiff1d(all_inds, NH_centroids)
    global_masks['Hemispheres']['Southern Hemisphere'] = np.asarray(impact.imp_mat[:, ~NH_centroids].sum(axis=1))
    
    global_masks['NH-TR-SH'] = {}
    NH_ET_centroids = np.where(lat >= 30)[0]
    NH_TR_centroids = np.where((lat < 30) & (lat>=0))[0]
    SH_TR_centroids = np.where((lat < 0) & (lat>=-30))[0]
    SH_ET_centroids = np.where(lat < -30)[0]
    global_masks['NH-TR-SH']['Northern Hemisphere Extratropics'] = np.asarray(impact.imp_mat[:, NH_ET_centroids].sum(axis=1))
    global_masks['NH-TR-SH']['Northern Hemisphere Tropics'] = np.asarray(impact.imp_mat[:, NH_TR_centroids].sum(axis=1))
    global_masks['NH-TR-SH']['Southern Hemisphere Tropics'] = np.asarray(impact.imp_mat[:, SH_TR_centroids].sum(axis=1))
    global_masks['NH-TR-SH']['Southern Hemisphere Extratropics'] = np.asarray(impact.imp_mat[:, SH_ET_centroids].sum(axis=1))

    global_masks_codes = {}
    global_masks_codes['Global'] = {}
    global_masks_codes['Global']['Global'] = 1
    global_masks_codes['Hemispheres'] = {}
    global_masks_codes['Hemispheres']['Northern Hemisphere'] = 2
    global_masks_codes['Hemispheres']['Southern Hemisphere'] = 3
    global_masks_codes['NH-TR-SH'] = {}
    global_masks_codes['NH-TR-SH']['Northern Hemisphere Extratropics'] = 11
    global_masks_codes['NH-TR-SH']['Northern Hemisphere Tropics'] = 12
    global_masks_codes['NH-TR-SH']['Southern Hemisphere Tropics'] = 13
    global_masks_codes['NH-TR-SH']['Southern Hemisphere Extratropics'] = 14

    return global_masks, global_masks_codes


def global_df(impact, years):
    
    global_masks, global_masks_codes = get_global_masks(impact)
    
    records = []
    
    for region_layer, regions in global_masks.items():
        for region_name, impact_values in regions.items():
            region_id = global_masks_codes.get(region_layer, {}).get(region_name, None)  
            
            # Ensure impact_values is properly flattened
            impact_values = np.ravel(impact_values)
            
            # Pair each impact value with its corresponding year
            for year, impact in zip(years, impact_values):
                records.append((region_id, region_name, region_layer, year, impact))
    
    # Convert to DataFrame
    df = pd.DataFrame(records, columns=["region_ID", "region_name", "region_layer", "year", "impact"])
    df_global = df[["region_ID", "region_name", "region_layer", "year", "impact"]]
    
    
    return df_global




# def get_region_id(region_shape, centroids, region_ID_column='region_ID'):
#     """
#     Get region_ids from regional polygons for all centroids.

#     Parameters
#     ----------
#     region_shape : gpd
#         Dataframe with region shapes 
#     centroids : Climada.Centroid object
#         Hazard centroids
#     region_ID_column : str
#         Name of the column in the region_shape which contains the region_ID.

#     Returns
#     -------
#     region_ID : np.array
#         Array (len(Centroids)) with region_ids. 
#         Can be set as Hazard.centroids.region_id

#     """
#     lat = centroids.lat
#     lon = centroids.lon
    
#     region_ID = np.full((lon.size,), -1, dtype=int)
    
#     for region in region_shape.itertuples():
#         unset = (region_ID == -1).nonzero()[0]
#         select = shapely.vectorized.contains(region.geometry,lon[unset], lat[unset])
#         region_ID[unset[select]] = getattr(region, region_ID_column)
        
#     return region_ID




def get_region_id(region_shape, centroids, region_ID_column='region_ID'):
    points = gpd.GeoSeries([Point(xy) for xy in zip(centroids.lon, centroids.lat)], crs='EPSG:4326')
    centroids_gdf = gpd.GeoDataFrame(geometry=points)

    joined = gpd.sjoin(centroids_gdf, region_shape[[region_ID_column, 'geometry']], how='left', predicate='within')
    region_ID = joined[region_ID_column].fillna(-1).astype(int).values

    return region_ID



def create_impact_reg(haz_wf, impact, centr_impact, region_shape, var_drop=['region_des','geometry']):

    region_ID = get_region_id(region_shape, haz_wf.centroids)
    id_impact = region_ID[centr_impact]
    id_impact[centr_impact == -1] = -1
    impact_regions = impact.impact_at_reg(id_impact)
    df = impact_regions.drop(columns=[-1])
    
    df_melted = df.melt(var_name="region_ID", value_name="impact")
    df_melted["year"] = haz_wf.event_name * (len(df.columns))
    df_melted = df_melted.sort_values(by="region_ID").reset_index(drop=True)
    region_light = region_shape.drop(columns=var_drop)
    df_final = df_melted.merge(region_light, on="region_ID", how="left")
    
    return df_final


def wrap_reg_aggr(dir_reg_layer, haz_wf, impact, dir_data, exp_name):


    mapping_CSV = pd.read_csv(dir_reg_layer / 'Region_Names_Lookup.csv')
    
    centr_impact = impact.match_centroids(haz_wf)
    
    for directory in dir_reg_layer.iterdir():
        if directory.is_dir():       
            region_layer = directory.name
            print(region_layer)
            output_file_name = dir_data+f'/Results/{exp_name}/seasonal_impacts_{exp_name}_{region_layer}.csv'
            output_file_path = Path(output_file_name)

            # Skip if file already exists
            if output_file_path.exists():
                print(f"Skipping {region_layer} — output file already exists.")
                continue
            
            shp_file = list(directory.glob("*.shp"))[0]
            print(shp_file)
            
            region_shape0 = gpd.read_file(shp_file)
            
            if region_layer == 'GADM_UCDavis_L1':
                region_shape = region_shape0.merge(mapping_CSV, on='region_ID', how='left')
                var_drop = ['fid', 'GID_0', 'COUNTRY', 'GID_1', 'NAME_1', 'VARNAME_1', 'NL_NAME_1',
                            'TYPE_1', 'ENGTYPE_1', 'CC_1', 'HASC_1', 'ISO_1', 'geometry', 'region_des']
            elif region_layer == 'RECCAP2_SHP':
                region_shape = region_shape0.merge(mapping_CSV, left_on='RECCAP2', right_on='region_ID', how='left')
                var_drop = ['RECCAP2', 'geometry', 'region_des']
                region_layer = 'RECCAP2_regions'
            else:
                region_shape = region_shape0
                var_drop=['region_des','geometry']
            
            df_reg = create_impact_reg(haz_wf, impact, centr_impact, region_shape, var_drop=var_drop)
            
            df_reg['region_layer'] = region_layer
            df_reg.rename(columns={"region_nam": "region_name"}, inplace=True)
            df_reg2 = df_reg[["region_ID", "region_name", "region_layer", "year", "impact"]]
            df_reg2.to_csv(output_file_name, index=False)

            
            # Clear DataFrames and force garbage collection
            del df_reg, df_reg2, region_shape
            gc.collect()
    

# -*- coding: utf-8 -*-
"""
Created on Sun Aug 24 00:17:45 2025

@author: FYEC_SKasa
"""

# -*- coding: utf-8 -*-
"""
Core functions for watershed delineation.
"""

from pathlib import Path
import tempfile
import math
import numpy as np
import geopandas as gpd
from shapely.geometry import Point, box, MultiPolygon
from shapely.ops import unary_union
from pyproj import CRS, Transformer
import rasterio
from rasterio.mask import mask
from rasterio.features import rasterize
from whitebox.whitebox_tools import WhiteboxTools

# =============================================================================
#
# HELPER FUNCTIONS (No changes needed)
#
# =============================================================================

def utm_crs_from_lonlat(lon: float, lat: float) -> CRS:
    """Determines the appropriate UTM zone CRS from a longitude and latitude."""
    zone = int((lon + 180) // 6) + 1
    epsg = 32600 + zone if lat >= 0 else 32700 + zone
    return CRS.from_epsg(epsg)

def utm_crs_from_polygon_centroid(poly_gdf: gpd.GeoDataFrame) -> CRS:
    """Determines the appropriate UTM zone CRS from the centroid of a GeoDataFrame."""
    wgs = poly_gdf.to_crs(4326)
    c = wgs.geometry.iloc[0].centroid
    zone = int((c.x + 180) // 6) + 1
    epsg = 32600 + zone if c.y >= 0 else 32700 + zone
    return CRS.from_epsg(epsg)

def make_square_box_utm(lon: float, lat: float, half_size_m: float, utm_crs: CRS) -> gpd.GeoDataFrame:
    """Creates a square GeoDataFrame buffer in a UTM projection."""
    to_utm = Transformer.from_crs(CRS.from_epsg(4326), utm_crs, always_xy=True)
    x, y = to_utm.transform(lon, lat)
    sq = box(x - half_size_m, y - half_size_m, x + half_size_m, y + half_size_m)
    return gpd.GeoDataFrame(geometry=[sq], crs=utm_crs)

def clip_dem_by_polygon(dem_path: str, poly_gdf: gpd.GeoDataFrame, out_path: str) -> str:
    """Clips a DEM raster using a polygon GeoDataFrame."""
    dem_crs = rasterio.open(dem_path).crs
    if dem_crs is not None:
        poly_gdf = poly_gdf.to_crs(dem_crs)
    with rasterio.open(dem_path) as src:
        out_img, out_transform = mask(src, [poly_gdf.iloc[0].geometry.__geo_interface__], crop=True)
        out_meta = src.meta.copy()
        out_meta.update({
            "height": out_img.shape[1],
            "width": out_img.shape[2],
            "transform": out_transform
        })
    with rasterio.open(out_path, "w", **out_meta) as dst:
        dst.write(out_img)
    return out_path

def make_pour_point_file(lon: float, lat: float, target_crs: CRS, out_path: str) -> str:
    """Creates a shapefile for a single pour point."""
    gdf = gpd.GeoDataFrame({"id": [1]}, geometry=[Point(lon, lat)], crs="EPSG:4326")
    if target_crs is not None:
        gdf = gdf.to_crs(target_crs)
    gdf.to_file(out_path)
    return out_path

def _assert_exists(path_str: str, step_name: str):
    """Raises a RuntimeError if a file does not exist."""
    if not Path(path_str).exists():
        raise RuntimeError(f"{step_name} did not produce the expected output: {path_str}")

def snap_point_to_flowacc(pour_pts_vec: str, acc_raster: str, snap_dist_m: float,
                          out_path: str, dem_crs: CRS):
    """Move pour point to center of highest flow-accumulation cell within radius."""
    gdf = gpd.read_file(pour_pts_vec)
    if len(gdf) != 1:
        raise RuntimeError(f"Expected 1 pour point, found {len(gdf)}.")
    if gdf.crs is None:
        gdf.crs = dem_crs
    if CRS.from_user_input(gdf.crs) != dem_crs:
        gdf = gdf.to_crs(dem_crs)
    pt = gdf.geometry.iloc[0]
    if pt.is_empty:
        raise RuntimeError("Pour point geometry is empty.")

    with rasterio.open(acc_raster) as src:
        acc = src.read(1)
        transform = src.transform
        nodata = src.nodata
        xres = abs(transform.a)
        yres = abs(transform.e)

        if dem_crs.is_geographic:
            lonlat = gpd.GeoSeries([pt], crs=dem_crs).to_crs("EPSG:4326").iloc[0]
            lat_rad = math.radians(lonlat.y)
            m_per_deg_lat = 111320.0
            m_per_deg_lon = math.cos(lat_rad) * 111320.0
            px_m = xres * m_per_deg_lon
            py_m = yres * m_per_deg_lat
        else:
            px_m, py_m = xres, yres

        radius_px = max(1, int(math.ceil(snap_dist_m / max(px_m, py_m))))
        col, row = ~transform * (pt.x, pt.y)
        col = int(round(col)); row = int(round(row))
        r0 = max(0, row - radius_px); r1 = min(src.height - 1, row + radius_px)
        c0 = max(0, col - radius_px); c1 = min(src.width - 1, col + radius_px)

        window = acc[r0:r1+1, c0:c1+1]
        if window.size == 0:
            raise RuntimeError("Snap window is empty; increase SNAP_DIST_M or check DEM clip.")

        mask_valid = np.ones_like(window, dtype=bool)
        if nodata is not None:
            mask_valid &= (window != nodata)
        mask_valid &= np.isfinite(window)
        if not mask_valid.any():
            raise RuntimeError("No valid accumulation cells in snap window.")

        win_vals = np.where(mask_valid, window, -np.inf)
        idx = np.unravel_index(np.nanargmax(win_vals), win_vals.shape)
        rr = r0 + idx[0]; cc = c0 + idx[1]
        x_center, y_center = transform * (cc + 0.5, rr + 0.5)

    out_gdf = gpd.GeoDataFrame({"id": [1]}, geometry=[Point(x_center, y_center)], crs=dem_crs)
    out_gdf.to_file(out_path)

def _pick_basin_polygon_from_vectorized(tmp_poly_path: str, snapped_pt_path: str, out_poly_path: str):
    """Selects the correct watershed polygon after vectorization."""
    polys = gpd.read_file(tmp_poly_path)
    if polys.empty:
        raise RuntimeError("Vectorization produced no polygons.")

    value_col = None
    for cand in ["VALUE", "Value", "value", "DN"]:
        if cand in polys.columns:
            value_col = cand
            break

    selected = None
    if value_col is not None:
        pos = polys[polys[value_col].astype(float) > 0]
        if not pos.empty:
            pos = pos.dissolve().explode(index_parts=False).reset_index(drop=True)
            selected = pos

    if selected is None:
        pt = gpd.read_file(snapped_pt_path).geometry.iloc[0]
        pt = gpd.GeoSeries([pt], crs=polys.crs)
        mask_contains = polys.contains(pt.iloc[0])
        if mask_contains.any():
            selected = polys[mask_contains]
        else:
            polys["__dist"] = polys.distance(pt.iloc[0])
            selected = polys.sort_values(["__dist", polys.geometry.area.name], ascending=[True, False]).head(1)
            selected = selected.drop(columns="__dist", errors="ignore")

    geom = unary_union(selected.geometry)
    if isinstance(geom, MultiPolygon):
        pt = gpd.read_file(snapped_pt_path).geometry.iloc[0]
        parts = list(geom.geoms)
        contains = [p.contains(pt) for p in parts]
        geom = parts[contains.index(True)] if any(contains) else max(parts, key=lambda g: g.area)

    gpd.GeoDataFrame({"id": [1]}, geometry=[geom], crs=polys.crs).to_file(out_poly_path)


# =============================================================================
#
# MAIN PROCESSING FUNCTION
#
# =============================================================================

def delineate_watershed(dem_path: str, pour_lon: float, pour_lat: float, output_dir: str, name: str, export_lfp: bool = False):
    """
    Delineates a watershed from a pour point and computes its attributes.

    Args:
        dem_path (str): Path to the input Digital Elevation Model (DEM) raster file.
        pour_lon (float): Longitude of the pour point.
        pour_lat (float): Latitude of the pour point.
        output_dir (str): Directory where the output shapefile will be saved.
        name (str): Name for the output shapefile (e.g., "my_watershed").
        export_lfp (bool): Whether to export the Longest Flow Path as a shapefile.

    Returns:
        str: Path to the generated watershed shapefile on success.
    """
    try:
        # ---- Hydrology calc params ----
        BUFFER_KM = 40
        SNAP_DIST_M = 1000

        # ---- Prepare output paths and tools ----
        print("Starting delineation process...")
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        out_poly_shp = str(Path(output_dir) / f"{name}.shp")

        wbt = WhiteboxTools()
        wbt.set_verbose_mode(False)

        # ----------------------
        # Stage 1: Delineate basin polygon from pour point
        # ----------------------
        print("Step 1: Preparing analysis area...")
        utm_for_box = utm_crs_from_lonlat(pour_lon, pour_lat)
        half = BUFFER_KM * 1000.0
        box_utm = make_square_box_utm(pour_lon, pour_lat, half, utm_for_box)

        with rasterio.open(dem_path) as src:
            if src.crs is None:
                dem_crs = CRS.from_epsg(4326)
                print("Warning: DEM has no CRS; assuming EPSG:4326.")
            else:
                dem_crs = CRS.from_wkt(src.crs.to_wkt())
        box_dem = box_utm.to_crs(dem_crs)

        with tempfile.TemporaryDirectory() as tmp1:
            tmp_path = Path(tmp1)
            print(f"Using temporary directory: {tmp_path}")

            # Clip DEM by the box for faster processing
            clipped_dem = str(tmp_path / "dem_clipped_for_delineation.tif")
            clip_dem_by_polygon(dem_path, box_dem, clipped_dem)
            print("Step 2: Clipped DEM to buffer area.")

            # Define temporary file paths
            dem_breached = str(tmp_path / "dem_breached.tif")
            d8_pointer = str(tmp_path / "d8_pointer.tif")
            facc = str(tmp_path / "flow_acc.tif")
            pour_pts_vec = str(tmp_path / "pour_point.shp")
            pour_pts_snap = str(tmp_path / "pour_point_snapped.shp")
            watershed_r = str(tmp_path / "watershed.tif")
            tmp_polys = str(tmp_path / "watershed_polys.shp")

            # Create the initial pour point shapefile
            make_pour_point_file(pour_lon, pour_lat, dem_crs, pour_pts_vec)

            # Perform core hydrology steps using WhiteboxTools
            print("Step 3: Breaching depressions...")
            wbt.breach_depressions(dem=clipped_dem, output=dem_breached)
            _assert_exists(dem_breached, "BreachDepressions")

            print("Step 4: Calculating D8 flow direction...")
            wbt.d8_pointer(dem=dem_breached, output=d8_pointer)
            _assert_exists(d8_pointer, "D8Pointer")

            print("Step 5: Calculating flow accumulation...")
            wbt.d8_flow_accumulation(i=dem_breached, output=facc, out_type="cells")
            _assert_exists(facc, "D8FlowAccumulation")

            # Snap pour point and delineate watershed
            print("Step 6: Snapping pour point to stream...")
            snap_point_to_flowacc(pour_pts_vec, facc, SNAP_DIST_M, pour_pts_snap, dem_crs)
            _assert_exists(pour_pts_snap, "Manual snap")

            print("Step 7: Delineating watershed raster...")
            wbt.watershed(d8_pntr=d8_pointer, pour_pts=pour_pts_snap, output=watershed_r)
            _assert_exists(watershed_r, "Watershed")

            # Convert raster watershed to vector polygon
            print("Step 8: Converting raster to vector polygon...")
            wbt.raster_to_vector_polygons(i=watershed_r, output=tmp_polys)
            _assert_exists(tmp_polys, "RasterToVectorPolygons")

            print("Step 9: Selecting final basin and exporting...")
            _pick_basin_polygon_from_vectorized(tmp_polys, pour_pts_snap, out_poly_shp)

        print("\n------------------------------------")
        print("SUCCESS: Watershed delineation complete!")
        print(f"Output saved to: {out_poly_shp}")
        print("------------------------------------")

        # ----------------------
        # Stage 2: Compute attributes and add to shapefile
        # ----------------------
        print("Starting Stage 2: Computing attributes...")
        with tempfile.TemporaryDirectory() as tmp2:
            tmp_path = Path(tmp2)
            print(f"Using temporary directory for Stage 2: {tmp_path}")

            # Load polygon
            poly_gdf = gpd.read_file(out_poly_shp)
            if poly_gdf.crs is None:
                poly_gdf.crs = dem_crs

            # Get UTM CRS for accurate metrics
            utm_crs = utm_crs_from_polygon_centroid(poly_gdf)
            poly_utm = poly_gdf.to_crs(utm_crs)

            area_m2 = poly_utm.area.iloc[0]
            perimeter_m = poly_utm.length.iloc[0]

            # Clip DEM tightly to polygon
            clipped_dem = str(tmp_path / "dem_clipped.tif")
            clip_dem_by_polygon(dem_path, poly_gdf, clipped_dem)
            print("Clipped DEM to watershed polygon.")

            # Breach, D8, FAC on clipped DEM
            dem_breached = str(tmp_path / "dem_breached.tif")
            wbt.breach_depressions(dem=clipped_dem, output=dem_breached)
            _assert_exists(dem_breached, "BreachDepressions (Stage 2)")

            d8_pointer = str(tmp_path / "d8_pointer.tif")
            wbt.d8_pointer(dem=dem_breached, output=d8_pointer)
            _assert_exists(d8_pointer, "D8Pointer (Stage 2)")

            facc = str(tmp_path / "flow_acc.tif")
            wbt.d8_flow_accumulation(i=dem_breached, output=facc, out_type="cells")
            _assert_exists(facc, "D8FlowAccumulation (Stage 2)")

            # Rasterize polygon as basins mask
            with rasterio.open(dem_breached) as src:
                transform = src.transform
                width, height = src.width, src.height
                basins_raster = str(tmp_path / "basins.tif")
                shapes = [(geom, 1) for geom in poly_gdf.geometry]
                burned = rasterize(shapes, out_shape=(height, width), transform=transform, fill=0, dtype='uint8')
                with rasterio.open(basins_raster, 'w', driver='GTiff', height=height, width=width, count=1, dtype='uint8',
                                   crs=src.crs, transform=transform) as dst:
                    dst.write(burned, 1)
            print("Rasterized basin mask.")

            # Longest flow path
            lfp_vec = str(tmp_path / "longest_flowpath.shp")
            wbt.longest_flowpath(dem=dem_breached, basins=basins_raster, output=lfp_vec)
            _assert_exists(lfp_vec, "LongestFlowpath")
            lfp_gdf = gpd.read_file(lfp_vec)
            if lfp_gdf.crs is None:
                lfp_gdf.crs = dem_crs

            # keep only the single longest line
            lfp_gdf["length"] = lfp_gdf.length
            lfp_gdf = lfp_gdf.loc[[lfp_gdf["length"].idxmax()]].drop(columns="length")

            lfp_utm = lfp_gdf.to_crs(utm_crs)
            lfp_length_m = lfp_utm.length.sum()
            print("Computed longest flow path (kept only max length).")

            if export_lfp:
                out_lfp_shp = str(Path(output_dir) / f"{name}_lfp.shp")
                lfp_gdf.to_file(out_lfp_shp)
                print(f"Exported Longest Flow Path to: {out_lfp_shp}")

            # Shape factors
            basin_length = lfp_length_m
            form_factor = area_m2 / (basin_length ** 2) if basin_length > 0 else np.nan
            circularity_ratio = (4 * math.pi * area_m2) / (perimeter_m ** 2) if perimeter_m > 0 else np.nan

            # Elevation stats
            with rasterio.open(dem_breached) as src:
                data = src.read(1)
                valid = (data != src.nodata) & np.isfinite(data)
                if valid.any():
                    elev_min = data[valid].min()
                    elev_max = data[valid].max()
                    elev_mean = data[valid].mean()
                else:
                    elev_min = elev_max = elev_mean = np.nan
            print("Computed elevation statistics.")

            # Slope stats
            slope_raster = str(tmp_path / "slope.tif")
            wbt.slope(dem=dem_breached, output=slope_raster, units="degrees")
            _assert_exists(slope_raster, "Slope")
            with rasterio.open(slope_raster) as src:
                data = src.read(1)
                valid = (data != src.nodata) & np.isfinite(data)
                if valid.any():
                    slope_mean = data[valid].mean()
                else:
                    slope_mean = np.nan
            print("Computed slope statistics.")

            # Drainage density
            thresh = 50
            streams_raster = str(tmp_path / "streams.tif")
            wbt.extract_streams(flow_accum=facc, output=streams_raster, threshold=thresh)
            _assert_exists(streams_raster, "ExtractStreams")

            streams_vec = str(tmp_path / "streams.shp")
            wbt.raster_streams_to_vector(streams=streams_raster, d8_pntr=d8_pointer, output=streams_vec)
            if Path(streams_vec).exists():
                streams_gdf = gpd.read_file(streams_vec)
                if streams_gdf.crs is None:
                    streams_gdf.crs = dem_crs
                streams_utm = streams_gdf.to_crs(utm_crs)
                total_stream_length_m = streams_utm.length.sum()
            else:
                total_stream_length_m = 0.0
                print("No streams extracted; setting drainage density to 0.")
            area_km2 = area_m2 / 1e6
            drainage_density = (total_stream_length_m / 1000) / area_km2 if area_km2 > 0 else np.nan
            print("Computed drainage density.")

            # Add attributes to poly_gdf
            poly_gdf['area_m2'] = area_m2
            poly_gdf['perim_m'] = perimeter_m
            poly_gdf['lfp_m'] = lfp_length_m
            poly_gdf['form_fact'] = form_factor
            poly_gdf['circ_rat'] = circularity_ratio
            poly_gdf['elev_min'] = elev_min
            poly_gdf['elev_max'] = elev_max
            poly_gdf['elev_mean'] = elev_mean
            poly_gdf['slope_mean'] = slope_mean
            poly_gdf['drain_dens'] = drainage_density
            poly_gdf['pour_lon'] = pour_lon
            poly_gdf['pour_lat'] = pour_lat

            # Resave shapefile with attributes
            poly_gdf.to_file(out_poly_shp)
            print("Added attributes to shapefile.")

        print("\n------------------------------------")
        print("SUCCESS: Attributes computation complete!")
        print("------------------------------------")
        return out_poly_shp

    except Exception as e:
        print(f"\nERROR: An error occurred during processing.")
        print(f"Details: {str(e)}")
        return None

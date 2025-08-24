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
# HELPER FUNCTIONS
# =============================================================================

def utm_crs_from_lonlat(lon: float, lat: float) -> CRS:
    """Determine appropriate UTM zone CRS from lon/lat."""
    zone = int((lon + 180) // 6) + 1
    epsg = 32600 + zone if lat >= 0 else 32700 + zone
    return CRS.from_epsg(epsg)

def utm_crs_from_polygon_centroid(poly_gdf: gpd.GeoDataFrame) -> CRS:
    """Determine UTM zone CRS from centroid of polygon GeoDataFrame."""
    wgs = poly_gdf.to_crs(4326)
    c = wgs.geometry.iloc[0].centroid
    zone = int((c.x + 180) // 6) + 1
    epsg = 32600 + zone if c.y >= 0 else 32700 + zone
    return CRS.from_epsg(epsg)

def make_square_box_utm(lon: float, lat: float, half_size_m: float, utm_crs: CRS) -> gpd.GeoDataFrame:
    """Create square polygon buffer in UTM projection."""
    to_utm = Transformer.from_crs(CRS.from_epsg(4326), utm_crs, always_xy=True)
    x, y = to_utm.transform(lon, lat)
    sq = box(x - half_size_m, y - half_size_m, x + half_size_m, y + half_size_m)
    return gpd.GeoDataFrame(geometry=[sq], crs=utm_crs)

def clip_dem_by_polygon(dem_path: str, poly_gdf: gpd.GeoDataFrame, out_path: str) -> str:
    """Clip DEM raster using polygon."""
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
    """Create shapefile for pour point."""
    gdf = gpd.GeoDataFrame({"id": [1]}, geometry=[Point(lon, lat)], crs="EPSG:4326")
    if target_crs is not None:
        gdf = gdf.to_crs(target_crs)
    gdf.to_file(out_path)
    return out_path

def _assert_exists(path_str: str, step_name: str):
    """Ensure a file exists or raise error."""
    if not Path(path_str).exists():
        raise RuntimeError(f"{step_name} did not produce expected output: {path_str}")

def snap_point_to_flowacc(pour_pts_vec: str, acc_raster: str, snap_dist_m: float,
                          out_path: str, dem_crs: CRS):
    """Snap pour point to highest accumulation cell within radius."""
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
        col, row = int(round(col)), int(round(row))
        r0, r1 = max(0, row - radius_px), min(src.height - 1, row + radius_px)
        c0, c1 = max(0, col - radius_px), min(src.width - 1, col + radius_px)

        window = acc[r0:r1+1, c0:c1+1]
        if window.size == 0:
            raise RuntimeError("Snap window empty; increase SNAP_DIST_M or check DEM clip.")

        mask_valid = np.ones_like(window, dtype=bool)
        if nodata is not None:
            mask_valid &= (window != nodata)
        mask_valid &= np.isfinite(window)
        if not mask_valid.any():
            raise RuntimeError("No valid accumulation cells in snap window.")

        win_vals = np.where(mask_valid, window, -np.inf)
        idx = np.unravel_index(np.nanargmax(win_vals), win_vals.shape)
        rr, cc = r0 + idx[0], c0 + idx[1]
        x_center, y_center = transform * (cc + 0.5, rr + 0.5)

    out_gdf = gpd.GeoDataFrame({"id": [1]}, geometry=[Point(x_center, y_center)], crs=dem_crs)
    out_gdf.to_file(out_path)

def _pick_basin_polygon_from_vectorized(tmp_poly_path: str, snapped_pt_path: str, out_poly_path: str):
    """Select the correct watershed polygon from vectorized output."""
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
# MAIN FUNCTION
# =============================================================================

def delineate_watershed(dem_path: str, pour_lon: float, pour_lat: float,
                        output_dir: str, name: str, export_lfp: bool = False):
    """
    Delineates watershed and computes attributes.
    Returns path to watershed shapefile.
    """
    try:
        BUFFER_KM = 40
        SNAP_DIST_M = 1000

        Path(output_dir).mkdir(parents=True, exist_ok=True)
        out_poly_shp = str(Path(output_dir) / f"{name}.shp")

        wbt = WhiteboxTools()
        wbt.set_verbose_mode(False)

        # Stage 1: Delineation
        utm_for_box = utm_crs_from_lonlat(pour_lon, pour_lat)
        half = BUFFER_KM * 1000.0
        box_utm = make_square_box_utm(pour_lon, pour_lat, half, utm_for_box)

        with rasterio.open(dem_path) as src:
            dem_crs = CRS.from_wkt(src.crs.to_wkt()) if src.crs else CRS.from_epsg(4326)
        box_dem = box_utm.to_crs(dem_crs)

        with tempfile.TemporaryDirectory() as tmp1:
            tmp_path = Path(tmp1)

            clipped_dem = str(tmp_path / "dem_clipped.tif")
            clip_dem_by_polygon(dem_path, box_dem, clipped_dem)

            dem_breached = str(tmp_path / "dem_breached.tif")
            d8_pointer = str(tmp_path / "d8_pointer.tif")
            facc = str(tmp_path / "flow_acc.tif")
            pour_pts_vec = str(tmp_path / "pour_point.shp")
            pour_pts_snap = str(tmp_path / "pour_point_snapped.shp")
            watershed_r = str(tmp_path / "watershed.tif")
            tmp_polys = str(tmp_path / "watershed_polys.shp")

            make_pour_point_file(pour_lon, pour_lat, dem_crs, pour_pts_vec)

            wbt.breach_depressions(dem=clipped_dem, output=dem_breached); _assert_exists(dem_breached, "Breach")
            wbt.d8_pointer(dem=dem_breached, output=d8_pointer); _assert_exists(d8_pointer, "D8Pointer")
            wbt.d8_flow_accumulation(i=dem_breached, output=facc, out_type="cells"); _assert_exists(facc, "FlowAccum")

            snap_point_to_flowacc(pour_pts_vec, facc, SNAP_DIST_M, pour_pts_snap, dem_crs)
            _assert_exists(pour_pts_snap, "Snap")

            wbt.watershed(d8_pntr=d8_pointer, pour_pts=pour_pts_snap, output=watershed_r); _assert_exists(watershed_r, "Watershed")
            wbt.raster_to_vector_polygons(i=watershed_r, output=tmp_polys); _assert_exists(tmp_polys, "Raster2Vector")

            _pick_basin_polygon_from_vectorized(tmp_polys, pour_pts_snap, out_poly_shp)

        # Stage 2: Attributes
        with tempfile.TemporaryDirectory() as tmp2:
            tmp_path = Path(tmp2)

            poly_gdf = gpd.read_file(out_poly_shp)
            if poly_gdf.crs is None:
                poly_gdf.crs = dem_crs

            utm_crs = utm_crs_from_polygon_centroid(poly_gdf)
            poly_utm = poly_gdf.to_crs(utm_crs)

            area_m2 = poly_utm.area.iloc[0]
            perimeter_m = poly_utm.length.iloc[0]

            clipped_dem = str(tmp_path / "dem_clip2.tif")
            clip_dem_by_polygon(dem_path, poly_gdf, clipped_dem)

            dem_breached = str(tmp_path / "dem_breached2.tif")
            d8_pointer = str(tmp_path / "d8_pointer2.tif")
            facc = str(tmp_path / "flow_acc2.tif")
            wbt.breach_depressions(dem=clipped_dem, output=dem_breached); _assert_exists(dem_breached, "Breach2")
            wbt.d8_pointer(dem=dem_breached, output=d8_pointer); _assert_exists(d8_pointer, "D8Pointer2")
            wbt.d8_flow_accumulation(i=dem_breached, output=facc, out_type="cells"); _assert_exists(facc, "FlowAccum2")

            # LFP
            lfp_vec = str(tmp_path / "lfp.shp")
            wbt.longest_flowpath(dem=dem_breached, basins=clipped_dem, output=lfp_vec); _assert_exists(lfp_vec, "LFP")
            lfp_gdf = gpd.read_file(lfp_vec)
            if lfp_gdf.crs is None:
                lfp_gdf.crs = dem_crs

            # FIX: compute length in UTM
            lfp_utm = lfp_gdf.to_crs(utm_crs)
            lfp_utm["__len_m"] = lfp_utm.length
            longest_idx = lfp_utm["__len_m"].idxmax()
            lfp_gdf = lfp_gdf.loc[[longest_idx]]
            lfp_length_m = float(lfp_utm.loc[longest_idx, "__len_m"])

            if export_lfp:
                out_lfp_shp = str(Path(output_dir) / f"{name}_lfp.shp")
                lfp_gdf.to_file(out_lfp_shp)

            form_factor = area_m2 / (lfp_length_m ** 2) if lfp_length_m > 0 else np.nan
            circularity_ratio = (4 * math.pi * area_m2) / (perimeter_m ** 2) if perimeter_m > 0 else np.nan

            # Elevation stats
            with rasterio.open(dem_breached) as src:
                data = src.read(1)
                valid = (data != src.nodata) & np.isfinite(data)
                elev_min = data[valid].min() if valid.any() else np.nan
                elev_max = data[valid].max() if valid.any() else np.nan
                elev_mean = data[valid].mean() if valid.any() else np.nan

            # Slope
            slope_raster = str(tmp_path / "slope.tif")
            wbt.slope(dem=dem_breached, output=slope_raster, units="degrees"); _assert_exists(slope_raster, "Slope")
            with rasterio.open(slope_raster) as src:
                data = src.read(1)
                valid = (data != src.nodata) & np.isfinite(data)
                slope_mean = data[valid].mean() if valid.any() else np.nan

            # Drainage density (simplified)
            streams_raster = str(tmp_path / "streams.tif")
            wbt.extract_streams(flow_accum=facc, output=streams_raster, threshold=50)
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
            area_km2 = area_m2 / 1e6
            drainage_density = (total_stream_length_m / 1000) / area_km2 if area_km2 > 0 else np.nan

            # Save attributes
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

            poly_gdf.to_file(out_poly_shp)

        return out_poly_shp

    except Exception as e:
        print(f"ERROR: {e}")
        return None

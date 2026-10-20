#!/usr/bin/env python
"""
Example 0: Export Sample Datasets (Structured NetCDF, Unstructured UGRID, GeoJSON).

Exports:
1. `data/structured_global_climate.nc`:
   - Structured 2D rectilinear grid (73 x 144, 2.5 degree resolution)
   - Coordinate variables: `lat`, `lon`
   - Fields: `temperature` (K), `elevation` (m), `wind_speed` (m/s)
   - Compliant with CF-1.8 conventions.

2. `data/unstructured_geodesic_mesh.nc`:
   - Unstructured 2D triangular geodesic mesh (642 nodes, 1280 faces)
   - Topology metadata: `Mesh2` (mesh_topology)
   - Coordinate variables: `Mesh2_node_x`, `Mesh2_node_y`
   - Connectivity: `Mesh2_face_nodes` (face-to-node topology)
   - Fields on faces: `vorticity` (s-1), `sea_surface_height` (m)
   - Compliant with CF-1.8 & UGRID-1.0 conventions.

3. `data/flight_routes.geojson`:
   - Intercontinental commercial aviation corridors with traffic metrics.

4. `data/shipping_routes.geojson`:
   - Global maritime choke points and shipping routes.
"""

import json
import os

import netCDF4 as nc
import numpy as np
import pyvista as pv


def export_structured_netcdf(output_path: str):
    """Generate and export a CF-1.8 compliant structured rectilinear NetCDF dataset."""
    n_lats = 73
    n_lons = 144
    lats = np.linspace(-90, 90, n_lats, dtype=np.float32)
    lons = np.linspace(-180, 180, n_lons, dtype=np.float32)

    with nc.Dataset(output_path, "w", format="NETCDF4") as ds:
        ds.title = "Global Structured Earth Climate and Topography"
        ds.institution = "pyearthviz3d sample data"
        ds.source = "Analytic geophysical Earth model"
        ds.Conventions = "CF-1.8"
        ds.grid_type = "structured_rectilinear"

        ds.createDimension("lat", n_lats)
        ds.createDimension("lon", n_lons)

        v_lat = ds.createVariable("lat", "f4", ("lat",))
        v_lat.units = "degrees_north"
        v_lat.standard_name = "latitude"
        v_lat.long_name = "Latitude"
        v_lat.axis = "Y"
        v_lat[:] = lats

        v_lon = ds.createVariable("lon", "f4", ("lon",))
        v_lon.units = "degrees_east"
        v_lon.standard_name = "longitude"
        v_lon.long_name = "Longitude"
        v_lon.axis = "X"
        v_lon[:] = lons

        lat_rad = np.radians(lats[:, None])
        lon_rad = np.radians(lons[None, :])

        # Surface Temperature (K)
        v_temp = ds.createVariable("temperature", "f4", ("lat", "lon"))
        v_temp.units = "K"
        v_temp.standard_name = "air_temperature"
        v_temp.long_name = "Surface Air Temperature"
        temp_data = (
            288.15 + 32.0 * np.cos(lat_rad) + 6.0 * np.cos(lon_rad) * np.cos(lat_rad)
        )
        v_temp[:] = temp_data.astype(np.float32)

        # Topography / Elevation (m)
        v_elev = ds.createVariable("elevation", "f4", ("lat", "lon"))
        v_elev.units = "m"
        v_elev.standard_name = "surface_altitude"
        v_elev.long_name = "Surface Topography / Elevation"
        elev_data = 800.0 * np.sin(2.0 * lat_rad) * np.cos(
            2.0 * lon_rad
        ) + 400.0 * np.cos(4.0 * lon_rad)
        v_elev[:] = elev_data.astype(np.float32)

        # Wind Speed (m/s)
        v_wind = ds.createVariable("wind_speed", "f4", ("lat", "lon"))
        v_wind.units = "m s-1"
        v_wind.standard_name = "wind_speed"
        v_wind.long_name = "Near-Surface Wind Speed"
        wind_data = (
            5.0 + 12.0 * np.sin(2.0 * lat_rad) ** 2 + 3.0 * np.sin(3.0 * lon_rad)
        )
        v_wind[:] = wind_data.astype(np.float32)

    print(
        f"✓ Exported structured NetCDF: {output_path} ({os.path.getsize(output_path) // 1024} KB)"
    )


def export_unstructured_ugrid_netcdf(output_path: str):
    """Generate and export a UGRID-1.0 compliant unstructured geodesic triangular mesh."""
    # Subdivide an icosahedron on the unit sphere
    ico = pv.Icosahedron(radius=1.0)
    sphere = ico.subdivide(3)

    points = sphere.points
    r = np.linalg.norm(points, axis=1)
    points = points / r[:, None]

    node_lons = np.degrees(np.arctan2(points[:, 1], points[:, 0])).astype(np.float32)
    node_lats = np.degrees(np.arcsin(np.clip(points[:, 2], -1.0, 1.0))).astype(
        np.float32
    )
    face_nodes = sphere.faces.reshape(-1, 4)[:, 1:].astype(np.int32)

    n_nodes = len(node_lons)
    n_faces = len(face_nodes)

    # Compute face centers for cell-centered scalars
    face_centers = np.mean(points[face_nodes], axis=1)
    fc_theta = np.arctan2(face_centers[:, 1], face_centers[:, 0])
    fc_phi = np.arcsin(np.clip(face_centers[:, 2], -1.0, 1.0))

    vorticity = (np.cos(4.0 * fc_theta) * np.sin(3.0 * fc_phi) * 1e-4).astype(
        np.float32
    )
    ssh = (
        0.5 * np.sin(2.0 * fc_phi) * np.cos(3.0 * fc_theta)
        + 0.2 * np.sin(5.0 * fc_theta)
    ).astype(np.float32)

    with nc.Dataset(output_path, "w", format="NETCDF4") as ds:
        ds.title = "Global Unstructured Geodesic Triangular Mesh (UGRID-1.0)"
        ds.institution = "pyearthviz3d sample data"
        ds.source = "Spherical icosahedral subdivision"
        ds.Conventions = "CF-1.8 UGRID-1.0"

        ds.createDimension("nMesh2_node", n_nodes)
        ds.createDimension("nMesh2_face", n_faces)
        ds.createDimension("nMaxMesh2_face_nodes", 3)

        # Topology descriptor variable
        v_topo = ds.createVariable("Mesh2", "i4")
        v_topo.cf_role = "mesh_topology"
        v_topo.topology_dimension = 2
        v_topo.node_coordinates = "Mesh2_node_x Mesh2_node_y"
        v_topo.face_node_connectivity = "Mesh2_face_nodes"
        v_topo.face_dimension = "nMesh2_face"

        # Node coordinates
        v_nx = ds.createVariable("Mesh2_node_x", "f4", ("nMesh2_node",))
        v_nx.standard_name = "longitude"
        v_nx.long_name = "Longitude of 2D mesh nodes"
        v_nx.units = "degrees_east"
        v_nx[:] = node_lons

        v_ny = ds.createVariable("Mesh2_node_y", "f4", ("nMesh2_node",))
        v_ny.standard_name = "latitude"
        v_ny.long_name = "Latitude of 2D mesh nodes"
        v_ny.units = "degrees_north"
        v_ny[:] = node_lats

        # Face-to-node connectivity (0-based)
        v_fn = ds.createVariable(
            "Mesh2_face_nodes", "i4", ("nMesh2_face", "nMaxMesh2_face_nodes")
        )
        v_fn.cf_role = "face_node_connectivity"
        v_fn.start_index = 0
        v_fn[:] = face_nodes

        # Data fields defined on faces
        v_vort = ds.createVariable("vorticity", "f4", ("nMesh2_face",))
        v_vort.long_name = "Relative Vorticity"
        v_vort.units = "s-1"
        v_vort.mesh = "Mesh2"
        v_vort.location = "face"
        v_vort[:] = vorticity

        v_ssh = ds.createVariable("sea_surface_height", "f4", ("nMesh2_face",))
        v_ssh.long_name = "Sea Surface Height Anomaly"
        v_ssh.units = "m"
        v_ssh.mesh = "Mesh2"
        v_ssh.location = "face"
        v_ssh[:] = ssh

    # Also export companion .vtk PolyData file for direct visualization
    vtk_path = os.path.splitext(output_path)[0] + ".vtk"
    sphere.cell_data["vorticity"] = vorticity
    sphere.cell_data["sea_surface_height"] = ssh
    sphere.save(vtk_path)

    print(
        f"✓ Exported unstructured UGRID NetCDF: {output_path} ({os.path.getsize(output_path) // 1024} KB)"
    )
    print(
        f"✓ Exported unstructured VTK PolyData: {vtk_path} ({os.path.getsize(vtk_path) // 1024} KB)"
    )


def export_flight_routes_geojson(output_path: str):
    """Export global commercial aviation corridors as GeoJSON."""
    routes = {
        "type": "FeatureCollection",
        "name": "Global Commercial Flight Corridors",
        "crs": {
            "type": "name",
            "properties": {"name": "urn:ogc:def:crs:OGC:1.3:CRS84"},
        },
        "features": [
            {
                "type": "Feature",
                "properties": {
                    "route_id": "LHR-JFK",
                    "name": "London Heathrow to New York JFK",
                    "traffic_index": 5.0,
                    "category": "Transatlantic",
                },
                "geometry": {
                    "type": "LineString",
                    "coordinates": [
                        [-0.4543, 51.47],
                        [-15.0, 56.5],
                        [-35.0, 58.0],
                        [-52.0, 52.0],
                        [-65.0, 44.0],
                        [-73.7781, 40.6413],
                    ],
                },
            },
            {
                "type": "Feature",
                "properties": {
                    "route_id": "HND-SFO",
                    "name": "Tokyo Haneda to San Francisco",
                    "traffic_index": 4.2,
                    "category": "Transpacific",
                },
                "geometry": {
                    "type": "LineString",
                    "coordinates": [
                        [139.7798, 35.5494],
                        [160.0, 45.0],
                        [180.0, 50.0],
                        [-160.0, 48.0],
                        [-135.0, 42.0],
                        [-122.375, 37.6188],
                    ],
                },
            },
            {
                "type": "Feature",
                "properties": {
                    "route_id": "DXB-SIN",
                    "name": "Dubai to Singapore Changi",
                    "traffic_index": 3.8,
                    "category": "Asia-MiddleEast",
                },
                "geometry": {
                    "type": "LineString",
                    "coordinates": [
                        [55.3644, 25.2532],
                        [65.0, 18.0],
                        [78.0, 10.0],
                        [90.0, 6.0],
                        [103.9915, 1.3644],
                    ],
                },
            },
            {
                "type": "Feature",
                "properties": {
                    "route_id": "SYD-SCL",
                    "name": "Sydney to Santiago de Chile",
                    "traffic_index": 2.1,
                    "category": "Transpolar South",
                },
                "geometry": {
                    "type": "LineString",
                    "coordinates": [
                        [151.1772, -33.9461],
                        [170.0, -45.0],
                        [-160.0, -55.0],
                        [-120.0, -58.0],
                        [-85.0, -45.0],
                        [-70.7933, -33.3928],
                    ],
                },
            },
        ],
    }

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(routes, f, indent=2)

    print(
        f"✓ Exported flight routes GeoJSON: {output_path} ({os.path.getsize(output_path) // 1024} KB)"
    )


def export_shipping_routes_geojson(output_path: str):
    """Export major global maritime shipping corridors as GeoJSON."""
    routes = {
        "type": "FeatureCollection",
        "name": "Major Global Shipping Corridors",
        "crs": {
            "type": "name",
            "properties": {"name": "urn:ogc:def:crs:OGC:1.3:CRS84"},
        },
        "features": [
            {
                "type": "Feature",
                "properties": {
                    "corridor": "Asia-Europe via Suez",
                    "chokepoints": "Malacca, Bab-el-Mandeb, Suez",
                    "density": 5.0,
                },
                "geometry": {
                    "type": "LineString",
                    "coordinates": [
                        [121.5, 31.2],
                        [114.2, 22.3],
                        [103.8, 1.25],
                        [95.0, 5.5],
                        [80.0, 5.9],
                        [51.0, 12.0],
                        [43.3, 12.6],
                        [32.5, 29.9],
                        [14.5, 36.0],
                        [-5.6, 36.0],
                        [0.0, 48.0],
                        [4.0, 51.9],
                    ],
                },
            },
            {
                "type": "Feature",
                "properties": {
                    "corridor": "Trans-Pacific Eastbound",
                    "chokepoints": "Great Circle North Pacific",
                    "density": 4.5,
                },
                "geometry": {
                    "type": "LineString",
                    "coordinates": [
                        [121.5, 31.2],
                        [140.0, 35.0],
                        [165.0, 42.0],
                        [180.0, 46.0],
                        [-160.0, 45.0],
                        [-135.0, 38.0],
                        [-118.2, 33.7],
                    ],
                },
            },
            {
                "type": "Feature",
                "properties": {
                    "corridor": "Panama Transit",
                    "chokepoints": "Panama Canal",
                    "density": 3.8,
                },
                "geometry": {
                    "type": "LineString",
                    "coordinates": [
                        [-118.2, 33.7],
                        [-105.0, 20.0],
                        [-85.0, 9.0],
                        [-79.5, 8.9],
                        [-79.9, 9.3],
                        [-75.0, 15.0],
                        [-74.0, 40.7],
                    ],
                },
            },
        ],
    }

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(routes, f, indent=2)

    print(
        f"✓ Exported shipping routes GeoJSON: {output_path} ({os.path.getsize(output_path) // 1024} KB)"
    )


def main():
    repo_root = os.path.dirname(os.path.dirname(__file__))
    data_dir = os.path.join(repo_root, "data")
    struct_dir = os.path.join(data_dir, "structured")
    unstruct_dir = os.path.join(data_dir, "unstructured")
    vector_dir = os.path.join(data_dir, "vector")

    os.makedirs(struct_dir, exist_ok=True)
    os.makedirs(unstruct_dir, exist_ok=True)
    os.makedirs(vector_dir, exist_ok=True)

    print(f"Exporting sample datasets into {data_dir}...")
    export_structured_netcdf(os.path.join(struct_dir, "structured_global_climate.nc"))
    export_unstructured_ugrid_netcdf(
        os.path.join(unstruct_dir, "unstructured_geodesic_mesh.nc")
    )
    export_flight_routes_geojson(os.path.join(vector_dir, "flight_routes.geojson"))
    export_shipping_routes_geojson(os.path.join(vector_dir, "shipping_routes.geojson"))
    print("All sample datasets successfully generated.")


if __name__ == "__main__":
    main()

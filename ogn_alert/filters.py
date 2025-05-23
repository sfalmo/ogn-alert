from xml.etree import ElementTree


class Filter:
    def __init__(self, beacon_filter=lambda beacon: True):
        self.beacon_filter = beacon_filter

    def __call__(self, data):
        filtered_data = {}
        for address, beacon in data.items():
            if self.beacon_filter(beacon):
                filtered_data[address] = beacon
        return filtered_data


class GeofenceSection:
    def __init__(self, coordinates_or_kml, beacon_filter=lambda beacon: True):
        if isinstance(coordinates_or_kml, str):
            coordinates = self._kml_to_coordinates(coordinates_or_kml)
        else:
            coordinates = coordinates_or_kml
        self._init_from_coordinates(coordinates)
        self.beacon_filter = beacon_filter

    def _kml_to_coordinates(self, kml):
        tree = ElementTree.parse(kml)
        root = tree.getroot()
        polygons = []
        for polygon in root.iter():
            if "Polygon" not in polygon.tag:
                continue
            for coordinates in polygon.iter():
                if "coordinates" not in coordinates.tag:
                    continue
                lon_lat_height = coordinates.text.strip().split(" ")
                polygon_coordinates = []
                for vertex in lon_lat_height:
                    lon, lat, _ = vertex.split(",")
                    polygon_coordinates.append((lat, lon))
                polygons.append(polygon_coordinates)
        if len(polygons) == 0:
            print(f"WARNING: no polygons found in the provided kml file {kml}")
        else:
            print(f"Found {len(polygons)} polygons in the provided kml file {kml}")
        return polygons

    def _init_from_coordinates(self, polygons):
        from shapely import Polygon, contains_xy
        self.polygons = []
        for polygon in polygons:
            self.polygons.append(Polygon(polygon))
        self.contains_xy = contains_xy

    def is_triggered_by(self, beacon):
        for polygon in self.polygons:
            if self.contains_xy(polygon, beacon["latitude"], beacon["longitude"]):
                return self.beacon_filter(beacon)
        return False


class GeofenceFilter(Filter):
    def __init__(self, includes, excludes=[]):
        self.includes = includes
        self.excludes = excludes

    def __call__(self, data):
        filtered_data = {}
        for address, beacon in data.items():
            if self.is_triggered_by(beacon):
                filtered_data[address] = beacon
        return filtered_data

    def is_triggered_by(self, beacon):
        for exclude in self.excludes:
            if exclude.is_triggered_by(beacon):
                return False
        for include in self.includes:
            if include.is_triggered_by(beacon):
                return True
        return False

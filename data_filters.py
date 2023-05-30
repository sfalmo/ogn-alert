class DataFilter:
    def __call__(self, data):
        pass


class Geometry:
    def __init__(self, bounds_coordinates, filters=[]):
        from shapely import Polygon, contains_xy
        self.polygon = Polygon(bounds_coordinates)
        self.filters = filters
        self.contains_xy = contains_xy

    def triggered(self, beacon):
        if not self.contains_xy(self.polygon, beacon["latitude"], beacon["longitude"]):
            return False
        for filt in self.filters:
            if not filt(beacon):
                return False
        return True


class GeofenceFilter(DataFilter):
    def __init__(self, includes, excludes=[]):
        self.includes = includes
        self.excludes = excludes

    def __call__(self, data):
        filtered_data = {}
        for address, beacon in data.items():
            if self.triggered(beacon):
                filtered_data[address] = beacon
        return filtered_data

    def triggered(self, beacon):
        for exclude in self.excludes:
            if exclude.triggered(beacon):
                return False
        for include in self.includes:
            if include.triggered(beacon):
                return True
        return False

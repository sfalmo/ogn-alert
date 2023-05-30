class DataFilter:
    def __call__(self, data):
        pass


class GeofenceSection:
    def __init__(self, bounds_coordinates, filt=None):
        from shapely import Polygon, contains_xy
        self.polygon = Polygon(bounds_coordinates)
        self.filt = filt
        self.contains_xy = contains_xy

    def is_triggered_by(self, beacon):
        if not self.contains_xy(self.polygon, beacon["latitude"], beacon["longitude"]):
            return False
        if self.filt and not self.filt(beacon):
            return False
        return True


class GeofenceFilter(DataFilter):
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

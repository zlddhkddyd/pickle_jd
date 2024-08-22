from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut

class ImageMetadataProcessor:
    def __init__(self):
        self.geolocator = Nominatim(user_agent="my_app")

    def process(self, image_path):
        exif_data = self._get_exif_data(image_path)
        labeled_exif = self._get_labeled_exif(exif_data)
        location_info = self._get_location_info(labeled_exif)
        return {
            'exif_data': exif_data,
            'labeled_exif': labeled_exif,
            'location_info': location_info
        }

    def _get_exif_data(self, image_path):
        exif_data = {}
        try:
            image = Image.open(image_path)
            info = image._getexif()
            if info:
                for tag, value in info.items():
                    decoded = TAGS.get(tag, tag)
                    if decoded == "GPSInfo":
                        gps_data = {}
                        for t in value:
                            sub_decoded = GPSTAGS.get(t, t)
                            gps_data[sub_decoded] = value[t]
                        exif_data[decoded] = gps_data
                    else:
                        exif_data[decoded] = value
        except Exception as e:
            print(f"EXIF 데이터 추출 중 오류 발생: {e}")
        return exif_data

    def _get_labeled_exif(self, exif_data):
        labeled_exif = {}
        if "DateTimeOriginal" in exif_data:
            labeled_exif["Date/Time"] = exif_data["DateTimeOriginal"]
        
        if "GPSInfo" in exif_data:
            gps_info = exif_data["GPSInfo"]
            lat = self._convert_to_degrees(gps_info.get("GPSLatitude", [0, 0, 0]))
            lon = self._convert_to_degrees(gps_info.get("GPSLongitude", [0, 0, 0]))
            if gps_info.get("GPSLatitudeRef", "N") != "N":
                lat = -lat
            if gps_info.get("GPSLongitudeRef", "E") != "E":
                lon = -lon
            labeled_exif["Latitude"] = lat
            labeled_exif["Longitude"] = lon
        
        return labeled_exif

    @staticmethod
    def _convert_to_degrees(value):
        if not value:
            return 0
        d = float(value[0])
        m = float(value[1])
        s = float(value[2])
        return d + (m / 60.0) + (s / 3600.0)

    def _get_location_info(self, labeled_exif):
        location_info = {}
        if "Latitude" in labeled_exif and "Longitude" in labeled_exif:
            try:
                location = self.geolocator.reverse(f"{labeled_exif['Latitude']}, {labeled_exif['Longitude']}")
                location_info = location.raw
            except GeocoderTimedOut as e:
                print(f"Geocoding timed out: {e}")
            except Exception as e:
                print(f"Geocoding error: {e}")
        return location_info

from PIL import Image
from PIL.ExifTags import TAGS


image = Image.open("thermal1.jpg")

exis_data = image._getexif()

if exis_data:

    for tag_id, value in exis_data.items():
        tags= TAGS.get(tag_id, value)
        print(f"{tags},: {value}")
else:
    print("No metadata found")
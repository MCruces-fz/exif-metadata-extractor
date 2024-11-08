import json, os
from PIL import Image
from PIL.ExifTags import TAGS
from datetime import datetime

# print(json.dumps(TAGS, indent=1))

# landing_path = "/media/netac/share/Landing/"
target_path = "/media/netac/share/Fotinhos/"
landing_path = os.path.join(target_path, "YearZero")
failed_path = os.path.join(target_path, "Failed")


def log(txt):
	log_file = "/media/netac/share/metex_log.md"
	with open(log_file, "a") as log:
		log.write(f"- [{datetime.now()}]: {txt}\n")
		

def get_metadata(image_path: str) -> dict:
	with Image.open(image_path) as image:
		exifdata = image.getexif()

	metadata = {}

	if not exifdata:
		return metadata

	for tag_id in exifdata:
		tag_name = TAGS.get(tag_id, tag_id)
		data = exifdata.get(tag_id)
		# if isinstance(data, bytes):
		# 	data = data.decode()
		# print(f"{tag_name:25}: {data}, {type(data)}")
		metadata[tag_name] = data
	return metadata


for image_name in os.listdir(landing_path):
	full_path = os.path.join(landing_path, image_name)
	_, extension = os.path.splitext(image_name)

	# try:
	metadata = get_metadata(full_path)
	if not metadata:
		log(f"**Warning!** Not metadata for {full_path}")
		os.rename(full_path, os.path.join(failed_path, image_name))
		continue
	# except Exception as ex:
	# 	log(f"**Exception** reading image metadata {image_name}: {ex}")
	# 	continue

	try:
		datetime_str = metadata.get("DateTime")
		datetime_obj = datetime.strptime(datetime_str, "%Y:%m:%d %H:%M:%S")
		datetime_fmt = datetime_obj.strftime("%Y-%m-%d_%H-%M-%S")
		year_dir = datetime_obj.strftime("%Y")
	
		make = metadata.get("Make").rstrip('\x00')
		model = metadata.get("Model").rstrip('\x00')  
		
		new_image_name = f"{datetime_fmt}_{make}_{model}{extension}"
	
		new_target_path = os.path.join(target_path, year_dir)
		if not os.path.exists(new_target_path):
			os.makedirs(new_target_path)
	
		os.rename(full_path, os.path.join(new_target_path, new_image_name))
		# print(f"{image_name} -> {new_image_name}")
		log(f"{image_name} -> {new_image_name}")

	except Exception as ex:
		log(f"**Exception** with image {image_name} : {ex} : {metadata} ")
		os.rename(full_path, os.path.join(failed_path, image_name))


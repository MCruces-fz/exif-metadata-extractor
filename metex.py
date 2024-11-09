import json, os, pathlib
from PIL import Image
from PIL.ExifTags import TAGS
from datetime import datetime

home_path = pathlib.Path.home()
required_config_fields = {'working_path', 'landing_dir_name', 'failed_dir_name'}

with open(home_path.joinpath('.metex'), "r") as cfg_file:
	config = json.loads(cfg_file.read())
	if not config.keys() >= required_config_fields:
		raise ValueError(f"Required fields in $HOME/.metex: {required_config_fields}")


landing_path = os.path.join(config["working_path"], config["landing_dir_name"])
working_path = config["working_path"]


def save_log(txt):
	log_file = os.path.join(working_path , "metex_log.md")
	with open(log_file, "a") as log:
		log.write(f"- [{datetime.now()}]: {txt}\n")
		

def get_metadata(image_path: str) -> dict:
	metadata = {}

	with Image.open(image_path) as image:
		exifdata = image.getexif()

	for tag_id in exifdata:
		tag_name = TAGS.get(tag_id, tag_id)
		data = exifdata.get(tag_id)
		metadata[tag_name] = data
	return metadata


def get_datetime_from_metadata(metadata: dict) -> datetime:
	datetime_str = metadata.get("DateTime")
	return datetime.strptime(datetime_str, "%Y:%m:%d %H:%M:%S")


def get_device_from_metadata(metadata: dict) -> str:
	brand = metadata.get("Make").rstrip('\x00')
	model = metadata.get("Model").rstrip('\x00')
	return (" ".join([brand, model]) if not brand in model else model).replace(" ", "_")


def move_to_dir(old_file_name:str, new_file_name: str, given_dir:str) -> None:
	_from = os.path.join(working_path, config["landing_dir_name"], old_file_name)
	_to = os.path.join(working_path, given_dir, new_file_name)

	to_dir = os.path.join(working_path, given_dir)
	if not os.path.exists(to_dir):
		os.makedirs(to_dir)

	os.rename(_from, _to)


def move_to_failed_dir(old_file_name:str) -> None:
	_from = os.path.join(working_path, config["landing_dir_name"], old_file_name)
	_to = os.path.join(working_path, config["failed_dir_name"], old_file_name)

	os.rename(_from, _to)


def should_trigger() -> None:
	pull_it_dir = os.path.join(working_path, "pull_it")

	if not os.path.exists(pull_it_dir):
		os.makedirs(pull_it_dir)

	if "trigger" in os.listdir(pull_it_dir):
		os.rename(os.path.join(pull_it_dir, "trigger"), os.path.join(working_path, "trigger"))
	else:
		exit(0)


should_trigger()

for image_name in os.listdir(landing_path):
	_, extension = os.path.splitext(image_name)

	metadata = get_metadata(os.path.join(landing_path, image_name))
	if not metadata:
		save_log(f"**Warning!** Not metadata for `{image_name}`")
		move_to_failed_dir(image_name)
		continue

	try:
		datetime_obj = get_datetime_from_metadata(metadata)
		device = get_device_from_metadata(metadata)

		new_base_name = datetime_obj.strftime("%Y-%m-%d_%H-%M-%S")
		year_dir = datetime_obj.strftime("%Y")
		
		new_image_name = f"{new_base_name}_{device}{extension}"

		move_to_dir(image_name, new_image_name, year_dir)
		save_log(f"`{image_name}` -> `{new_image_name}`")

	except Exception as ex:
		save_log(f"**Exception** with image `{image_name}` : {ex} : {metadata} ")
		move_to_failed_dir(image_name)


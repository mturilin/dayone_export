#!/usr/local/bin/python3

import json
import sys
import os
import shutil
import dateutil.parser
from tzlocal import get_localzone # $ pip install tzlocal
from datetime import datetime
import time

# get local timezone    
local_tz = get_localzone() 

if len(sys.argv) < 2:
	print(f"Usage: {sys.argv[0]} day_one_export_file.json")
	sys.exit(1)

file_name = sys.argv[1]

print(f"Opening file %{file_name}")

with open(file_name) as f:
	dayone_export = json.load(f)

def unixtime(dt):
	return int(dt.timestamp())

print(f"Success! Found {len(dayone_export['entries'])} entries!")


def unique_file_name(dir, basename, extension):
	full_name = f"{dir}/{basename}.{extension}"
	i = 2
	while (os.path.exists(full_name)):
		full_name = f"{dir}/{basename} {i}.{extension}"	
		i += 1

		if i > 1000:
			print(f"Something is messed up with {full_name}!!!",file=sys.stderr)
			sys.exit(i)
	
	return full_name

def letters_and_spaces(input):
    valids = []
    for character in input:
        if character.isalpha() or character in " !?,0123456789":
            valids.append(character)
    return ''.join(valids).strip()

def export_entry_to_file(entry, root_dir):
	creation_date_str = entry["creationDate"]
	year = creation_date_str[:4]

	file_dir = f"{root_dir}/{year}"
	if not os.path.exists(file_dir):
		os.makedirs(file_dir)
	
	try:
		text = entry["text"]
	except KeyError:
		print(f"Warining: Entry on {entry['creationDate']} doesn't have any text")
		return

	creation_date = dateutil.parser.parse(creation_date_str)

	first_line = text.split('\n')[0].split(".")[0]

	if len(first_line) > 50:
		first_line = first_line[:50]

	first_line = letters_and_spaces(first_line)

	date_prefix = creation_date_str[:10]

	if first_line:
		basename = date_prefix + " - " + first_line
	else:
		basename = date_prefix

	file_name = unique_file_name(file_dir, basename, "txt")
	local_time = creation_date.astimezone(local_tz)
	print (f"creation date = {local_time}")
	with open(file_name, "w") as f:
		f.write(text)

	# creation date
	os.system(f"SetFile -d \"{local_time.strftime('%m/%d/%Y %H:%M:%S')}\" \"{file_name}\"")
	
	# access and modification time
	creation_unix_time = unixtime(creation_date)
	os.utime(file_name, (creation_unix_time, creation_unix_time))
	print(f"Exported {file_name}")



root_dir = os.path.abspath(os.path.dirname(file_name)) + "/export"
print(f"Root dir {root_dir}")

if os.path.exists(root_dir):
	print("Previos export directory found.")
	input = input("Delete? Y/N: ")
	if input.lower() == "y":
		shutil.rmtree(root_dir)

	else:
		sys.exit(1)

os.makedirs(root_dir)

for entry in dayone_export["entries"]:
	export_entry_to_file(entry, root_dir)

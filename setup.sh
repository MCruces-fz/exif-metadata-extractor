#!/usr/bin/bash

if [ ! -d ./venv/ ]; then
	python3 -m venv venv
fi

. venv/bin/activate
python3 -m pip install pillow

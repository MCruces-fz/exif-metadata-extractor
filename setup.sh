#!/usr/bin/bash

if [ ! -d ./venv/ ]; then
	echo "Creating environment..."
	python3 -m venv venv
else
	echo "Environment already created."
fi

. venv/bin/activate
python3 -m pip install pillow

if [ ! -f $HOME/.metex ]; then

	if [[ $# -gt 0 ]]; then
		WORKING_PATH=$1
		echo "Set" $WORKING_PATH "as working path";
	else
		echo "ERROR!! First parameter needed! (working path)";
		return 1;
	fi

	cat << EOF >> $HOME/.metex
{
	"working_path": "$WORKING_PATH",
	"landing_dir_name": "landing",
	"failed_dir_name": "failed"
}
EOF
	echo "Created .metex file configuration at $HOME/.metex";

	mkdir -p $WORKING_PATH/pull_it;
	touch $WORKING_PATH/trigger;
	echo "Created trigger and pull_it/ at working path $WORKING_PATH";

else
	echo "Configuraion file $HOME/.metex already exists.";
fi
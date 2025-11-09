#/bin/bash

if [ ! -f /deja ]; then
	python3 -m venv venv
	source venv/bin/activate
	pip install -U pip
	pip install -U -r requirements.txt
	echo "hold it" > /deja
else
	source venv/bin/activate
fi

python3 main.py

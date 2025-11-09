#/bin/bash

python3 -m venv venv
source venv/bin/activate

if [ ! -f /deja ]; then
	pip install --upgrade pip
	pip install --upgrade langchain
	pip install --upgrade langchain-openai
	echo "hold it" > /deja
fi

python3 main.py

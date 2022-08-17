init:
	pipenv install
	cp .envrc_template .envrc

script:
	pipenv run jupyter nbconvert --to=script notebook.ipynb

run: script
	pipenv run python notebook.py

notebook:
	pipenv run jupyter notebook
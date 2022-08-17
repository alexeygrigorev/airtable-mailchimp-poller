install:
	pipenv install

script:
	pipenv run jupyter nbconvert --to=script notebook.ipynb

run: script
	pipenv run python notebook.py

notebook:
	pipenv run jupyter notebook
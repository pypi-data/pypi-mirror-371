# auth in .pypirc
rm -rf ../dead-man/dist
pip install --upgrade build twine
python3 -m build --sdist
python3 -m twine upload dist/*
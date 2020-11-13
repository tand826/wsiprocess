cd ../tests
pytest tests.py

cd ../
rm -f -r wsiprocess.egg-info/* dist/*
python setup.py sdist bdist_wheel
twine upload --repository pypi dist/*
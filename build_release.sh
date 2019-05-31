#!/usr/bin/env bash
rm -rf ./build ./dist
python setup.py bdist_wheel --universal
twine upload dist/kecpkg_tools-*.whl

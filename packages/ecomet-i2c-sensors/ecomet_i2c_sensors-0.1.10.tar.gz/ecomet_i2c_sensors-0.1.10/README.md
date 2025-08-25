# ecomet_i2c_sensors-pypi
**Last modification:** 4.09.2023

**Contributor:** Marian Minar, Juraj Cekan

```python
$ pip3 install setuptools
$ pip3 install wheel
$ sudo apt-get install python3-venv -y
$ python3 -m venv ~/my_venv
$ source ~/my_venv/bin/activate
$ git clone git@github.com:mamin27/icfs-pypi.git
$ cd ~/ecomet-i2c-ensors-pypi
$ python3 setup.py bdist_wheel
$ pip3 install -e .


$ pip3 install setuptools wheel
$ pip3 install twine
$ python3 setup.py bdist_wheel
$ rm -rf build/ dist/ *.egg-info/
$ python3 -m build
$ twine check dist/*   <-- <= twine==6.0.1
$ twine upload --verbose --repository testpypi dist/*

$ twine upload --verbose --repository pypi dist/*
```

**Links:**

* [TestPyPi](https://test.pypi.org/)
* [PyPi](https://pypi.org/)

**Library Name:**
ecomet-i2c-sensors-pypi

**Dependency:**
* Adafruit_PureIO>=1.1.8
* OPi.GPIO >= 0.5.2
* RPI.GPIO>=0.7.1
* crc>=7.0.0
* pillow>=11.0.0
* pypng>=0.20220715.0
* pyyaml>=6.0.2
* qrcode>=8.0
* smbus2>=0.5.0
* typing-extensions>=4.12.2

**Download commands:**
```sh
vi CHANGELOG.txt
vi setpu.py

pip3 install -i https://test.pypi.org/simple/ ecomet-i2c-sensors <-- API token look into keepas
pip3 install -i https://pypi.org/simple/ ecomet-i2c-sensors

pip install ecomet-i2c-sensors 
pip3 install --index-url https://test.pypi.org/simple ecomet-i2c-sensors
```


**Update under requirements.txt file:**
```sh
pip3 install --upgrade -r requirements.txt --break-system-packages
```

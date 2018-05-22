# Q.U.A.I.L. QUAIL Univeral Analytics of Informatic Linkages
This is a project used to pull down and analyze data from REDCap. It places the project
metadata and data into sqlite databases arranged by form.

# Install

As a python package, QUAIL should be installed from source with pip and python3.

`$ pip3 install -e ./path/to/quail`

## install requirements

QUAIL requires that https://github.com/ctsit/cappy be installed in order for it to
work properly. If you do not install this first then you will get errors as it will
use another cappy from Pypi

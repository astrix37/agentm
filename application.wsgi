activate_this = "/apps/msi/venv/bin/activate_this.py"
execfile(activate_this, dict(__file__=activate_this))

import sys
sys.path.insert(0, '/apps/msi/app/minersite')

from server import app as application
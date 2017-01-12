activate_this = "/apps/agtm/venv/bin/activate_this.py"
execfile(activate_this, dict(__file__=activate_this))

import sys
sys.path.insert(0, '/apps/agtm/app/agentm')

from server import app as application
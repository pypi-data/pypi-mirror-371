"""
This module is a wrapper around the `dashlab` and this should be considered deprecated in the future.
Use [dashlab](https://github.com/asaboor-gh/dashlab) instead.
"""

import sys
import dashlab

sys.modules[__name__] = dashlab # Redirect to dashlab module
dashlab.InteractBase = dashlab.DashboardBase # For backward compatibility

print("Warning: einteract module is deprecated. Use dashlab module instead.")
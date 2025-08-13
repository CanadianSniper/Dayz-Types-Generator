# qt_env_runtime_hook.py
# Ensures crisp UI on high-DPI displays and consistent Fusion defaults
import os
os.environ.setdefault("QT_ENABLE_HIGHDPI_SCALING", "1")
os.environ.setdefault("QT_SCALE_FACTOR_ROUNDING_POLICY", "PassThrough")

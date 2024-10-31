"""
test_activate_conda
"""

import os

os.system('. /home/bioinfo/services/tools/miniconda3/etc/profile.d/conda.sh && \
          conda activate xmipp_DLTK_v0.3 && conda info')

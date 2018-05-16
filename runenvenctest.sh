#!/bin/bash
source spamenv/bin/activate
export PYTHONIOENCODING="UTF-8"
export LC_CTYPE="C.UTF-8"
python3 enctest.py $@
deactivate


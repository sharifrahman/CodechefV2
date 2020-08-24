from __future__ import print_function
import numpy as np
import pandas as pd
import os
import time
from datetime import datetime

class printnsave():
    def __init__(self, folder, text):

        t = open(folder+'/printout.txt','a+')

        if type(text)==str:
            t.write('\n'+text)
        elif type(text)==pd.core.frame.DataFrame:
            t.write('\n'+text.to_string())

        t.close()

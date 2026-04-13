# -*- coding: utf-8 -*-
"""
Created on Mon Apr 13 16:43:13 2026

@author: ALBERTO
"""

import qrcode

img = qrcode.make("https://buckskin-stereo-eastcoast.ngrok-free.dev/")
img.save("Código_QR.png")
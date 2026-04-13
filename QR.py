# -*- coding: utf-8 -*-
"""
Created on Mon Apr 13 16:43:13 2026

@author: ALBERTO
"""

import qrcode

url = "https://f-cks-news-bdt-app.onrender.com"

img = qrcode.make(url)
img.save("QR_F-cks_News_BDT.png")
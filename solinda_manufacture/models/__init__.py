# -*- coding: utf-8 -*-

"""
Buat MO langsung ke mrp production berdasarkan product yang di PO
Buat MO ke mrp production dengan melalaui wizard untuk menentukan BoM yang ingin dipakai
Buat MO ke mrp breakdown dengan acuan product template dari product product yang ingin dipakai
"""

from . import mrp_breakdown
from . import purchase_order
from . import purchase_request
from . import res_company
from . import mrp_production
from . import stock_move
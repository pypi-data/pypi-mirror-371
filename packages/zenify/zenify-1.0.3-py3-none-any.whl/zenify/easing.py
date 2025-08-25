# -*- coding: utf-8 -*-
# easing.py

def ease_in_out(t):
    """Smooth step function for easing in and out."""
    # Smoothstep function: 3t² - 2t³
    if t <= 0: return 0
    if t >= 1: return 1
    return t * t * (3.0 - 2.0 * t)
#!/usr/bin/python3

# -*- coding: utf-8 -*-

from robots import *

filename = input_robot()

if filename:
    content_robot(filename)
    image_robot(filename)
    video_robot(filename)


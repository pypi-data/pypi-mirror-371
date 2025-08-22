#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
##############################################
# Home	: https://www.netkiller.cn
# Author: Neo <netkiller@msn.com>
# Data: 2025-08-18
##############################################
from . import attribute


# feBlend - 与图像相结合的滤镜
# feColorMatrix - 用于彩色滤光片转换
# feComponentTransfer
# feComposite
# feConvolveMatrix
# feDiffuseLighting
# feDisplacementMap
# feFlood
# feImage
# feMerge
# feMorphology

# feSpecularLighting
# feTile
# feTurbulence
# feDistantLight - 用于照明过滤
# fePointLight - 用于照明过滤
# feSpotLight - 用于照明过滤

class Filter:
    def __init__(self, id: str, **kwargs):
        self.id = id
        self.__attrs = attribute(kwargs)
        self.elements = []

    def append(self, element):
        self.elements.append(element.__str__())
        return self

    def __str__(self):
        return f'<filter id="{self.id}" {self.__attrs}>{" ".join(self.elements)}</filter>'


class feGaussianBlur:
    def __init__(self, inn: str, stdDeviation: str, edgeMode: str = None, **kwargs):
        kwargs['in'] = inn
        kwargs['stdDeviation'] = stdDeviation
        if edgeMode:
            kwargs['edgeMode'] = edgeMode
        self.attrs = attribute(kwargs)

    #     self.elements = []
    #
    # def append(self, element):
    #     self.elements.append(element.__str__())

    def __str__(self):
        return f'<feGaussianBlur {self.attrs} />'


class feOffset:
    def __init__(self, inn: str, dx: int, dy: int, **kwargs):
        kwargs['in'] = inn
        kwargs['dx'] = dx
        kwargs['dy'] = dy
        self.attrs = attribute(kwargs)
        # self.elements = []

    # def append(self, element):
    #     self.elements.append(element.__str__())

    def __str__(self):
        return f'<feOffset {self.attrs} />'

#!/usr/bin/env python
# encoding: utf-8


from __future__ import print_function, division
import chimera.extension


class PropKaDialog(chimera.extension.EMO):

    def name(self):
        return 'Tangram PropKa'

    def description(self):
        return "Calculate pKa, pI, charge and folding stabilities for proteins"

    def categories(self):
        return ['InsiliChem']

    def icon(self):
        return

    def activate(self):
        self.module('gui').showUI()


chimera.extension.manager.registerExtension(PropKaDialog(__file__))

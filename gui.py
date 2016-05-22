#!/usr/bin/env python
# encoding: utf-8

# Get used to importing this in your Py27 projects!
from __future__ import print_function, division 
# Python stdlib
import Tkinter as tk
# Chimera stuff
import chimera
from chimera.baseDialog import ModelessDialog
from chimera.widgets import MoleculeScrolledListBox
# Additional 3rd parties

# Own
from core import Controller, Model

"""
The gui.py module contains the interface code, and only that. 
It should only 'draw' the window, and should NOT contain any
business logic like parsing files or applying modifications
to the opened molecules. That belongs to core.py.
"""

# This is a Chimera thing. Do it, and deal with it.
ui = None
def showUI(callback=None):
    """
    Requested by Chimera way-of-doing-things
    """
    if chimera.nogui:
        tk.Tk().withdraw()
    global ui
    if not ui:  # Edit this to reflect the name of the class!
        ui = PropKaDialog()
    model = Model()
    controller = Controller(gui=ui, model=model)
    ui.enter()
    if callback:
        ui.addCallback(callback)


class PropKaDialog(ModelessDialog):

    """
    To display a new dialog on the interface, you will normally inherit from
    ModelessDialog class of chimera.baseDialog module. Being modeless means
    you can have this dialog open while using other parts of the interface.
    If you don't want this behaviour and instead you want your extension to 
    claim exclusive usage, use ModalDialog.
    """

    buttons = ('OK', 'Close')
    default = None
    help = 'https://www.insilichem.com'

    def __init__(self, *args, **kwarg):
        # GUI init
        self.title = 'Plume PropKa'

        # Fire up
        ModelessDialog.__init__(self, resizable=False)
        if not chimera.nogui:
            chimera.extension.manager.registerInstance(self)

    def _initialPositionCheck(self, *args):
        try:
            ModelessDialog._initialPositionCheck(*args)
        except Exception as e:
            if not chimera.nogui:
                raise e

    def fillInUI(self, parent):
        """
        This is the main part of the interface. With this method you code
        the whole dialog, buttons, textareas and everything.
        """
        # Create main window
        self.canvas = tk.Frame(parent)
        self.canvas.pack(expand=True, fill='both', padx=10, pady=10)

        molecules_frame = tk.LabelFrame(self.canvas, text='Select a molecule')
        molecules_frame.grid(row=0, columnspan=2, sticky='ew', padx=5, pady=5)
        self.molecules = MoleculeScrolledListBox(molecules_frame)
        self.molecules.pack(expand=True, fill='both', padx=3, pady=3)

        self.cfg_chains = tk.Entry(self.canvas)

        self.cfg_ph = tk.Entry(self.canvas)
        self.cfg_ph_window = tk.Entry(self.canvas)
        self.cfg_ph_grid = tk.Entry(self.canvas)
        self.cfg_ph_reference = tk.Entry(self.canvas)
        self.cfg_titrate_only = tk.Entry(self.canvas)
        self.cfg_keep_protons = tk.Checkbutton(self.canvas)
        self.cfg_mutations = tk.Entry(self.canvas)
        self.cfg_mutation_method = tk.Entry(self.canvas)
        self.cfg_mutation_options = tk.Entry(self.canvas)

        labels = {
            'cfg_ph': 'pH',
            'cfg_ph_window': 'pH window',
            'cfg_ph_grid': 'pH grid',
            'cfg_ph_reference': 'pH reference',
            'cfg_titrate_only': 'Titrate only',
            'cfg_keep_protons': 'Keep protons',
            'cfg_mutations': 'Mutations',
            'cfg_mutation_method': 'Mutation method',
            'cfg_mutation_options': 'Mutation options',
            'cfg_chains': 'Chains'
        }
        for i, attr in enumerate(sorted(self.__dict__)):
            if attr.startswith('cfg_'):
                name = labels[attr]
                tk.Label(self.canvas, text=name).grid(row=i+1, column=0, sticky='e', padx=4, pady=1)
                getattr(self, attr).grid(row=i+1, column=1, padx=4, pady=1, sticky='w')

    def Apply(self):
        """
        Default! Triggered action if you click on an Apply button
        """
        pass

    def OK(self):
        """
        Default! Triggered action if you click on an OK button
        """
        self.Apply()
        self.destroy()

    def Close(self):
        """
        Default! Triggered action if you click on the Close button
        """
        ModelessDialog.Close(self)
        self.destroy()

    # Below this line, implement all your custom methods for the GUI.
    def load_controller(self):
        pass

if __name__ == '__main__':
    showUI()
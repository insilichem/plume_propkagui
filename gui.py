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
from core import Controller, ViewModel

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
    model = ViewModel(gui=ui)
    controller = Controller(gui=ui, model=model)
    ui.enter()
    ui.controller = controller
    controller.connect_model_and_gui()
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

        # Variables
        self._ph = tk.DoubleVar()
        self._ph_window = tk.DoubleVar(), tk.DoubleVar(), tk.DoubleVar()
        self._ph_grid = tk.DoubleVar(), tk.DoubleVar(), tk.DoubleVar()
        self._ph_reference = tk.StringVar()
        self._mutations = tk.StringVar()
        self._mutations_method = tk.StringVar()
        self._mutations_options = tk.StringVar()
        self._titrate = tk.StringVar()
        self._keep_protons = tk.IntVar()
        self._chains = tk.StringVar()

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

        self.cfg_chains_frame = tk.Frame(self.canvas)
        self.cfg_chains = [tk.Entry(self.cfg_chains_frame, textvariable=self._chains, width=15),
                           tk.Button(self.cfg_chains_frame, text='+')]

        self.cfg_ph = tk.Scale(self.canvas, from_=0, to=14, resolution=0.1, orient='horizontal',
                               length=163, variable=self._ph)
        self.cfg_ph_window_frame = tk.Frame(self.canvas)
        self.cfg_ph_window = [tk.Entry(self.cfg_ph_window_frame, textvariable=var, width=6)
                              for var in self._ph_window]
        self.cfg_ph_grid_frame = tk.Frame(self.canvas)
        self.cfg_ph_grid = [tk.Entry(self.cfg_ph_grid_frame, textvariable=var, width=6)
                            for var in self._ph_grid]
        self.cfg_ph_reference = tk.OptionMenu(self.canvas,self._ph_reference, 'neutral', 'low-pH')

        self.cfg_titrate_frame = tk.Frame(self.canvas)
        self.cfg_titrate = [tk.Entry(self.cfg_titrate_frame, textvariable=self._titrate, width=15),
                            tk.Button(self.cfg_titrate_frame, text='+')]

        self.cfg_keep_protons = tk.Checkbutton(self.canvas, variable=self._keep_protons)
        self.cfg_mutations = tk.Entry(self.canvas, textvariable=self._mutations)
        self.cfg_mutations_method = tk.OptionMenu(self.canvas, self._mutations_method,
                                                  'alignment', 'scwrl', 'jackal')
        self.cfg_mutations_options = tk.Entry(self.canvas, textvariable=self._mutations_options)

        labeled_widgets = {
            (0, 'cfg_chains_frame'): 'Chains',
            (1, 'cfg_ph') : 'pH',
            (2, 'cfg_ph_window_frame') : 'pH window',
            (3, 'cfg_ph_grid_frame') : 'pH grid',
            (4, 'cfg_ph_reference') : 'pH reference',
            (5, 'cfg_titrate_frame') : 'Titrate only',
            (6, 'cfg_keep_protons') : 'Keep protons',
            # (7, 'cfg_mutations'): 'Mutations',
            # (8, 'cfg_mutations_method'): 'Mutation method',
            # (9, 'cfg_mutations_options'): 'Mutation options',
        }
        for (i, attr), title in sorted(labeled_widgets.items()):
            tk.Label(self.canvas, text=title).grid(row=i+1, column=0, sticky='e', padx=4, pady=1)
            getattr(self, attr).grid(row=i+1, column=1, padx=4, pady=1, sticky='w')

        left_packed = self.cfg_ph_window + self.cfg_ph_grid + self.cfg_chains + self.cfg_titrate
        for widget in left_packed:
            widget.pack(side='left', padx=1, expand=True, fill='both')

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
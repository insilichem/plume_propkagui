#!/usr/bin/env python
# encoding: utf-8

# Get used to importing this in your Py27 projects!
from __future__ import print_function, division 
# Python stdlib
import Tkinter as tk
from operator import itemgetter
# Chimera stuff
import chimera
from chimera.baseDialog import ModelessDialog
from chimera.widgets import MoleculeScrolledListBox, SortableTable
from ShowAttr import ShowAttrDialog
# Additional 3rd parties
import matplotlib
matplotlib.use('TkAgg')
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
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
    controller.set_mvc()
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

    buttons = ('Run', 'Close')
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
            ModelessDialog._initialPositionCheck(self, *args)
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

        # Molecules
        molecules_frame = tk.LabelFrame(self.canvas, text='Select a molecule')
        molecules_frame.grid(row=0, columnspan=2, sticky='ew', padx=5, pady=5)
        self.molecules = MoleculeScrolledListBox(molecules_frame)
        self.molecules.pack(expand=True, fill='both', padx=3, pady=3)

        # Configuration
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

    def Close(self):
        """
        Default! Triggered action if you click on the Close button
        """
        global ui
        ui = None
        ModelessDialog.Close(self)
        chimera.extension.manager.deregisterInstance(self)
        self.destroy()

    # Below this line, implement all your custom methods for the GUI.
    def Run(self):
        pass

class PropKaResultsDialog(ModelessDialog):

    buttons = ('Close')
    _show_attr_dialog = None

    def __init__(self, parent=None, molecules=None, *args, **kwargs):
        self.molecules = molecules
        if molecules:
            names = ', '.join(m.name for m in molecules)
            self.title = 'PropKa results for {}'.format(names)
        else:
            self.title = 'PropKa results'
        self._data = None
        self.parent = parent

        self._original_colors = {}

        ModelessDialog.__init__(self, *args, **kwargs)
        if not chimera.nogui:
            chimera.extension.manager.registerInstance(self)

    def _initialPositionCheck(self, *args):
        try:
            ModelessDialog._initialPositionCheck(self, *args)
        except Exception as e:
            if not chimera.nogui:
                raise e

    def fillInUI(self, parent):
        self.canvas = tk.Frame(parent, width=800)
        self.canvas.pack(expand=True, fill='both', padx=5, pady=5)
        self.canvas.columnconfigure(0, weight=1)

        self.table_frame = tk.LabelFrame(master=self.canvas, text='Per-residue information')
        self.table = SortableTable(self.table_frame)
        self.show_backbone_values = tk.IntVar()
        show_bb_values_check = tk.Checkbutton(self.table_frame, text='Show backbone values',
                                              variable=self.show_backbone_values,
                                              command=self._populate_table)

        self.plot_frame = tk.LabelFrame(self.canvas, text='Per-pH information')
        self.plot_figure = Figure(figsize=(4, 4), dpi=100, facecolor='#D9D9D9')
        self.plot_widget = FigureCanvasTkAgg(self.plot_figure, master=self.plot_frame)
        self.plot = self.plot_figure.add_subplot(111)

        self.actions_frame = tk.LabelFrame(self.canvas, text='Actions')
        self.actions = [tk.Button(self.actions_frame, text='Color by pKa', command=self.color_by_pka),
                        tk.Button(self.actions_frame, text='Color by charge', command=self.color_by_charge),
                        tk.Button(self.actions_frame, text='Reset color', command=self.reset_colors)]

        self.other_frame = tk.LabelFrame(self.canvas, text='Key pH values')

        # Pack and grid
        self.table_frame.grid(row=0, columnspan=1, sticky='news', padx=5, pady=5)
        self.table.pack(expand=True, fill='both', padx=5, pady=5)
        show_bb_values_check.pack(expand=True, fill='both', padx=5, pady=5)

        self.actions_frame.grid(row=0, column=1, sticky='news', padx=5, pady=5)
        for button in self.actions:
            button.pack(padx=5, pady=5)
        self.other_frame.grid(row=0, column=2, sticky='news', padx=5, pady=5)

        self.plot_frame.grid(row=1, columnspan=3, sticky='news', padx=5, pady=5)
        self.plot_widget.get_tk_widget().configure(background='#D9D9D9', highlightcolor='#D9D9D9',
                                                   highlightbackground='#D9D9D9')
        self.plot_widget.get_tk_widget().pack(expand=True, fill='both')


    def fillInData(self, data):
        # Fill in table
        self._data = data
        self._populate_table(data)
        self._populate_plot(data)
        self._populate_other(data)

    def _populate_table(self, data=None, show_backbone=None):
        if data is None:
            data = self._data
        if show_backbone is None:
            show_backbone = self.show_backbone_values.get()

        columns = [('#', itemgetter(0)), ('Residues', itemgetter(1)), 
                   ('pKa', itemgetter(2)), ('Charge', itemgetter(3))]
        for column, fetcher in columns:
            self.table.addColumn(column, fetcher)
        table_data = []
        for residue, pka in data['residues_pka'].items():
            restype, respos, chainid = residue
            if not show_backbone and restype in ('BBC', 'BBN'):
                continue
            charge = data['residues_charge'][residue]
            key = ':{}.{} {}'.format(respos, chainid, restype)
            table_data.append((respos, key, pka, charge))
        
        self.table.setData(sorted(table_data))
        try: 
            self.table.launch()
        except tk.TclError: 
            self.table.refresh(rebuild=True)

    def _populate_plot(self, data):
        charge_x, charge_y = zip(*data['charge_profile'])[:2]
        self.plot.plot(charge_x, charge_y, 'b', label='Charge')
        self.plot.set_xlabel('pH')

        folding_x, folding_y = zip(*data['folding_profile'])
        self.plot.plot(folding_x, folding_y, 'r', label='dG')

        self.plot_figure.subplots_adjust(bottom=0.15)
        self.plot.patch.set_visible(False)
        legend = self.plot.legend(loc='upper right', handlelength=2, fancybox=True)
        legend.get_frame().set_alpha(0.5)
        for label in legend.get_texts():
            label.set_fontsize('small')
        for label in legend.get_lines():
            label.set_linewidth(2)  # the legend line width
        self.plot_widget.show()


    def _populate_other(self, data):
        labels = {
            'pi_folded': 'pI (folded)',
            'pi_unfolded': 'pI (unfolded)',
            'pH_opt': 'Optimum pH',
            'pH_min': 'Minimum pH',
            'pH_max': 'Maximum pH',
            'dG_opt': u'Optimum \u0394G',
            'dG_min': u'Minimum \u0394G',
            'dG_max': u'Maximum \u0394G',
            }
        
        for i, (key, label) in enumerate(sorted(labels.items())):
            value = data.get(key)
            value = '{:.2f}'.format(value) if value else 'N/A'
            tk.Label(self.other_frame, text=label + ':').grid(row=i, column=0, sticky='w',
                padx=10, pady=5)
            tk.Label(self.other_frame, text=value).grid(row=i, column=1, sticky='e',
                padx=5, pady=5)

    def color_by_pka(self):
        self.set_attr('pka', self._data['residues_pka'])
        self.render_by_attr('pka', colormap='Rainbow', histogram_values=[0, 14])

    def color_by_charge(self):
        self.set_attr('charge', self._data['residues_charge'])
        self.render_by_attr('charge')

    def set_attr(self, attr, values):
        for key, value in values.items():
            if isinstance(value, list):
                try:
                    value = value[0]
                except IndexError:
                    value = None
            restype, respos, chainid = key
            selection = chimera.specifier.evalSpec(':{}.{}'.format(respos, chainid))
            for res in selection.residues():
                setattr(res, attr, value)

    def render_by_attr(self, attr, colormap='Blue-Red', histogram_values=None):
        if self._show_attr_dialog is None:
            self._show_attr_dialog = ShowAttrDialog()

        d = self._show_attr_dialog
        d.enter()
        d.configure(models=self.molecules, attrsOf='residues', attrName=attr)
        if isinstance(histogram_values, list) and len(histogram_values) == 2:
            d.histogram()['datasource'] = histogram_values + [lambda n: d._makeBins(n, 'Render')]
        d.colorAtomsVar.set(0)
        d.setPalette(colormap)
        d.paletteMenu.setvalue(colormap)
        d.paletteMenu.invoke()
        # Let the histogram end its calculations; otherwise errors will ocurr
        d.uiMaster().after(500, d.Apply)

    def reset_colors(self):
        for m in self.molecules:
            for r in m.residues:
                r.ribbonColor = None
                # r.ribbonColor.ambientDiffuse = m.color.rgba()[:3]


if __name__ == '__main__':
    showUI()
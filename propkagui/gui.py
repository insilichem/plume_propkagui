#!/usr/bin/env python
# encoding: utf-8


from __future__ import print_function, division 
# Python stdlib
import Tkinter as tk
import Pmw
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
from libplume.ui import PlumeBaseDialog
from core import Controller, ViewModel


ui = None
def showUI(callback=None):
    if chimera.nogui:
        tk.Tk().withdraw()
    global ui
    if not ui:  
        ui = PropKaDialog()
    model = ViewModel(gui=ui)
    controller = Controller(gui=ui, model=model)
    ui.enter()
    controller.set_mvc()
    if callback:
        ui.addCallback(callback)


class PropKaDialog(PlumeBaseDialog):

    buttons = ('Run', 'Close')
    default = None
    help = 'https://www.insilichem.com'

    def __init__(self, *args, **kwargs):
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
        super(PropKaDialog, self).__init__(*args, **kwargs)

    def fill_in_ui(self, parent):
        self.canvas.columnconfigure(1, weight=1)
        # Molecules
        self.ui_molecules_frame = tk.LabelFrame(self.canvas, text='Select a molecule')
        self.ui_molecules_frame.grid(row=0, column=0, columnspan=2, sticky='ew', padx=5, pady=5)
        self.ui_molecules = MoleculeScrolledListBox(self.ui_molecules_frame)
        self.ui_molecules.pack(expand=True, fill='both', padx=3, pady=3)

        # Configuration
        ## Chains
        self.ui_chains_frame = tk.Frame(self.canvas)
        self.ui_chains_entry = tk.Entry(self.ui_chains_frame, 
                textvariable=self._chains, width=15)
        self.ui_chains_btn = tk.Button(self.ui_chains_frame, text='+')
        self.ui_chains = [self.ui_chains_entry, self.ui_chains_btn]

        ## pH
        self.ui_ph = tk.Scale(self.canvas, from_=0, to=14, resolution=0.1, orient='horizontal',
                               length=163, variable=self._ph)
        self.ui_ph_window_frame = tk.Frame(self.canvas)
        self.ui_ph_window_0 = tk.Entry(self.ui_ph_window_frame, 
                                        textvariable=self._ph_window[0], width=6)
        self.ui_ph_window_1 = tk.Entry(self.ui_ph_window_frame, 
                                        textvariable=self._ph_window[1], width=6)
        self.ui_ph_window_2 = tk.Entry(self.ui_ph_window_frame, 
                                        textvariable=self._ph_window[2], width=6)
        self.ui_ph_window = [self.ui_ph_window_0, self.ui_ph_window_1, self.ui_ph_window_2]                     
        
        self.ui_ph_grid_frame = tk.Frame(self.canvas)
        self.ui_ph_grid_0 = tk.Entry(self.ui_ph_grid_frame, 
                                    textvariable=self._ph_grid[0], width=6)
        self.ui_ph_grid_1 = tk.Entry(self.ui_ph_grid_frame, 
                                    textvariable=self._ph_grid[1], width=6)
        self.ui_ph_grid_2 = tk.Entry(self.ui_ph_grid_frame, 
                                    textvariable=self._ph_grid[2], width=6)
        self.ui_ph_grid = [self.ui_ph_grid_0, self.ui_ph_grid_1, self.ui_ph_grid_2]
        self.ui_ph_reference = Pmw.OptionMenu(self.canvas, 
                                    menubutton_textvariable=self._ph_reference,
                                    items=['neutral', 'low-pH'])
 
        self.ui_titrate_frame = tk.Frame(self.canvas)
        self.ui_titrate_entry = tk.Entry(self.ui_titrate_frame, textvariable=self._titrate, width=15)
        self.ui_titrate_btn = tk.Button(self.ui_titrate_frame, text='+')
        self.ui_titrate = [self.ui_titrate_entry, self.ui_titrate_btn]

        self.ui_keep_protons = tk.Checkbutton(self.canvas, variable=self._keep_protons,
                                              anchor='w')
        self.ui_mutations = tk.Entry(self.canvas, textvariable=self._mutations)
        self.ui_mutations_method = tk.OptionMenu(self.canvas, self._mutations_method,
                                                  'alignment', 'scwrl', 'jackal')
        self.ui_mutations_options = tk.Entry(self.canvas, textvariable=self._mutations_options)

        labeled_widgets = {
            (0, 'ui_chains_frame'): 'Chains',
            (1, 'ui_ph') : 'pH',
            (2, 'ui_ph_window_frame') : 'pH window',
            (3, 'ui_ph_grid_frame') : 'pH grid',
            (4, 'ui_ph_reference') : 'pH reference',
            (5, 'ui_titrate_frame') : 'Titrate only',
            (6, 'ui_keep_protons') : 'Keep protons',
            # (7, 'ui_mutations'): 'Mutations',
            # (8, 'ui_mutations_method'): 'Mutation method',
            # (9, 'ui_mutations_options'): 'Mutation options',
        }
        for (i, attr), title in sorted(labeled_widgets.items()):
            tk.Label(self.canvas, text=title).grid(row=i+1, column=0, sticky='e', padx=4, pady=1)
            getattr(self, attr).grid(row=i+1, column=1, padx=4, pady=1, sticky='we')

        left_packed = self.ui_ph_window + self.ui_ph_grid + self.ui_chains + self.ui_titrate
        for widget in left_packed:
            expand, fill = True, 'both'
            if isinstance(widget, tk.Button):
                expand, fill = False, None
            widget.pack(side='left', padx=1, expand=expand, fill=fill)

    def Run(self):
        pass

    def Close(self):
        global ui
        ui = None
        super(PropKaDialog, self).Close()


class PropKaResultsDialog(PlumeBaseDialog):

    buttons = ('Close',)
    _show_attr_dialog = None

    def __init__(self, molecules=None, *args, **kwargs):
        self.molecules = molecules
        if molecules:
            names = ', '.join(m.name for m in molecules)
            self.title = 'PropKa results for {}'.format(names)
        else:
            self.title = 'PropKa results'
        self._data = None

        self._original_colors = {}

        super(PropKaResultsDialog, self).__init__(*args, **kwargs)

    def fill_in_ui(self, parent):
        self.canvas.columnconfigure(0, weight=1)

        self.ui_table_frame = tk.LabelFrame(master=self.canvas, text='Per-residue information')
        self.ui_table = SortableTable(self.ui_table_frame)
        self.var_show_backbone_values = tk.IntVar()
        self.ui_show_bb_values_check = tk.Checkbutton(self.ui_table_frame, 
            text='Show backbone values',
            variable=self.var_show_backbone_values,
            command=self._populate_table)

        self.ui_plot_frame = tk.LabelFrame(self.canvas, text='Per-pH information')
        self.plot_figure = Figure(figsize=(4, 4), dpi=100, facecolor='#D9D9D9')
        self.plot_widget = FigureCanvasTkAgg(self.plot_figure, master=self.ui_plot_frame)
        self.plot = self.plot_figure.add_subplot(111)

        self.ui_actions_frame = tk.LabelFrame(self.canvas, text='Actions')
        self.ui_actions_0 = tk.Button(self.ui_actions_frame, text='Color by pKa', 
                                      command=self.color_by_pka)
        self.ui_actions_1 = tk.Button(self.ui_actions_frame, text='Color by charge', 
                                      command=self.color_by_charge)
        self.ui_actions_2 = tk.Button(self.ui_actions_frame, text='Reset color', 
                                      command=self.reset_colors)
        self.ui_actions = [self.ui_actions_0, self.ui_actions_1, self.ui_actions_2]
        self.ui_other_frame = tk.LabelFrame(self.canvas, text='Key pH values')

        # Pack and grid
        self.ui_table_frame.grid(row=0, columnspan=1, sticky='news', padx=5, pady=5)
        self.ui_table.pack(expand=True, fill='both', padx=5, pady=5)
        self.ui_show_bb_values_check.pack(expand=True, fill='both', padx=5, pady=5)

        self.ui_actions_frame.grid(row=0, column=1, sticky='news', padx=5, pady=5)
        for button in self.ui_actions:
            button.pack(padx=5, pady=5)
        self.ui_other_frame.grid(row=0, column=2, sticky='news', padx=5, pady=5)

        self.ui_plot_frame.grid(row=1, columnspan=3, sticky='news', padx=5, pady=5)
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
            show_backbone = self.var_show_backbone_values.get()

        columns = [('#', itemgetter(0)), ('Residues', itemgetter(1)), 
                   ('pKa', itemgetter(2)), ('Charge', itemgetter(3))]
        for column, fetcher in columns:
            self.ui_table.addColumn(column, fetcher, refresh=False)
        table_data = []
        for residue, pka in data['residues_pka'].items():
            restype, respos, chainid = residue
            if not show_backbone and restype in ('BBC', 'BBN'):
                continue
            charge = data['residues_charge'][residue]
            key = ':{}.{} {}'.format(respos, chainid, restype)
            table_data.append((respos, key, pka, charge))
        
        self.ui_table.setData(sorted(table_data))
        try: 
            self.ui_table.launch()
        except tk.TclError: 
            self.ui_table.refresh(rebuild=True)

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
            tk.Label(self.ui_other_frame, text=label + ':').grid(row=i, column=0, sticky='w',
                padx=10, pady=5)
            tk.Label(self.ui_other_frame, text=value).grid(row=i, column=1, sticky='e',
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
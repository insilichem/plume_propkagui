#!/usr/bin/env python
# encoding: utf-8

# Get used to importing this in your Py27 projects!
from __future__ import print_function, division
# Python stdlib
import Tkinter as tk
# Chimera stuff
import chimera
from OpenSave import osTemporaryFile
# Additional 3rd parties
import propka
# Own


"""
This module contains the business logic of your extension. Normally, it should
contain the Controller and the Model. Read on MVC design if you don't know about it.
"""


class Controller(object):

    """
    The controller manages the communication between the UI (graphic interface)
    and the data model. Actions such as clicks on buttons, enabling certain areas, 
    or running external programs, are the responsibility of the controller.
    """

    def __init__(self, gui, model, *args, **kwargs):
        self.molecules_chimera_to_propka = {}
        self.molecules_propka_to_chimera = {}

    def run(self):
        cli_args = self.optional_arguments()
        for molecule in self.molecules:
            self.run_single(molecule, cli_args)

    def run_single(self, molecule, options):
        pdb = self.write_pdb(molecule)
        results = propka_run(pdb, options)

    @property
    def molecules(self):
        return self.gui.molecules_list.getvalue()

    def write_pdb(self, molecule, path=None):
        if path is None:
            path = osTemporaryFile(suffix='.pdb')
        chimera.pdbWrite([molecule], filename=path)
        return path

    def optional_arguments(self):
        args = []
        if self.model.ph:
            args.append('-o')
            args.append(self.model.ph)
        if self.model.ph_window:
            args.append('-w')
            args.append(self.model.ph_window)
        if self.model.ph_grid:
            args.append('-g')
            args.append(self.model.ph_grid)
        if self.model.ph_reference:
            args.append('-r')
            args.append(self.model.ph_reference)
        if self.model.mutations:
            args.append('-m')
            args.append(self.model.mutations)
        if self.model.mutation_method:
            args.append('--mutator={}'.format(self.model.mutation_method))
        if self.model.mutation_options:
            args.append('--mutator-option={}'.format(self.model.mutation_options))
        if self.model.titrate_only:
            args.append('-i')
            args.append(self.model.titrate_only)
        if self.model.keep_protons:
            args.append('-k')
        if self.model.chains:
            args.append('-c')
            args.append(self.model.chains)

        return args


class Model(object):

    """
    The model controls the data we work with. Normally, it'd be a Chimera molecule
    and some input files from other programs. The role of the model is to create
    a layer around those to allow the easy access and use to the data contained in
    those files
    """

    def __init__(self, *args, **kwargs):
        self._ph = tk.DoubleVar()
        self._ph_window = tk.DoubleVar()
        self._ph_grid = tk.DoubleVar()
        self._ph_reference = tk.StringVar()
        self._mutations = tk.StringVar()
        self._mutation_method = tk.StringVar()
        self._mutation_options = tk.StringVar()
        self._titrate_only = tk.StringVar()
        self._keep_protons = tk.BooleanVar()
        self._chains = tk.StringVar()

    @property
    def ph(self):
        return self._ph.get()

    @ph.setter
    def ph(self, value):
        value = float(value)
        if 0 <= value <= 14.0:
            self._ph.set(value)

    @property
    def ph_window(self):
        return self._ph_window.get()

    @ph_window.setter
    def ph_window(self, value):
        self._ph_window.set(value)

    @property
    def ph_grid(self):
        return self._ph_grid.get()

    @ph_grid.setter
    def ph_grid(self, value):
        self._ph_grid.set(value)

    @property
    def ph_reference(self):
        return self._ph_reference.get()

    @ph_reference.setter
    def ph_reference(self, value):
        self._ph_reference.set(value)

    @property
    def mutations(self):
        return self._mutations.get()

    @mutations.setter
    def mutations(self, value):
        self._mutations.set(value)

    @property
    def mutation_method(self):
        return self._mutation_method.get()

    @mutation_method.setter
    def mutation_method(self, value):
        self._mutation_method.set(value)

    @property
    def mutation_options(self):
        return self._mutation_options.get()

    @mutation_options.setter
    def mutation_options(self, value):
        self._mutation_options.set(value)

    @property
    def titrate_only(self):
        return self._titrate_only.get()

    @titrate_only.setter
    def titrate_only(self, value):
        self._titrate_only.set(value)

    @property
    def keep_protons(self):
        return self._keep_protons.get()

    @keep_protons.setter
    def keep_protons(self, value):
        self._keep_protons.set(value)

    @property
    def chains(self):
        return self._chains.get()

    @chains.setter
    def chains(self, value):
        self._chains.set(value)


def propka_run(pdb, cli_options):
    """
    Run a PropKa job and get all values back in a programmatic way.
    """
    args, _ = propka.lib.loadOptions(*cli_options)
    propka_mol = propka.molecular_container.Molecular_container(pdb, args)
    residues_pka, residues_charge = {}, {}
    for conformation in propka_mol.conformations:
        conformation.calculate_pka(propka_mol.version, propka_mol.options)
        for group in conformation.groups:
            key = group.residue_type, group.atom.resNumb, group.atom.chainID
            residues_pka[key] = group.pka_value
            residues_charge[key] = group.charge

    propka_mol.find_non_covalently_coupled_groups()
    propka_mol.average_of_conformations()

    charge_profile = propka_mol.getChargeProfile(grid=args.grid)
    folded_pi, unfolded_pi = propka_mol.getPI(grid=args.grid)
    folding_profile, (pH_opt, dG_opt), (dG_min, dG_max), (pH_min, pH_max) = \
        propka_mol.getFoldingProfile(reference=args.reference, grid=args.grid)

    return {'residues_pka': residues_pka,
            'residues_charge': residues_charge,
            'charge_profile': charge_profile,
            'folded_pi': folded_pi,
            'unfolded_pi': unfolded_pi,
            'folding_profile': folding_profile,
            'pH_opt': pH_opt,
            'dG_opt': dG_opt,
            'dG_min': dG_min,
            'dG_max': dG_max,
            'pH_min': pH_min,
            'pH_max': pH_max}

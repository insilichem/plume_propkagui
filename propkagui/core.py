#!/usr/bin/env python
# encoding: utf-8


from __future__ import print_function, division
# Python stdlib
import contextlib
import os
# Chimera stuff
import chimera
from OpenSave import osTemporaryFile
# Additional 3rd parties
try:
    import propka
    import propka.lib
    import propka.molecular_container
except ImportError as e :
    raise chimera.UserError("PropKa is not installed!" + str(e))
# Own
from libtangram.core import ignored, enter_directory
import gui


class Controller(object):

    results = {}

    def __init__(self, gui, model, *args, **kwargs):
        self.gui = gui
        self.model = model

    def run(self):
        cli_args = self.optional_arguments
        for molecule in self.molecules:
            self.results[molecule] = results = self.run_single(molecule, cli_args)
        results_dialog = gui.PropKaResultsDialog(master=self.gui.uiMaster(),
                                                 molecules=self.molecules)
        results_dialog.fillInData(results)
        results_dialog.enter()

    def run_single(self, molecule, options):
        pdb = self.write_pdb(molecule)
        with enter_directory(os.path.dirname(pdb)):
            results = propka_run(pdb, options)
        return results

    def set_mvc(self):
        # Tie model and gui
        names = ['ph', 'ph_window', 'ph_grid', 'ph_reference', 'mutations', 'chains',
                 'mutations_method', 'mutations_options', 'titrate', 'keep_protons']
        for name in names:
            with ignored(AttributeError):
                var = getattr(self.model, '_' + name)
                var.trace(lambda *args: setattr(self.model, name, var.get()))

        # Buttons callbacks
        self.gui.buttonWidgets['Run'].configure(command=self.run)

    @property
    def molecules(self):
        return self.gui.ui_molecules.getvalue(),

    @property
    def optional_arguments(self):
        args = ['-q'] # quiet
        if self.model.ph:
            args.append('-o')
            args.append(self.model.ph)
        if self.model.ph_window:
            args.append('-w')
            args.extend(self.model.ph_window)
        if self.model.ph_grid:
            args.append('-g')
            args.extend(self.model.ph_grid)
        if self.model.ph_reference:
            args.append('-r')
            args.append(self.model.ph_reference)
        if self.model.mutations:
            args.append('-m')
            args.append(self.model.mutations)
        if self.model.mutations_method:
            args.append('--mutator={}'.format(self.model.mutations_method))
        if self.model.mutations_options:
            args.append('--mutator-option={}'.format(self.model.mutations_options))
        if self.model.titrate:
            args.append('-i')
            args.append(self.model.titrate)
        if self.model.keep_protons:
            args.append('-k')
        if self.model.chains:
            args.append('-c')
            args.append(self.model.chains)

        return args

    @staticmethod
    def write_pdb(molecule, path=None):
        if path is None:
            path = osTemporaryFile(suffix='.pdb')
        chimera.pdbWrite([molecule], molecule.openState.xform, path)
        return path


class ViewModel(object):

    defaults = {
        'ph': 7.0,
        'ph_window': [0, 14, 1],
        'ph_grid': [0, 14, 1],
        'ph_reference': 'neutral',
        'mutations': '',
        'mutations_method': 'alignment',
        'mutations_options': '',
        'titrate': '',
        'keep_protons': True,
        'chains': '',
    }

    def __init__(self, gui, *args, **kwargs):
        self.gui = gui
        self.set_defaults()

    def set_defaults(self):
        for name, value in self.defaults.items():
            setattr(self, name, value)

    @property
    def ph(self):
        return self.gui._ph.get()

    @ph.setter
    def ph(self, value):
        value = float(value)
        if 0 <= value <= 14.0:
            self.gui._ph.set(value)

    @property
    def ph_window(self):
        return [var.get() for var in self.gui._ph_window]

    @ph_window.setter
    def ph_window(self, values):
        for var, value in zip(self.gui._ph_window, values):
            var.set(value)

    @property
    def ph_grid(self):
        return [var.get() for var in self.gui._ph_grid]

    @ph_grid.setter
    def ph_grid(self, values):
        for var, value in zip(self.gui._ph_grid, values):
            var.set(value)

    @property
    def ph_reference(self):
        return self.gui._ph_reference.get()

    @ph_reference.setter
    def ph_reference(self, value):
        self.gui._ph_reference.set(value)

    @property
    def mutations(self):
        return self.gui._mutations.get()

    @mutations.setter
    def mutations(self, value):
        self.gui._mutations.set(value)

    @property
    def mutations_method(self):
        return self.gui._mutations_method.get()

    @mutations_method.setter
    def mutations_method(self, value):
        self.gui._mutations_method.set(value)

    @property
    def mutations_options(self):
        return self.gui._mutations_options.get()

    @mutations_options.setter
    def mutations_options(self, value):
        self.gui._mutations_options.set(value)

    @property
    def titrate(self):
        return self.gui._titrate.get()

    @titrate.setter
    def titrate(self, value):
        self.gui._titrate.set(value)

    @property
    def keep_protons(self):
        return bool(self.gui._keep_protons.get())

    @keep_protons.setter
    def keep_protons(self, value):
        self.gui._keep_protons.set(value)

    @property
    def chains(self):
        return self.gui._chains.get()

    @chains.setter
    def chains(self, value):
        self.gui._chains.set(value)


def propka_run(pdb, cli_options):
    """
    Run a PropKa job and get all values back programmatically.

    Parameters
    ----------
    pdb : str
        Path to PDB file that contains the molecule to be analyzed.
    cli_options : list of str
        List of arguments that would have been passed in a CLI environment.
    """
    args, _ = propka.lib.loadOptions(*cli_options)
    propka_mol = propka.molecular_container.Molecular_container(pdb, args)

    residues_pka, residues_charge = {}, {}
    for name, conformation in propka_mol.conformations.items():
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
            'pi_folded': folded_pi,
            'pi_unfolded': unfolded_pi,
            'folding_profile': folding_profile,
            'pH_opt': pH_opt,
            'dG_opt': dG_opt,
            'dG_min': dG_min,
            'dG_max': dG_max,
            'pH_min': pH_min,
            'pH_max': pH_max}

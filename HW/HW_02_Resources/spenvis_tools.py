"""
spenvis_tools.py
----------------
Generic reader + plotting helpers for SPENVIS report files (.txt) used in the
RADFX space-environment homework.

Author: D. Loveless, dlovele@iu.edu
Date of last update: 2026-Sept-10

Typical use (see generate_spenvis_plots_example.ipynb):

    from spenvis_tools import Mission, load_missions, plot_spectra, threshold_table

    missions = load_missions("./", {
        "Starlink LEO": "starlink",
        "Polar LEO":    "polar_leo",
        "HEO":          "heo",
    })
    plot_spectra(missions, "trapped_protons")
    plot_spectra(missions, "solar_ions_flux", ions=["He", "Fe"])
    threshold_table(missions, "trapped_protons", energies=[1, 10, 200])

Design notes
------------
* One SPENVIS file holds one or more *blocks* (separated by 'End of Block' /
  'End of File').  Every block is parsed into a `Block` with its header records
  (a dict), its column definitions (names + units) and a numeric numpy array.
* Species blocks (92 ions) get one IFlux/DFlux column per element, so any ion
  can be requested by symbol ("He", "Fe", "Xe", ...) - nothing is hard-coded.
* Units are read from the column definition lines and fluxes given in m^-2 are
  converted to cm^-2 automatically (factor 1e-4).  Everything downstream is in
  cm^-2 (s^-1 sr^-1 where applicable).
* The "analyses" (trapped protons, solar proton flux, ...) are just named
  recipes in the ANALYSES table: which file kind, which PLT_HDR text to match,
  and the axis labels.  Add a new analysis by adding one entry.
"""

from __future__ import annotations

import glob
import os
import re
from dataclasses import dataclass, field
from itertools import cycle
from typing import Dict, Iterable, List, Optional, Sequence

import numpy as np

try:
    import matplotlib.pyplot as plt
except ImportError:  # plotting is optional for the parser
    plt = None

# ----------------------------------------------------------------------------
# Low-level parser
# ----------------------------------------------------------------------------

_QUOTED = re.compile(r"'((?:[^']|'')*)'")


def _split_record(line: str) -> List[str]:
    """Split a SPENVIS header record into fields, respecting single quotes."""
    fields, buf, inq = [], "", False
    for ch in line:
        if ch == "'":
            inq = not inq
        elif ch == "," and not inq:
            fields.append(buf.strip())
            buf = ""
        else:
            buf += ch
    fields.append(buf.strip())
    return fields


@dataclass
class Block:
    """One data block of a SPENVIS report."""
    header: Dict[str, object] = field(default_factory=dict)   # e.g. MOD_ABB, PLT_HDR, TRP_MOD, ORB_HDR
    species: List[str] = field(default_factory=list)           # ['proton'] or ['H','He',...]
    columns: List[str] = field(default_factory=list)           # expanded column names
    units: Dict[str, str] = field(default_factory=dict)        # column -> unit string
    data: np.ndarray = field(default_factory=lambda: np.empty((0, 0)))

    # -- convenience -----------------------------------------------------
    @property
    def model(self) -> str:
        return str(self.header.get("MOD_ABB", ""))

    @property
    def plot_header(self) -> str:
        return str(self.header.get("PLT_HDR", ""))

    def col(self, name: str) -> np.ndarray:
        return self.data[:, self.columns.index(name)]

    @property
    def energy(self) -> np.ndarray:
        return self.col("Energy")

    def flux(self, kind: str = "IFlux", ion: Optional[str] = None,
             to_cm2: bool = True) -> np.ndarray:
        """Integral ('IFlux') or differential ('DFlux') flux/fluence column.

        `ion` is required for species blocks (e.g. 'He', 'Fe'); ignored otherwise.
        Values are converted from m^-2 to cm^-2 when `to_cm2` is True.
        """
        if len(self.species) > 1:
            if ion is None:
                raise ValueError(f"block has {len(self.species)} species; specify ion=")
            name = f"{kind}_{ion.strip()}"
        else:
            name = kind
        vals = self.col(name)
        unit = self.units.get(name, "")
        if to_cm2 and "m!u-2!n" in unit and "cm!u-2" not in unit:
            vals = vals * 1e-4
        return vals

    def unit(self, kind: str = "IFlux", ion: Optional[str] = None, to_cm2=True) -> str:
        name = f"{kind}_{ion.strip()}" if (len(self.species) > 1 and ion) else kind
        u = self.units.get(name, "")
        if to_cm2:
            u = u.replace("m!u-2!n", "cm!u-2!n") if "cm!u-2" not in u else u
        return pretty_unit(u)


def pretty_unit(u: str) -> str:
    """Turn SPENVIS 'cm!u-2!n s!u-1!n' into 'cm⁻² s⁻¹'."""
    sup = str.maketrans("-0123456789", "⁻⁰¹²³⁴⁵⁶⁷⁸⁹")
    return re.sub(r"!u([-\d]+)!n", lambda m: m.group(1).translate(sup), u).strip()


def parse_spenvis(filename: str) -> List[Block]:
    """Parse a SPENVIS report file into a list of Blocks."""
    with open(filename, "r", errors="replace") as fh:
        lines = [ln.rstrip("\n") for ln in fh]

    blocks: List[Block] = []
    blk = Block()
    coldefs: List[tuple] = []   # (name, unit, count)
    rows: List[List[float]] = []
    skip_annotation = 0
    in_data = False

    def flush():
        nonlocal blk, coldefs, rows, in_data
        if coldefs:
            names, units = [], {}
            for name, unit, count in coldefs:
                if count == 1:
                    names.append(name); units[name] = unit
                else:
                    for sp in blk.species[:count]:
                        n = f"{name}_{sp.strip()}"
                        names.append(n); units[n] = unit
            blk.columns, blk.units = names, units
            blk.data = np.array(rows, dtype=float) if rows else np.empty((0, len(names)))
            blocks.append(blk)
        blk, coldefs, rows, in_data = Block(), [], [], False

    for raw in lines:
        line = raw.strip()
        if not line:
            continue
        if line.startswith("'End of"):
            flush(); continue

        if line.startswith("'"):
            f = _split_record(line)
            key = f[0]
            if key == "*" or key.startswith("SPENVIS"):
                continue
            if key == "PS Annotation":
                # 'PS Annotation', n, m  -> followed by n (text, coords) pairs
                skip_annotation = int(f[1]); continue
            if skip_annotation:
                skip_annotation -= 1; continue
            if key == "SPECIES":
                blk.species = [s for s in f[2:]]
                continue
            # column definition: 'Name','unit', count,'description'[,'SPECIES']
            if len(f) >= 4 and f[2].lstrip("-").isdigit() and not in_data and (
                key in ("Energy", "IFlux", "DFlux", "LET") or coldefs
            ):
                coldefs.append((key, f[1], int(f[2])))
                continue
            # generic header record: 'KEY', n, value[, unit]
            if len(f) >= 3:
                val = f[2]
                try:
                    val = float(val)
                    if val.is_integer():
                        val = int(val)
                except ValueError:
                    pass
                blk.header[key] = val
            continue

        if skip_annotation:      # coordinate line following an annotation text
            skip_annotation -= 1; continue
        # numeric row
        try:
            rows.append([float(x) for x in line.split(",") if x.strip()])
            in_data = True
        except ValueError:
            continue
    flush()
    return blocks


def find_block(blocks: Iterable[Block], plt_hdr: Optional[str] = None,
               species: Optional[str] = None, model: Optional[str] = None) -> Block:
    """Return the first block matching the given PLT_HDR substring / species / MOD_ABB."""
    for b in blocks:
        if plt_hdr and plt_hdr.lower() not in b.plot_header.lower():
            continue
        if model and b.model != model:
            continue
        if species and not (b.species == [species] or species in b.species):
            continue
        return b
    raise KeyError(f"no block with plt_hdr~'{plt_hdr}', species={species}, model={model}; "
                   f"available: {[b.plot_header for b in blocks]}")


# ----------------------------------------------------------------------------
# Missions
# ----------------------------------------------------------------------------

# SPENVIS file "kinds" as they appear in the filenames: <prefix>_spenvis_<kind>.txt
FILE_KINDS = {
    "tri":      "trapped radiation (AP-8 / AE-8)",
    "sefflare": "solar particle event flux (CREME-96 worst day)",
    "sef":      "solar particle mission fluence (ESP-PSYCHIC)",
    "gcf":      "galactic cosmic ray flux (CREME-96)",
}


@dataclass
class Mission:
    label: str
    files: Dict[str, str]                      # kind -> path
    _cache: Dict[str, List[Block]] = field(default_factory=dict, repr=False)

    @classmethod
    def from_prefix(cls, label: str, prefix: str, folder: str = ".") -> "Mission":
        files = {}
        for kind in FILE_KINDS:
            cands = glob.glob(os.path.join(folder, f"{prefix}*spenvis_{kind}.txt"))
            if cands:
                files[kind] = cands[0]
        if not files:
            raise FileNotFoundError(f"no '{prefix}*spenvis_*.txt' files in {folder}")
        return cls(label, files)

    def blocks(self, kind: str) -> List[Block]:
        if kind not in self.files:
            raise KeyError(f"mission '{self.label}' has no '{kind}' file "
                           f"({FILE_KINDS.get(kind, kind)})")
        if kind not in self._cache:
            self._cache[kind] = parse_spenvis(self.files[kind])
        return self._cache[kind]

    def orbit(self) -> Dict[str, object]:
        """Orbit header values (from whichever file is available)."""
        b = self.blocks(next(iter(self.files)))[0].header
        keys = ["ORB_HDR", "ORB_APO", "ORB_PER", "ORB_INC", "ORB_PRD", "MIS_DUR"]
        return {k: b.get(k) for k in keys if k in b}

    def spectrum(self, analysis: str, ion: Optional[str] = None,
                 kind: str = "IFlux"):
        """(energy, values, unit_string) for a named analysis (see ANALYSES)."""
        a = ANALYSES[analysis]
        blk = find_block(self.blocks(a["file"]), plt_hdr=a["plt_hdr"],
                         species=a.get("species"))
        return blk.energy, blk.flux(kind, ion), blk.unit(kind, ion)


def load_missions(folder: str, missions: Dict[str, str]) -> List[Mission]:
    """missions = {label: filename_prefix}. Returns a list of Mission objects."""
    return [Mission.from_prefix(label, prefix, folder) for label, prefix in missions.items()]


# ----------------------------------------------------------------------------
# Analyses: which file, which block, how to label it
# ----------------------------------------------------------------------------

ANALYSES: Dict[str, Dict[str, object]] = {
    "trapped_protons": dict(
        file="tri", plt_hdr="Orbit averaged flux", species="proton",
        title="Trapped Proton Integral Flux", xlim=(0.1, 1e3), ions=False),
    "trapped_electrons": dict(
        file="tri", plt_hdr="Orbit averaged flux", species="e-",
        title="Trapped Electron Integral Flux", xlim=(0.01, 10), ions=False),
    "solar_protons_flux": dict(
        file="sefflare", plt_hdr="solar protons",
        title="Solar Proton Integral Flux (CREME-96 worst day)", xlim=(0.1, 1e3), ions=False),
    "solar_ions_flux": dict(
        file="sefflare", plt_hdr="solar ions",
        title="Solar Heavy Ion Integral Flux (CREME-96 worst day)", xlim=(0.1, 1e3), ions=True),
    "solar_protons_fluence": dict(
        file="sef", plt_hdr="solar protons",
        title="Mission Solar Proton Integral Fluence (ESP-PSYCHIC)", xlim=(0.1, 1e3), ions=False),
    "solar_ions_fluence": dict(
        file="sef", plt_hdr="solar ions",
        title="Mission Solar Heavy Ion Integral Fluence (ESP-PSYCHIC)", xlim=(0.1, 1e3), ions=True),
    "gcr_ions_flux": dict(
        file="gcf", plt_hdr="ion spectrum (GCR)",
        title="GCR Integral Flux (CREME-96)", xlim=(0.1, 1e6), ions=True),
}

DEFAULT_IONS = ["H", "He", "Fe"]

# Per-mission marker/linestyle, per-ion fill/linestyle - extend freely.
_MARKERS = ["o", "s", "^", "D", "v", "P", "X", "*"]
_ION_STYLE = {  # ion -> (linestyle, filled marker?)
    "H": ("-", True), "He": ("--", True), "Fe": (":", False),
}
_FALLBACK_ION_STYLES = cycle([("-.", False), ("-", False), ("--", False)])


def _ion_style(ion: str):
    if ion not in _ION_STYLE:
        _ION_STYLE[ion] = next(_FALLBACK_ION_STYLES)
    return _ION_STYLE[ion]


# ----------------------------------------------------------------------------
# Plotting
# ----------------------------------------------------------------------------

def plot_spectra(missions: Sequence[Mission], analysis: str,
                 ions: Optional[Sequence[str]] = None, kind: str = "IFlux",
                 xlim=None, ylim=None, title: Optional[str] = None,
                 savefig: Optional[str] = None, ax=None, figsize=(10, 6),
                 show: bool = True):
    """Overlay one analysis for every mission (and every requested ion).

    analysis : key of ANALYSES, e.g. "trapped_protons", "gcr_ions_flux"
    ions     : list of element symbols for ion analyses (default DEFAULT_IONS)
    kind     : "IFlux" (integral) or "DFlux" (differential)
    """
    if plt is None:
        raise RuntimeError("matplotlib is not available")
    a = ANALYSES[analysis]
    is_ion = bool(a.get("ions"))
    ions = list(ions or DEFAULT_IONS) if is_ion else [None]

    if ax is None:
        fig, ax = plt.subplots(figsize=figsize)
    else:
        fig = ax.figure

    colors = plt.rcParams["axes.prop_cycle"].by_key()["color"]
    unit = ""
    for mi, m in enumerate(missions):
        color, marker = colors[mi % len(colors)], _MARKERS[mi % len(_MARKERS)]
        for ion in ions:
            try:
                e, v, unit = m.spectrum(analysis, ion=ion, kind=kind)
            except KeyError as err:
                print(f"skipping {m.label} / {analysis}: {err}")
                continue
            ls, filled = _ion_style(ion) if ion else ("-", True)
            label = f"{m.label} {ion}" if ion else m.label
            mask = v > 0                                   # log axes: drop zeros
            ax.loglog(e[mask], v[mask], marker=marker, linestyle=ls, color=color,
                      mfc=(color if filled else "w"), label=label)

    ylabel = ("Integral " if kind == "IFlux" else "Differential ") + \
             ("Fluence" if "fluence" in analysis else "Flux") + f" ({unit})"
    ax.set_xlabel("Energy (MeV/n)" if is_ion else "Energy (MeV)")
    ax.set_ylabel(ylabel)
    ax.set_title(title or a["title"])
    ax.set_xlim(xlim or a.get("xlim"))
    if ylim:
        ax.set_ylim(ylim)
    ax.grid(True, which="both", ls="--", lw=0.5)
    ax.legend()
    fig.tight_layout()
    if savefig:
        fig.savefig(savefig, dpi=150)
    if show:
        plt.show()
    return ax


def plot_all(missions: Sequence[Mission], ions: Sequence[str] = ("He", "Fe"),
             gcr_ions: Sequence[str] = ("H", "He", "Fe"), outdir: Optional[str] = None,
             show: bool = True):
    """Produce the standard set of homework plots for any number of missions."""
    plan = [
        ("trapped_protons", None), ("trapped_electrons", None),
        ("solar_protons_flux", None), ("solar_ions_flux", ions),
        ("solar_protons_fluence", None), ("solar_ions_fluence", ions),
        ("gcr_ions_flux", gcr_ions),
    ]
    for analysis, ion_list in plan:
        out = os.path.join(outdir, f"{analysis}.png") if outdir else None
        plot_spectra(missions, analysis, ions=ion_list, savefig=out, show=show)


# ----------------------------------------------------------------------------
# Numbers: integral flux/fluence above threshold energies, mission ratios
# ----------------------------------------------------------------------------

def value_at(energy: np.ndarray, values: np.ndarray, e0: float) -> float:
    """Log-log interpolation of an integral spectrum at energy e0."""
    m = (values > 0) & (energy > 0)
    e, v = energy[m], values[m]
    if e0 < e.min() or e0 > e.max():
        return float("nan")
    return float(np.exp(np.interp(np.log(e0), np.log(e), np.log(v))))


def threshold_table(missions: Sequence[Mission], analysis: str,
                    energies: Sequence[float] = (1, 10, 200), ion: Optional[str] = None,
                    reference: Optional[str] = None):
    """Integral flux/fluence above each threshold energy, per mission.

    Returns a pandas DataFrame (missions x energies). If `reference` names a
    mission label, a second set of columns gives the ratio to that mission.
    """
    import pandas as pd
    rows, unit = {}, ""
    for m in missions:
        e, v, unit = m.spectrum(analysis, ion=ion)
        rows[m.label] = {f">{E:g} MeV": value_at(e, v, E) for E in energies}
    df = pd.DataFrame(rows).T
    df.columns.name = unit
    if reference:
        ratio = df.div(df.loc[reference])
        ratio.columns = [f"{c} / {reference}" for c in ratio.columns]
        df = pd.concat([df, ratio], axis=1)
    return df


def summarize(missions: Sequence[Mission]):
    """Orbit parameters of every loaded mission as a DataFrame."""
    import pandas as pd
    return pd.DataFrame({m.label: m.orbit() for m in missions}).T

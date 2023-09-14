from pstl.diagnostics.probes.langmuir.single.analysis.utls.ion_current import thick,thin,transitional


"""
rp: Radius of Probe
LDe: Electron Debye Length

Let rp/LDe = ratio

Then
If ratio <= 3       ->  Thick Sheath
If 3 < ratio < 50   ->  Transitional Sheath
If ratio >= 50      ->  Thin Sheath
"""
# parsing, hashing, grouping, adapters
import datetime
import hashlib
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import List, Optional
from uuid import uuid4

import numpy as np


@dataclass(frozen=True)
class Calculation:
    id: str
    file: str
    output_hash: str
    geometry: str
    geometry_hash: str
    charge: int
    mult: int
    date_added: str
    date: str
    input: str


def process_all(root: Path) -> List[Calculation]:
    out_files = list(root.rglob("*.out"))
    items = []
    for f in out_files:
        calc = process_file(f)
        if calc:
            items.append(calc)
    return items


def process_file(path: Path) -> Optional[Calculation]:
    # --- adapter logic in one place ---
    from orca_studio import OrcaOutput  # type: ignore
    from orca_studio.parse.common import OrcaParsingError  # type: ignore

    try:
        data = OrcaOutput(path)
        xyz = str(data.molecule)
    except OrcaParsingError:
        return None

    # hash only coordinates, not n_atoms and comment
    geom_hash = hashlib.sha256(
        "\n".join(line.strip() for line in xyz.splitlines()[2:]).encode()
    ).hexdigest()

    return Calculation(
        id=str(uuid4()),
        file=str(path.resolve()),
        output_hash=hashlib.sha256(path.read_text().encode()).hexdigest(),
        geometry=xyz,
        geometry_hash=geom_hash,
        charge=data.charge,
        mult=data.mult,
        date_added=f"{date.today():%Y-%m-%d}",
        date=f"{datetime.datetime.fromtimestamp(path.stat().st_mtime):%Y-%m-%d}",
        input=data.calc_input,
    )


def cluster_by_hash(items: List[Calculation]) -> dict[str, List[str]]:
    groups: dict[str, List[str]] = {}
    for itm in items:
        groups.setdefault(itm.geometry_hash, []).append(itm.id)
    return groups


def plain_rmsd(xyz1: np.ndarray, xyz2: np.ndarray) -> float:
    if xyz1.shape != xyz2.shape:
        raise ValueError("shapes differ")
    diff = xyz1 - xyz2
    return ((diff**2).sum() / len(xyz1)) ** 0.5


def cluster_by_rmsd(geoms: List[np.ndarray], threshold: float) -> List[List[int]]:
    clusters: List[List[int]] = []
    for i, g in enumerate(geoms):
        placed = False
        for c in clusters:
            if plain_rmsd(geoms[c[0]], g) < threshold:
                c.append(i)
                placed = True
                break
        if not placed:
            clusters.append([i])
    return clusters

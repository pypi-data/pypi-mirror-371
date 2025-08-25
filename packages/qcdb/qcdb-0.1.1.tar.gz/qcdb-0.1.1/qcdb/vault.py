# reading/writing/linting vault
from pathlib import Path

import yaml

from qcdb.core import Calculation


class Vault:
    def __init__(self, root: Path):
        self.root = root

        self.calcs = self.root / "calcs"
        self.calcs.mkdir(parents=True, exist_ok=True)
        self.seen_calc_hashes = self._load_existing_hashes(tag="output_hash")

        self.geoms = self.root / "geoms"
        self.geoms.mkdir(parents=True, exist_ok=True)
        self.seen_geom_hashes = self._load_existing_hashes(tag="geometry_hash")

    def _load_existing_hashes(self, tag: str = "output_hash") -> set[str]:
        hashes: set[str] = set()
        for md in self.calcs.glob("*.md"):
            text = md.read_text().split("---")
            if len(text) >= 3:
                fm = yaml.safe_load(text[1])
                tags = fm.get("tags", {})
                h = tags.get(tag)
                if h:
                    hashes.add(h)
        return hashes

    def add(self, items: list[Calculation]) -> None:
        for itm in items:
            idx = len(list(self.calcs.glob(f"calc_{itm.date}_*.md")))
            if itm.output_hash in self.seen_calc_hashes:
                continue
            front = itm.__dict__

            geometry = self.geoms / f"{itm.geometry_hash}.md"
            if not geometry.is_file():
                # Initialize with geometry
                geometry.write_text(
                    f"# Geometry\n```xyz\n{itm.geometry}\n```\n# Links\n"
                )
            content = geometry.read_text()
            content += f"[[{itm.id}]]\n"
            geometry.write_text(content)

            directories = self.root / "dirs"
            directories.mkdir(exist_ok=True, parents=True)
            parents = Path(itm.file).parents
            for p in parents[:3]:
                directory = directories / f"{p.name}.md"
                if directory.is_file():
                    content = directory.read_text()
                else:
                    content = "\n".join([f"[[{p}]]\n" for p in parents])

                content += f"[[{itm.id}]]\n"
                directory.write_text(content)

            body = "\n".join(
                [
                    "# Notes",
                    "",
                    f"Geometry [[{itm.geometry_hash}]]",
                    # f"Path {' '.join([f'[[{p.name}]]' for p in parents])}",
                ]
            )
            # optional: add `same geometry: [[id]]` lines
            text = "---\n" + yaml.safe_dump(front) + "---\n" + body
            fname = f"calc_{itm.date}_{idx:04d}.md"
            (self.calcs / fname).write_text(text)

    def lint(self) -> None:
        # basic checks: no duplicate output_hashes, all tags present, etc.
        # raise or print warnings if you find problems
        pass

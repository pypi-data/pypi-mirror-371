from pathlib import Path

from sh.contrib import git

from hatchling.plugin import hookimpl
from hatchling.version.source.plugin.interface import VersionSourceInterface
from versioning import pep440, semver2
from versioning.project import NoVersion


class SimpleGitVersioningVersionSource(VersionSourceInterface):  # pragma: no cover
    PLUGIN_NAME = "simple-git-versioning"

    def get_version_data(self) -> dict:
        try:
            scheme = self.config["scheme"]
        except KeyError:
            Project = pep440.Project
        else:
            if not isinstance(scheme, str):
                raise TypeError(
                    f"unexpected versioning scheme (tool.hatch.version.scheme): '{scheme}', expected 'pep440' or 'semver2'"
                )

            scheme = scheme.casefold()
            if scheme == "pep440":
                Project = pep440.Project
            elif scheme == "semver2":
                Project = semver2.Project
            else:
                raise ValueError(
                    f"unexpected versioning scheme (tool.hatch.version.scheme): '{scheme}', expected 'pep440' or 'semver2'"
                )

        with Project(path=Path(self.root)) as proj:
            revision = git("rev-parse", "--short", "HEAD").strip()
            try:
                return {"version": str(proj.version())}
            except NoVersion:
                if isinstance(proj, pep440.Project):
                    options = dict(dev=0, local=(revision,))
                elif isinstance(proj, semver2.Project):
                    options = dict(build=revision)
                return {"version": str(proj.release(**options))}


@hookimpl
def hatch_register_version_source():  # pragma: no cover
    return SimpleGitVersioningVersionSource

import logging
from copy import deepcopy

from pydantic import BaseModel, ValidationError

from labels.model.file import DependencyType, LocationReadCloser
from labels.model.package import Language, Package, PackageType
from labels.model.relationship import Relationship
from labels.model.release import Environment
from labels.model.resolver import Resolver
from labels.parsers.cataloger.java.model import JavaArchive, JavaPomProject
from labels.parsers.cataloger.java.package import package_url
from labels.utils.strings import format_exception

LOGGER = logging.getLogger(__name__)


class LockFileDependency(BaseModel):
    group: str
    name: str
    version: str
    line: int | None = None


def parse_gradle_lockfile(
    _resolver: Resolver | None,
    __: Environment | None,
    reader: LocationReadCloser,
) -> tuple[list[Package], list[Relationship]]:
    dependencies: list[LockFileDependency] = []
    packages: list[Package] = []
    for line_number, line in enumerate(reader.read_closer.readlines(), 1):
        if "=" in line and ":" in line:  # To ensure it's a dependency line
            dependency_part = line.split("=")[0]
            group, name, version = dependency_part.split(":")
            dependencies.append(
                LockFileDependency(group=group, name=name, version=version, line=line_number),
            )

    for dependency in dependencies:
        name = dependency.name
        version = dependency.version

        if not name or not version:
            continue

        location = deepcopy(reader.location)
        if location.coordinates:
            location.coordinates.line = dependency.line
        location.dependency_type = DependencyType.UNDETERMINABLE

        archive = JavaArchive(
            pom_project=JavaPomProject(
                group_id=dependency.group,
                name=name,
                artifact_id=name,
                version=version,
            ),
        )

        try:
            packages.append(
                Package(
                    name=f"{dependency.group}:{name}",
                    version=version,
                    locations=[location],
                    language=Language.JAVA,
                    type=PackageType.JavaPkg,
                    metadata=archive,
                    p_url=package_url(name, version, archive),
                    licenses=[],
                ),
            )
        except ValidationError as ex:
            LOGGER.warning(
                "Malformed package. Required fields are missing or data types are incorrect.",
                extra={
                    "extra": {
                        "exception": format_exception(str(ex)),
                        "location": location.path(),
                    },
                },
            )
            continue

    return packages, []

import logging
from copy import deepcopy

from packageurl import PackageURL
from pydantic import ValidationError

from labels.model.file import DependencyType, Location, Scope
from labels.model.indexables import IndexedDict, ParsedValue
from labels.model.package import Language, Package, PackageType
from labels.parsers.cataloger.javascript.model import NpmPackageLockEntry
from labels.utils.strings import format_exception

LOGGER = logging.getLogger(__name__)


def new_package_lock_v1(
    location: Location,
    name: str,
    value: IndexedDict[str, ParsedValue],
    *,
    is_transitive: bool,
) -> Package | None:
    version: str = str(value.get("version", ""))
    if not name or not version:
        return None

    alias_prefix_package_lock = "npm:"
    if version.startswith(alias_prefix_package_lock):
        name, version = version.removeprefix(alias_prefix_package_lock).rsplit(
            "@",
            1,
        )
    current_location = deepcopy(location)
    is_dev = value.get("dev") is True
    current_location.scope = Scope.DEV if is_dev else Scope.PROD
    if current_location.coordinates:
        current_location.coordinates.line = value.position.start.line
        current_location.dependency_type = (
            DependencyType.TRANSITIVE if is_transitive else DependencyType.DIRECT
        )
    try:
        return Package(
            name=name,
            version=version,
            locations=[current_location],
            language=Language.JAVASCRIPT,
            licenses=[],
            type=PackageType.NpmPkg,
            metadata=NpmPackageLockEntry(
                resolved=str(value.get("resolved")) if value.get("resolved") is not None else None,
                integrity=str(value.get("integrity"))
                if value.get("integrity") is not None
                else None,
                is_dev=is_dev,
            )
            if value.get("resolved") and "integrity" in value
            else None,
            p_url=package_url(name, version),
            is_dev=is_dev,
        )
    except ValidationError as ex:
        LOGGER.warning(
            "Malformed package. Required fields are missing or data types are incorrect.",
            extra={
                "extra": {
                    "exception": format_exception(str(ex)),
                    "location": current_location.path(),
                },
            },
        )
        return None


def new_package_lock_v2(
    location: Location,
    name: str,
    value: IndexedDict[str, ParsedValue],
    *,
    is_transitive: bool,
) -> Package | None:
    version: str = str(value.get("version", ""))

    if not name or not version:
        return None

    current_location = location
    is_dev = value.get("dev") is True
    current_location.scope = Scope.DEV if is_dev else Scope.PROD
    if current_location.coordinates:
        current_location.coordinates.line = value.position.start.line
        current_location.dependency_type = (
            DependencyType.TRANSITIVE if is_transitive else DependencyType.DIRECT
        )
    try:
        return Package(
            name=name,
            version=version,
            locations=[current_location],
            language=Language.JAVASCRIPT,
            licenses=[],
            type=PackageType.NpmPkg,
            metadata=NpmPackageLockEntry(
                resolved=str(value.get("resolved")) if value.get("resolved") is not None else None,
                integrity=str(value.get("integrity"))
                if value.get("integrity") is not None
                else None,
                is_dev=is_dev,
            ),
            p_url=package_url(name, version),
            is_dev=is_dev,
        )
    except ValidationError as ex:
        LOGGER.warning(
            "Malformed package. Required fields are missing or data types are incorrect.",
            extra={
                "extra": {
                    "exception": format_exception(str(ex)),
                    "location": current_location.path(),
                },
            },
        )
        return None


def package_url(name: str, version: str) -> str:
    namespace = ""
    fields = name.split("/", 2)
    if len(fields) > 1:
        namespace = fields[0]
        name = fields[1]

    if not name:
        return ""

    return PackageURL(  # type: ignore[misc]
        type="npm",
        namespace=namespace,
        name=name,
        version=version,
        qualifiers={},
        subpath="",
    ).to_string()

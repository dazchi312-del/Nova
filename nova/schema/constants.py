"""Schema versioning constants for Nova Imagination Engine records."""

from typing import Final, FrozenSet

# Current schema version. Integer-only per ratified versioning rule.
CURRENT_SCHEMA_VERSION: Final[int] = 1

# Legacy schema version (pre-Track B, no artifact_sha256 required).
LEGACY_SCHEMA_VERSION: Final[int] = 0

# Allowed values for the optional schema_status field.
# Absence of the field is equivalent to "native_v1".
SCHEMA_STATUS_NATIVE: Final[str] = "native_v1"
SCHEMA_STATUS_MIGRATED: Final[str] = "legacy_v0_migrated"

SCHEMA_STATUS_VALUES: Final[FrozenSet[str]] = frozenset({
    SCHEMA_STATUS_NATIVE,
    SCHEMA_STATUS_MIGRATED,
})

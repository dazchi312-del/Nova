"""
IterationRecord schema versioning constants.

SCOPE
-----
These constants describe versioning for the *top-level* IterationRecord
persistence format defined in nova/core/schemas.py. They are consumed by
nova/migration/migration_v0_to_v1.py to lift legacy corpus records.

NOT IN SCOPE
------------
EmbeddingMetadata (a sub-field of IterationRecord) has its own independent
versioning axis, also called `schema_version`, with values 1 and 2 derived
from the presence of `source_sha256`. That versioning is implemented inline
in nova/core/schemas.py::EmbeddingMetadata and verified by
nova/core/provenance.py. Do not conflate the two.

  IterationRecord.schema_version  ∈ {0 (legacy), 1 (current)}   ← THIS FILE
  EmbeddingMetadata.schema_version ∈ {1 (no hash), 2 (hashed)}  ← see core/

Both fields share the literal name `schema_version` on disk. When reading
a raw JSON record, disambiguate by structural position: top-level vs.
nested under `embedding`.
"""


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

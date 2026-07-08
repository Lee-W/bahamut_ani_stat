# Schema Maintenance

The project currently creates tables directly from SQLAlchemy models and does not use a migration
tool such as Alembic. Schema changes therefore need an explicit compatibility plan before they are
merged.

## Before Changing Models

Check whether the change is additive or breaking.

Additive changes include new nullable columns, new tables, and new relationships that can be left
empty for historical rows.

Breaking changes include renamed columns, removed columns, changed primary keys, changed foreign
keys, non-null columns without defaults, and type changes that existing SQLite values cannot
represent safely.

## Required Steps

For additive changes:

1. update `bahamut_ani_stat/db/models.py`
2. update the parser or CLI write path that fills the new fields
3. add focused tests for the write path
4. document how existing `anime.db` files behave before backfill

For breaking changes:

1. write a one-off migration or backfill script
2. test it on a copy of `anime.db`
3. record the before and after schema
4. update the data maintenance documentation with the recovery plan
5. run the full test, style, docs, and security checks

## Verification

At minimum, run:

```sh
uv run poe style
uv run poe test
uv run poe doc-build
uv run poe audit
uv run poe bandit
```

When a schema change touches generated plots, also regenerate plot assets from a copy of the data
branch database before updating `accumulate-data`.

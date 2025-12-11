# Pydantic Field Investigation Notes

## Environment
- Pydantic version: 2.12.3
- Python: 3.12
- Date: 2025-12-11

## Research Sources
- https://docs.pydantic.dev/latest/concepts/fields/
- https://docs.pydantic.dev/latest/api/fields/

## Key Findings

### Field Parameters Discovered

1. **Default Value Management**
   - `default` - static default value
   - `default_factory` - callable for dynamic defaults (can accept validated data dict)
   - `validate_default` - whether to validate default values (off by default)

2. **Aliasing (3 types!)**
   - `alias` - for both validation and serialization
   - `validation_alias` - validation only (supports AliasPath, AliasChoices)
   - `serialization_alias` - serialization only
   - `alias_priority` - controls precedence with alias generators

3. **Numeric Constraints**
   - `gt`, `ge`, `lt`, `le` - comparison operators
   - `multiple_of` - divisibility check
   - `max_digits`, `decimal_places` - decimal precision
   - `allow_inf_nan` - permit infinity/NaN

4. **String Constraints**
   - `pattern` - regex validation
   - `min_length`, `max_length` - length bounds
   - `coerce_numbers_to_str` - auto-convert numbers

5. **Behavioral Controls**
   - `strict` - disable type coercion
   - `frozen` - immutable after creation
   - `repr` - include in __repr__
   - `exclude` - exclude from serialization
   - `exclude_if` - conditional exclusion (NEW in 2.12!)
   - `discriminator` - tagged unions

6. **Metadata/Schema**
   - `title`, `description`, `examples`
   - `json_schema_extra` - additional schema properties
   - `deprecated` - mark as deprecated
   - `field_title_generator` - dynamic title generation

7. **Dataclass-Specific**
   - `init` - include in __init__
   - `init_var` - init-only field
   - `kw_only` - keyword-only argument

8. **Union Handling**
   - `union_mode` - 'smart' or 'left_to_right'
   - `fail_fast` - stop on first error

## Examples Created

### Positive Examples (field_examples.py - 16 sections)
1. Simple fields without Field (when not needed)
2. Mutable defaults with default_factory
3. Dynamic defaults (UUID, datetime) with default_factory
4. default_factory with validated data access (v2 feature)
5. Numeric constraints (gt, ge, lt, le, multiple_of)
6. String constraints (min_length, max_length, pattern)
7. Decimal precision constraints (max_digits, decimal_places)
8. All three alias types (alias, validation_alias, serialization_alias)
9. AliasPath for nested data access
10. AliasChoices for multiple input names
11. Strict mode preventing type coercion
12. Frozen fields for immutability
13. Discriminated unions with discriminator
14. validate_default for validating defaults
15. Serialization control (exclude, repr)
16. JSON schema metadata (description, examples, json_schema_extra)
17. Deprecated fields
18. Complete real-world model combining all features

### Negative Examples (error_examples.py - 11 sections)
1. Shared mutable default bug (Python classic)
2. Static evaluation bug (same UUID for all instances)
3. Missing constraints allowing invalid data through
4. Type coercion surprises without strict mode
5. Alias mismatch causing validation failure
6. Nested data access failure without AliasPath
7. Discriminated union confusion without discriminator
8. Decimal precision loss without constraints
9. Accidental field modification without frozen
10. Sensitive data exposure without exclude/repr
11. Pattern validation missing allowing malformed strings

## Key Insights

### When Field() is NOT needed
- Simple required fields: `name: str`
- Optional fields with None: `email: Optional[str] = None`
- Immutable defaults: `status: str = "active"`

### When Field() IS needed
- Mutable defaults (list, dict): `Field(default_factory=list)`
- Dynamic defaults (uuid, datetime): `Field(default_factory=uuid4)`
- Any validation constraint: `Field(ge=0, min_length=3, pattern=...)`
- Aliasing: `Field(alias="camelCase")`
- Strict typing: `Field(strict=True)`
- Immutability: `Field(frozen=True)`
- Serialization control: `Field(exclude=True, repr=False)`

### v2 Specific Features
- `default_factory` can receive validated data dict for computed defaults
- `exclude_if` for conditional exclusion (new in 2.12)
- Better protection against mutable defaults (raises error)
- `AliasPath` and `AliasChoices` for complex alias scenarios

## Test Results
All examples run successfully:
- `field_examples.py`: 16 sections, all pass
- `error_examples.py`: 11 sections, all demonstrate expected behavior

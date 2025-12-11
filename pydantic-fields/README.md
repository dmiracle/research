# Pydantic Field Best Practices Guide

A comprehensive guide to using `Field()` in Pydantic v2.12+, with examples of when it's necessary, when it's not, and what goes wrong without it.

## Quick Reference: When Do You Need Field()?

| Scenario | Field Required? | Example |
|----------|----------------|---------|
| Simple required field | No | `name: str` |
| Immutable default | No | `status: str = "active"` |
| Mutable default (list, dict) | **Yes** | `Field(default_factory=list)` |
| Dynamic default (uuid, datetime) | **Yes** | `Field(default_factory=uuid4)` |
| Numeric constraints | **Yes** | `Field(ge=0, le=100)` |
| String constraints | **Yes** | `Field(min_length=3, pattern=...)` |
| Input/output aliasing | **Yes** | `Field(alias="userName")` |
| Strict type checking | **Yes** | `Field(strict=True)` |
| Immutable field | **Yes** | `Field(frozen=True)` |
| Exclude from serialization | **Yes** | `Field(exclude=True)` |
| Hide from repr | **Yes** | `Field(repr=False)` |
| Discriminated unions | **Yes** | `Field(discriminator="type")` |
| JSON schema metadata | **Yes** | `Field(description=..., examples=...)` |

## Field Parameters Reference (Pydantic v2.12)

### Default Value Management
- `default` - Static default value
- `default_factory` - Callable that generates defaults (can receive validated data dict)
- `validate_default` - Whether to validate default values (default: False)

### Aliasing
- `alias` - For both validation and serialization
- `validation_alias` - Validation only (supports `AliasPath`, `AliasChoices`)
- `serialization_alias` - Serialization only
- `alias_priority` - Controls precedence with alias generators

### Type Validation
- `strict` - Disable type coercion for this field
- `union_mode` - Control union validation (`'smart'` or `'left_to_right'`)
- `fail_fast` - Stop validation on first error (iterables only)

### Numeric Constraints
- `gt`, `ge`, `lt`, `le` - Greater/less than comparisons
- `multiple_of` - Value must be divisible by this
- `max_digits`, `decimal_places` - Decimal precision
- `allow_inf_nan` - Permit infinity and NaN

### String Constraints
- `pattern` - Regex pattern validation
- `min_length`, `max_length` - Length bounds
- `coerce_numbers_to_str` - Auto-convert numbers to strings

### Field Behavior
- `frozen` - Prevent modification after creation
- `repr` - Include in `__repr__` output (default: True)
- `exclude` - Exclude from serialization
- `exclude_if` - Conditional exclusion (NEW in v2.12)
- `discriminator` - Tagged union discrimination

### Metadata
- `title`, `description`, `examples` - Documentation
- `json_schema_extra` - Additional JSON schema properties
- `deprecated` - Mark field as deprecated
- `field_title_generator` - Dynamic title generation

---

## Section 1: When You DON'T Need Field

For simple fields with type annotations and immutable defaults, `Field()` is unnecessary:

```python
class SimpleModel(BaseModel):
    # Required fields - just type annotation
    id: int
    name: str

    # Optional with None default
    email: Optional[str] = None

    # Immutable defaults are fine
    is_active: bool = True
    max_retries: int = 3
    status: str = "pending"
```

---

## Section 2: Mutable Defaults (CRITICAL)

**The Bug**: Python evaluates default arguments once at function/class definition time. Mutable defaults (lists, dicts) are shared across all instances.

**Pydantic's Protection**: In v2, using bare mutable defaults raises an error.

```python
# WRONG - Pydantic v2 will raise an error to protect you
class BadModel(BaseModel):
    tags: List[str] = []  # Shared across all instances!

# CORRECT - Each instance gets its own list
class GoodModel(BaseModel):
    tags: List[str] = Field(default_factory=list)
    metadata: Dict[str, str] = Field(default_factory=dict)
    scores: List[int] = Field(default_factory=lambda: [0, 0, 0])
```

**Result without `default_factory`**:
```
# Plain Python bug demonstration
a.items = ['from_a']
b.items = ['from_a']  # Same list! Bug!
```

---

## Section 3: Dynamic Defaults (UUID, datetime)

**The Bug**: Defaults like `uuid4()` or `datetime.now()` are evaluated once when the class is defined, not per-instance.

```python
# WRONG - Same UUID/timestamp for ALL instances
class BuggySession(BaseModel):
    id: UUID = uuid4()                    # Evaluated ONCE at class definition
    created_at: datetime = datetime.now() # Same problem

# CORRECT - New values per instance
class CorrectSession(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    created_at: datetime = Field(default_factory=datetime.now)
```

**Result**:
```
Buggy:   s1.id == s2.id == s3.id  # True - All same UUID!
Correct: c1.id == c2.id == c3.id  # False - Each unique
```

---

## Section 4: default_factory with Validated Data (v2 Feature)

In Pydantic v2, `default_factory` can receive a dict of already-validated fields:

```python
class ComputedDefaults(BaseModel):
    first_name: str
    last_name: str

    # Factory receives validated data as dict
    full_name: str = Field(
        default_factory=lambda data: f"{data['first_name']} {data['last_name']}"
    )
    username: str = Field(
        default_factory=lambda data: f"{data['first_name'].lower()}_{data['last_name'].lower()}"
    )
```

**Result**:
```python
user = ComputedDefaults(first_name="John", last_name="Doe")
# user.full_name = "John Doe"
# user.username = "john_doe"
```

---

## Section 5: Numeric Constraints

Without constraints, invalid values silently pass validation:

```python
# WITHOUT constraints - accepts invalid data
class UserNoConstraints(BaseModel):
    age: int       # Accepts -5, 999, etc.
    discount: float # Accepts 1.5 (150%!)

# WITH constraints - validates business rules
class UserWithConstraints(BaseModel):
    age: int = Field(ge=0, le=150)
    discount: float = Field(ge=0, le=1)  # 0-100%
    rating: float = Field(ge=1, le=5, multiple_of=0.5)
```

**Available constraints**: `gt`, `ge`, `lt`, `le`, `multiple_of`

---

## Section 6: String Constraints

```python
class UserWithConstraints(BaseModel):
    username: str = Field(
        min_length=3,
        max_length=20,
        pattern=r'^[a-z0-9_]+$'
    )
    email: str = Field(pattern=r'^[\w.-]+@[\w.-]+\.\w+$')
    phone: str = Field(pattern=r'^\+?[1-9]\d{9,14}$')
```

**Without constraints**:
```
username='X' accepted           # Too short
email='not-an-email' accepted   # Invalid format
```

---

## Section 7: Decimal Precision

Critical for financial applications:

```python
class Money(BaseModel):
    amount: Decimal = Field(
        max_digits=10,
        decimal_places=2,
        ge=0
    )
```

**Without constraints**:
```
Decimal("99999999999.99") accepted  # Too many digits
Decimal("123.456") accepted         # Too many decimal places
Decimal("-50.00") accepted          # Negative money
```

---

## Section 8: Aliasing

Three types of aliases handle different input/output naming:

```python
class User(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    # alias: for both validation and serialization
    user_id: int = Field(alias="userId")

    # validation_alias: only for input parsing
    user_name: str = Field(validation_alias="userName")

    # serialization_alias: only for output
    email_address: str = Field(serialization_alias="emailAddress")

    # AliasPath: access nested data
    street: str = Field(validation_alias=AliasPath("address", "street"))

    # AliasChoices: accept multiple input names
    phone: str = Field(validation_alias=AliasChoices("phone", "telephone", "mobile"))
```

**Without aliases**:
```
API sends: {"userId": 123, "userName": "john"}
Error: user_id field required, user_name field required
```

---

## Section 9: Strict Mode

By default, Pydantic coerces types. Use `strict=True` to prevent this:

```python
class StrictModel(BaseModel):
    count: int = Field(strict=True)
    price: float = Field(strict=True)
    is_active: bool = Field(strict=True)

# Without strict:
# "42" -> 42 (str to int coercion)
# 1 -> True (int to bool coercion)
# "yes" -> True (truthy string to bool!)

# With strict:
# "42" -> ValidationError (must be int)
# 1 -> ValidationError (must be bool)
```

---

## Section 10: Frozen Fields (Immutability)

```python
class ImmutableRecord(BaseModel):
    id: int = Field(frozen=True)
    created_at: datetime = Field(default_factory=datetime.now, frozen=True)
    name: str  # This can still be modified

# Or freeze entire model:
class FullyFrozen(BaseModel):
    model_config = ConfigDict(frozen=True)
    # All fields are now frozen
```

**Without frozen**:
```python
record.id = 999  # Silently succeeds - potential data integrity bug
```

---

## Section 11: Discriminated Unions

For unions with a type tag, use `discriminator` for clearer errors and better performance:

```python
class Dog(BaseModel):
    type: Literal["dog"] = "dog"
    barks: int

class Cat(BaseModel):
    type: Literal["cat"] = "cat"
    meows: int

class PetOwner(BaseModel):
    # With discriminator - uses 'type' to pick correct model
    pet: Dog | Cat = Field(discriminator="type")
```

**Without discriminator**:
```
Error: 6 validation errors (tries each union member)
```

**With discriminator**:
```
Error: Input tag 'dragon' does not match expected tags: 'dog', 'cat'
```

---

## Section 12: Serialization Control

```python
class User(BaseModel):
    username: str
    password: str = Field(repr=False, exclude=True)  # Never show, never serialize
    api_key: str = Field(repr=False)                  # Hide from repr only
    internal_score: float = Field(default=0.0, exclude=True)
```

**Without protection**:
```
repr: User(username='admin', password='secret123', api_key='sk-abc123')
dict: {'username': 'admin', 'password': 'secret123', 'api_key': 'sk-abc123'}
# DANGER: Sensitive data in logs!
```

**With protection**:
```
repr: User(username='admin')
dict: {'username': 'admin'}
# Safe: Sensitive fields hidden
```

---

## Section 13: JSON Schema Metadata

For OpenAPI/documentation:

```python
class Product(BaseModel):
    id: int = Field(description="Unique product identifier")
    name: str = Field(
        description="Human-readable product name",
        examples=["Widget", "Gadget Pro"],
        min_length=1,
        max_length=100
    )
    sku: str = Field(
        json_schema_extra={
            "pattern": "^[A-Z]{3}-[0-9]{4}$",
            "examples": ["ABC-1234"]
        }
    )
```

---

## Section 14: Deprecated Fields

```python
class Model(BaseModel):
    new_field: str
    old_field: Optional[str] = Field(
        default=None,
        deprecated="Use 'new_field' instead. Will be removed in v3.0"
    )
```

Generates deprecation warnings and marks field as deprecated in JSON schema.

---

## Complete Example

```python
class CompleteUserModel(BaseModel):
    model_config = ConfigDict(populate_by_name=True, str_strip_whitespace=True)

    # Frozen UUID with factory
    id: UUID = Field(default_factory=uuid4, frozen=True)

    # Validation + multiple aliases
    username: str = Field(
        min_length=3,
        max_length=30,
        pattern=r'^[a-zA-Z][a-zA-Z0-9_]*$',
        validation_alias=AliasChoices("username", "user_name", "login")
    )

    # Email with pattern and serialization alias
    email: str = Field(
        pattern=r'^[\w.-]+@[\w.-]+\.\w+$',
        serialization_alias="emailAddress"
    )

    # Numeric constraint
    age: int = Field(ge=0, le=150)

    # Sensitive - hidden from output
    password_hash: str = Field(repr=False, exclude=True)

    # Mutable with factory
    roles: List[str] = Field(default_factory=lambda: ["user"])

    # Nested data extraction
    primary_address: Address = Field(validation_alias=AliasPath("addresses", 0))

    # Frozen timestamps
    created_at: datetime = Field(default_factory=datetime.now, frozen=True)
```

---

## Files in This Project

- `field_examples.py` - Comprehensive positive examples (16 sections)
- `error_examples.py` - Negative examples showing what goes wrong (11 sections)
- `notes.md` - Investigation notes and findings
- `README.md` - This report

## Running the Examples

```bash
python3 field_examples.py   # All positive examples
python3 error_examples.py   # All error demonstrations
```

## Environment

- Pydantic version: 2.12.3
- Python: 3.12

## Sources

- [Pydantic Fields Documentation](https://docs.pydantic.dev/latest/concepts/fields/)
- [Pydantic Fields API Reference](https://docs.pydantic.dev/latest/api/fields/)

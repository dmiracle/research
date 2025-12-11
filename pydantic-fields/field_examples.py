"""
field_examples.py

Comprehensive examples demonstrating Pydantic Field usage in v2.12+.
Covers when Field is necessary, when it's not, and what goes wrong without it.

Run with: python field_examples.py
"""

from __future__ import annotations

import re
import warnings
from datetime import datetime, date
from decimal import Decimal
from typing import Annotated, List, Dict, Optional, Literal, Union
from uuid import UUID, uuid4

from pydantic import (
    BaseModel,
    Field,
    ValidationError,
    ConfigDict,
    AliasPath,
    AliasChoices,
    field_validator,
)


# ============================================================================
# SECTION 1: When you DON'T need Field
# ============================================================================

class SimpleModel(BaseModel):
    """Basic fields with type annotations don't require Field()."""

    # Required fields - just type annotation
    id: int
    name: str

    # Optional with None default
    email: Optional[str] = None

    # Immutable defaults are fine without Field
    is_active: bool = True
    max_retries: int = 3
    status: str = "pending"


def demo_simple_no_field():
    """Shows that simple fields work fine without Field()."""
    print("\n" + "="*70)
    print("SECTION 1: When you DON'T need Field")
    print("="*70)

    user = SimpleModel(id=1, name="Alice")
    print(f"SimpleModel: {user}")
    print(f"  Defaults applied: is_active={user.is_active}, status={user.status}")
    print("  -> No Field() needed for basic types with immutable defaults\n")


# ============================================================================
# SECTION 2: Mutable Defaults - Field(default_factory=...) is REQUIRED
# ============================================================================

class BadMutableDefault(BaseModel):
    """
    DANGER: Using a mutable default directly.
    Pydantic v2 will raise an error to protect you.
    """
    model_config = ConfigDict(validate_default=True)

    # This will raise PydanticUserError in v2!
    # tags: List[str] = []  # WRONG - shared mutable default


class GoodMutableDefault(BaseModel):
    """Correct: using default_factory for mutable defaults."""

    tags: List[str] = Field(default_factory=list)
    metadata: Dict[str, str] = Field(default_factory=dict)
    scores: List[int] = Field(default_factory=lambda: [0, 0, 0])


def demo_mutable_defaults():
    """Shows why default_factory is essential for mutable types."""
    print("\n" + "="*70)
    print("SECTION 2: Mutable Defaults - default_factory is REQUIRED")
    print("="*70)

    # Correct behavior with default_factory
    a = GoodMutableDefault()
    b = GoodMutableDefault()

    a.tags.append("modified-a")
    a.metadata["key"] = "value-a"

    print(f"Instance a: tags={a.tags}, metadata={a.metadata}")
    print(f"Instance b: tags={b.tags}, metadata={b.metadata}")
    print("  -> Each instance has independent mutable objects")

    # Show what would happen without Field (conceptually)
    print("\n  WITHOUT default_factory (if allowed):")
    print("    a.tags.append('x') would modify b.tags too!")
    print("    This is the classic Python mutable default bug.")
    print("    Pydantic v2 raises an error to prevent this.\n")


# ============================================================================
# SECTION 3: default_factory for Dynamic Values
# ============================================================================

class Session(BaseModel):
    """UUID and timestamp must be generated per-instance."""

    # WRONG: id: UUID = uuid4()  # Same UUID for all instances!
    # RIGHT:
    id: UUID = Field(default_factory=uuid4)
    created_at: datetime = Field(default_factory=datetime.now)

    # Static default is fine for immutable
    status: str = "active"


class WrongSession(BaseModel):
    """Demonstrates the bug when NOT using default_factory."""

    # BUG: evaluated once at class definition time
    id: UUID = uuid4()
    created_at: datetime = datetime.now()


def demo_dynamic_defaults():
    """Shows why default_factory is needed for dynamic values."""
    print("\n" + "="*70)
    print("SECTION 3: default_factory for Dynamic Values")
    print("="*70)

    print("CORRECT - using default_factory:")
    s1 = Session()
    s2 = Session()
    print(f"  s1.id = {s1.id}")
    print(f"  s2.id = {s2.id}")
    print(f"  Different UUIDs: {s1.id != s2.id}")

    print("\nWRONG - static default (evaluated at class definition):")
    w1 = WrongSession()
    w2 = WrongSession()
    print(f"  w1.id = {w1.id}")
    print(f"  w2.id = {w2.id}")
    print(f"  Same UUID! Bug: {w1.id == w2.id}\n")


# ============================================================================
# SECTION 4: default_factory with Validated Data Access
# ============================================================================

class ComputedDefaults(BaseModel):
    """
    NEW in Pydantic v2: default_factory can receive validated data.
    This allows computed defaults based on other fields.
    """

    first_name: str
    last_name: str

    # default_factory receives dict of already-validated fields
    full_name: str = Field(
        default_factory=lambda data: f"{data['first_name']} {data['last_name']}"
    )

    username: str = Field(
        default_factory=lambda data: f"{data['first_name'].lower()}_{data['last_name'].lower()}"
    )


def demo_computed_defaults():
    """Shows default_factory receiving validated data."""
    print("\n" + "="*70)
    print("SECTION 4: default_factory with Validated Data Access")
    print("="*70)

    user = ComputedDefaults(first_name="John", last_name="Doe")
    print(f"  first_name: {user.first_name}")
    print(f"  last_name: {user.last_name}")
    print(f"  full_name (computed): {user.full_name}")
    print(f"  username (computed): {user.username}")
    print("  -> default_factory received validated data dict\n")


# ============================================================================
# SECTION 5: Numeric Constraints
# ============================================================================

class WithNumericConstraints(BaseModel):
    """Field() is required to add numeric validation."""

    age: int = Field(ge=0, le=150)
    price: float = Field(gt=0)
    quantity: int = Field(ge=1, le=1000)
    discount: float = Field(ge=0, le=1)  # 0-100%
    rating: float = Field(ge=1, le=5, multiple_of=0.5)


class WithoutNumericConstraints(BaseModel):
    """Same fields but no validation - accepts invalid data."""

    age: int
    price: float
    quantity: int
    discount: float
    rating: float


def demo_numeric_constraints():
    """Shows numeric constraint validation."""
    print("\n" + "="*70)
    print("SECTION 5: Numeric Constraints")
    print("="*70)

    # Valid data
    valid = WithNumericConstraints(
        age=25, price=9.99, quantity=5, discount=0.1, rating=4.5
    )
    print(f"Valid data accepted: {valid}")

    # Invalid data with constraints
    invalid_cases = [
        {"age": -5, "price": 10, "quantity": 1, "discount": 0, "rating": 3},
        {"age": 25, "price": 0, "quantity": 1, "discount": 0, "rating": 3},
        {"age": 25, "price": 10, "quantity": 1, "discount": 1.5, "rating": 3},
        {"age": 25, "price": 10, "quantity": 1, "discount": 0, "rating": 3.3},  # not multiple of 0.5
    ]

    print("\nWith Field constraints (rejects invalid):")
    for i, data in enumerate(invalid_cases):
        try:
            WithNumericConstraints(**data)
        except ValidationError as e:
            error = e.errors()[0]
            print(f"  Case {i+1}: {error['loc'][0]} - {error['msg']}")

    print("\nWithout Field constraints (accepts all):")
    for data in invalid_cases:
        obj = WithoutNumericConstraints(**data)
        print(f"  Accepted invalid: age={obj.age}, discount={obj.discount}, rating={obj.rating}")
    print()


# ============================================================================
# SECTION 6: String Constraints
# ============================================================================

class WithStringConstraints(BaseModel):
    """Field() needed for string validation."""

    username: str = Field(min_length=3, max_length=20, pattern=r'^[a-z0-9_]+$')
    email: str = Field(pattern=r'^[\w.-]+@[\w.-]+\.\w+$')
    phone: str = Field(pattern=r'^\+?[1-9]\d{9,14}$')
    bio: str = Field(default="", max_length=500)


class WithoutStringConstraints(BaseModel):
    """Same fields without validation."""

    username: str
    email: str
    phone: str
    bio: str = ""


def demo_string_constraints():
    """Shows string pattern and length validation."""
    print("\n" + "="*70)
    print("SECTION 6: String Constraints")
    print("="*70)

    # Valid
    valid = WithStringConstraints(
        username="john_doe",
        email="john@example.com",
        phone="+1234567890"
    )
    print(f"Valid: username={valid.username}, email={valid.email}")

    # Invalid cases
    invalid_cases = [
        {"username": "ab", "email": "test@test.com", "phone": "+1234567890"},  # too short
        {"username": "JohnDoe", "email": "test@test.com", "phone": "+1234567890"},  # uppercase
        {"username": "johndoe", "email": "not-an-email", "phone": "+1234567890"},  # bad email
        {"username": "johndoe", "email": "test@test.com", "phone": "123"},  # bad phone
    ]

    print("\nWith Field constraints (rejects invalid):")
    for i, data in enumerate(invalid_cases):
        try:
            WithStringConstraints(**data)
        except ValidationError as e:
            error = e.errors()[0]
            print(f"  Case {i+1}: {error['loc'][0]} - {error['type']}")

    print("\nWithout Field constraints (accepts all):")
    for data in invalid_cases:
        obj = WithoutStringConstraints(**data)
        print(f"  Accepted: username='{obj.username}', email='{obj.email}'")
    print()


# ============================================================================
# SECTION 7: Decimal Precision Constraints
# ============================================================================

class MoneyField(BaseModel):
    """Financial applications need precise decimal handling."""

    amount: Decimal = Field(max_digits=10, decimal_places=2, ge=0)
    exchange_rate: Decimal = Field(max_digits=12, decimal_places=6)


class MoneyFieldNaive(BaseModel):
    """Without constraints - loses precision guarantees."""

    amount: Decimal
    exchange_rate: Decimal


def demo_decimal_constraints():
    """Shows decimal precision validation."""
    print("\n" + "="*70)
    print("SECTION 7: Decimal Precision Constraints")
    print("="*70)

    # Valid
    valid = MoneyField(
        amount=Decimal("12345.67"),
        exchange_rate=Decimal("1.234567")
    )
    print(f"Valid: amount={valid.amount}, rate={valid.exchange_rate}")

    # Invalid - too many digits
    try:
        MoneyField(amount=Decimal("123456789.99"), exchange_rate=Decimal("1.0"))
    except ValidationError as e:
        print(f"Too many digits rejected: {e.errors()[0]['msg']}")

    # Invalid - too many decimal places
    try:
        MoneyField(amount=Decimal("123.456"), exchange_rate=Decimal("1.0"))
    except ValidationError as e:
        print(f"Too many decimals rejected: {e.errors()[0]['msg']}")

    # Without constraints - accepts anything
    naive = MoneyFieldNaive(
        amount=Decimal("9999999999999.999999999"),
        exchange_rate=Decimal("0.00000000001")
    )
    print(f"Naive accepts: amount={naive.amount}")
    print()


# ============================================================================
# SECTION 8: Aliases - validation_alias vs serialization_alias
# ============================================================================

class UserWithAliases(BaseModel):
    """Demonstrates all three alias types."""

    model_config = ConfigDict(populate_by_name=True)

    # alias: used for both validation and serialization
    user_id: int = Field(alias="userId")

    # validation_alias: only for input parsing
    user_name: str = Field(validation_alias="userName")

    # serialization_alias: only for output
    email_address: str = Field(serialization_alias="emailAddress")

    # AliasPath: for nested data access
    street: str = Field(validation_alias=AliasPath("address", "street"))

    # AliasChoices: accept multiple input names
    phone: str = Field(validation_alias=AliasChoices("phone", "telephone", "mobile"))


class UserWithoutAliases(BaseModel):
    """Same fields without aliases - fails on camelCase input."""

    user_id: int
    user_name: str
    email_address: str


def demo_aliases():
    """Shows how aliases handle different input/output formats."""
    print("\n" + "="*70)
    print("SECTION 8: Aliases - validation_alias vs serialization_alias")
    print("="*70)

    # Input data in various formats
    input_data = {
        "userId": 123,
        "userName": "johndoe",
        "email_address": "john@example.com",
        "address": {"street": "123 Main St"},
        "mobile": "+1234567890"
    }

    user = UserWithAliases(**input_data)
    print(f"Parsed user: {user}")
    print(f"  Attribute access: user.user_id={user.user_id}, user.street={user.street}")

    print(f"\nSerialization (by_alias=True):")
    print(f"  {user.model_dump(by_alias=True)}")
    print(f"Serialization (by_alias=False):")
    print(f"  {user.model_dump(by_alias=False)}")

    # Without aliases - fails
    print("\nWithout aliases (using same input data):")
    try:
        UserWithoutAliases(**input_data)
    except ValidationError as e:
        for error in e.errors():
            print(f"  Missing: {error['loc'][0]} - {error['msg']}")
    print()


# ============================================================================
# SECTION 9: Strict Mode
# ============================================================================

class StrictModel(BaseModel):
    """strict=True prevents type coercion."""

    count: int = Field(strict=True)
    price: float = Field(strict=True)
    active: bool = Field(strict=True)
    name: str = Field(strict=True)


class LooseModel(BaseModel):
    """Default behavior: coercion allowed."""

    count: int
    price: float
    active: bool
    name: str


def demo_strict_mode():
    """Shows how strict mode prevents unwanted coercion."""
    print("\n" + "="*70)
    print("SECTION 9: Strict Mode")
    print("="*70)

    # Data that would be coerced (note: int->str is NOT coerced by default)
    coercible_data = {
        "count": "42",       # str -> int (coerced by default)
        "price": "19.99",    # str -> float (coerced by default)
        "active": 1,         # int -> bool (coerced by default)
        "name": "Alice"      # correct type
    }

    print("Input data (some wrong types):", coercible_data)

    # Loose model accepts and coerces
    loose = LooseModel(**coercible_data)
    print(f"\nLoose model (coercion ON):")
    print(f"  count: {loose.count} (type: {type(loose.count).__name__}) - str '42' -> int 42")
    print(f"  price: {loose.price} (type: {type(loose.price).__name__}) - str '19.99' -> float")
    print(f"  active: {loose.active} (type: {type(loose.active).__name__}) - int 1 -> bool True")
    print(f"  name: '{loose.name}' (type: {type(loose.name).__name__})")

    # Strict model rejects
    print(f"\nStrict model (coercion OFF):")
    try:
        StrictModel(**coercible_data)
    except ValidationError as e:
        for error in e.errors():
            print(f"  {error['loc'][0]}: {error['msg']}")
    print()


# ============================================================================
# SECTION 10: Frozen Fields (Immutability)
# ============================================================================

class WithFrozenFields(BaseModel):
    """frozen=True makes specific fields immutable."""

    id: int = Field(frozen=True)  # Cannot change after creation
    name: str                      # Can change
    created_at: datetime = Field(default_factory=datetime.now, frozen=True)


class FullyFrozenModel(BaseModel):
    """Alternative: freeze entire model via config."""

    model_config = ConfigDict(frozen=True)

    id: int
    name: str


def demo_frozen_fields():
    """Shows immutability with frozen fields."""
    print("\n" + "="*70)
    print("SECTION 10: Frozen Fields (Immutability)")
    print("="*70)

    obj = WithFrozenFields(id=1, name="Original")
    print(f"Created: {obj}")

    # Can modify non-frozen field
    obj.name = "Modified"
    print(f"After name change: {obj}")

    # Cannot modify frozen field
    print("\nTrying to modify frozen 'id' field:")
    try:
        obj.id = 999
    except ValidationError as e:
        print(f"  Error: {e.errors()[0]['msg']}")

    # Fully frozen model
    frozen = FullyFrozenModel(id=1, name="Test")
    print(f"\nFully frozen model: {frozen}")
    try:
        frozen.name = "Changed"
    except ValidationError as e:
        print(f"  Cannot modify any field: {e.errors()[0]['msg']}")
    print()


# ============================================================================
# SECTION 11: Discriminated Unions
# ============================================================================

class Cat(BaseModel):
    pet_type: Literal["cat"] = "cat"
    meows: int


class Dog(BaseModel):
    pet_type: Literal["dog"] = "dog"
    barks: int


class Bird(BaseModel):
    pet_type: Literal["bird"] = "bird"
    chirps: int


class PetOwnerWithDiscriminator(BaseModel):
    """discriminator tells Pydantic which union member to use."""

    name: str
    pet: Cat | Dog | Bird = Field(discriminator="pet_type")


class PetOwnerWithoutDiscriminator(BaseModel):
    """Without discriminator - must try each type."""

    name: str
    pet: Cat | Dog | Bird  # Works but less efficient and clear


def demo_discriminated_unions():
    """Shows how discriminator improves union handling."""
    print("\n" + "="*70)
    print("SECTION 11: Discriminated Unions")
    print("="*70)

    # Different pet types
    cat_owner = PetOwnerWithDiscriminator(
        name="Alice",
        pet={"pet_type": "cat", "meows": 5}
    )
    dog_owner = PetOwnerWithDiscriminator(
        name="Bob",
        pet={"pet_type": "dog", "barks": 10}
    )

    print(f"Cat owner: {cat_owner}")
    print(f"  pet type: {type(cat_owner.pet).__name__}")
    print(f"Dog owner: {dog_owner}")
    print(f"  pet type: {type(dog_owner.pet).__name__}")

    # Invalid discriminator value
    print("\nInvalid pet_type:")
    try:
        PetOwnerWithDiscriminator(
            name="Eve",
            pet={"pet_type": "fish", "swims": 100}
        )
    except ValidationError as e:
        print(f"  Error: {e.errors()[0]['msg']}")
    print()


# ============================================================================
# SECTION 12: validate_default
# ============================================================================

class WithValidateDefault(BaseModel):
    """validate_default=True catches invalid defaults."""

    # This will fail at model creation time!
    # age: int = Field(default="not a number", validate_default=True)

    # Example with valid default but constraint violation would be caught
    score: int = Field(default=50, ge=0, le=100, validate_default=True)


class DynamicValidateDefault(BaseModel):
    """Shows validate_default catching factory issues."""

    model_config = ConfigDict(validate_default=True)

    # This default would be validated
    items: List[int] = Field(default_factory=list)


def demo_validate_default():
    """Shows how validate_default catches invalid defaults."""
    print("\n" + "="*70)
    print("SECTION 12: validate_default")
    print("="*70)

    # Define a bad model dynamically to show the error
    print("Creating model with invalid default and validate_default=True:")

    try:
        # This creates the model class with validation on defaults
        class BadDefault(BaseModel):
            age: int = Field(default="not_a_number", validate_default=True)
    except Exception as e:
        print(f"  Error at class definition: {type(e).__name__}")

    # Working example
    good = WithValidateDefault()
    print(f"\nGood model with valid default: score={good.score}")

    # Without validate_default, bad defaults slip through
    print("\nWithout validate_default, invalid defaults are NOT caught:")

    class SneakyBadDefault(BaseModel):
        # validate_default=False (default), so "abc" isn't validated
        # Only matters if the default is actually used
        value: int = Field(default=999)  # Would work with string if not validated

    obj = SneakyBadDefault()
    print(f"  Default used: value={obj.value}")
    print()


# ============================================================================
# SECTION 13: Serialization Control - exclude and repr
# ============================================================================

class UserWithExclusion(BaseModel):
    """exclude and repr control what gets shown/serialized."""

    id: int
    username: str
    password: str = Field(repr=False, exclude=True)  # Never show, never serialize
    api_key: str = Field(repr=False)  # Don't show in repr, but serialize

    internal_score: float = Field(default=0.0, exclude=True)


def demo_serialization_control():
    """Shows exclude and repr behavior."""
    print("\n" + "="*70)
    print("SECTION 13: Serialization Control - exclude and repr")
    print("="*70)

    user = UserWithExclusion(
        id=1,
        username="admin",
        password="secret123",
        api_key="key-abc-123"
    )

    print(f"repr(user): {repr(user)}")
    print("  -> password and api_key hidden from repr")

    print(f"\nmodel_dump(): {user.model_dump()}")
    print("  -> password and internal_score excluded")

    print(f"\nmodel_dump(exclude_unset=True): {user.model_dump(exclude_unset=True)}")

    # Direct attribute access still works
    print(f"\nDirect access: user.password = '{user.password}'")
    print()


# ============================================================================
# SECTION 14: JSON Schema Metadata
# ============================================================================

class ProductWithMetadata(BaseModel):
    """Field metadata enhances generated JSON schema."""

    id: int = Field(description="Unique product identifier")
    name: str = Field(
        description="Human-readable product name",
        examples=["Widget", "Gadget Pro"],
        min_length=1,
        max_length=100
    )
    price: Decimal = Field(
        description="Price in USD",
        examples=[9.99, 19.99],
        ge=0,
        decimal_places=2
    )
    tags: List[str] = Field(
        default_factory=list,
        description="Searchable tags",
        examples=[["electronics", "sale"]]
    )

    # Custom JSON schema additions
    sku: str = Field(
        json_schema_extra={
            "pattern": "^[A-Z]{3}-[0-9]{4}$",
            "examples": ["ABC-1234", "XYZ-5678"]
        }
    )


def demo_json_schema():
    """Shows JSON schema generation with Field metadata."""
    print("\n" + "="*70)
    print("SECTION 14: JSON Schema Metadata")
    print("="*70)

    import json
    schema = ProductWithMetadata.model_json_schema()

    print("Generated JSON Schema:")
    print(json.dumps(schema, indent=2))
    print()


# ============================================================================
# SECTION 15: Deprecated Fields
# ============================================================================

class ModelWithDeprecation(BaseModel):
    """deprecated marks fields for future removal."""

    id: int
    new_name: str

    # Deprecated field - still works but warns
    old_name: Optional[str] = Field(
        default=None,
        deprecated="Use 'new_name' instead. Will be removed in v3.0"
    )


def demo_deprecated():
    """Shows deprecated field behavior."""
    print("\n" + "="*70)
    print("SECTION 15: Deprecated Fields")
    print("="*70)

    # Using deprecated field triggers warning
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")

        obj = ModelWithDeprecation(id=1, new_name="current", old_name="legacy")
        print(f"Created: {obj}")

        if w:
            print(f"Deprecation warning: {w[-1].message}")

    # Check schema marks it as deprecated
    schema = ModelWithDeprecation.model_json_schema()
    old_name_schema = schema.get("properties", {}).get("old_name", {})
    print(f"\nIn JSON schema, deprecated={old_name_schema.get('deprecated')}")
    print()


# ============================================================================
# SECTION 16: Complex Example - All Together
# ============================================================================

class Address(BaseModel):
    street: str = Field(min_length=1)
    city: str = Field(min_length=1)
    zip_code: str = Field(pattern=r'^\d{5}(-\d{4})?$')


class CompleteUserModel(BaseModel):
    """Comprehensive example using many Field features."""

    model_config = ConfigDict(
        populate_by_name=True,
        str_strip_whitespace=True
    )

    # Required with factory
    id: UUID = Field(default_factory=uuid4, frozen=True)

    # Validation + alias
    username: str = Field(
        min_length=3,
        max_length=30,
        pattern=r'^[a-zA-Z][a-zA-Z0-9_]*$',
        validation_alias=AliasChoices("username", "user_name", "login")
    )

    # Email with pattern
    email: str = Field(
        pattern=r'^[\w.-]+@[\w.-]+\.\w+$',
        serialization_alias="emailAddress"
    )

    # Numeric with constraints
    age: int = Field(ge=0, le=150)

    # Sensitive - exclude from serialization
    password_hash: str = Field(repr=False, exclude=True)

    # Mutable with factory
    roles: List[str] = Field(default_factory=lambda: ["user"])

    # Nested with path alias
    primary_address: Address = Field(validation_alias=AliasPath("addresses", 0))

    # Timestamps
    created_at: datetime = Field(default_factory=datetime.now, frozen=True)
    updated_at: datetime = Field(default_factory=datetime.now)

    # Metadata for docs
    bio: str = Field(
        default="",
        max_length=1000,
        description="User biography",
        examples=["Software developer from NYC"]
    )


def demo_complete_example():
    """Shows a complete real-world model."""
    print("\n" + "="*70)
    print("SECTION 16: Complex Example - All Together")
    print("="*70)

    input_data = {
        "user_name": "johndoe",  # Using alias
        "email": "john@example.com",
        "age": 30,
        "password_hash": "hashed_secret",
        "addresses": [
            {"street": "123 Main St", "city": "Boston", "zip_code": "02101"}
        ]
    }

    user = CompleteUserModel(**input_data)
    print(f"Created user: {repr(user)}")
    print(f"\nSerialized (by_alias=True):")
    print(f"  {user.model_dump(by_alias=True)}")

    # Try to modify frozen field
    print("\nTrying to modify frozen 'id':")
    try:
        user.id = uuid4()
    except ValidationError as e:
        print(f"  Blocked: {e.errors()[0]['msg']}")
    print()


# ============================================================================
# MAIN
# ============================================================================

def main():
    print("=" * 70)
    print("PYDANTIC FIELD EXAMPLES - Comprehensive Guide")
    print("Pydantic version: 2.12+")
    print("=" * 70)

    demo_simple_no_field()
    demo_mutable_defaults()
    demo_dynamic_defaults()
    demo_computed_defaults()
    demo_numeric_constraints()
    demo_string_constraints()
    demo_decimal_constraints()
    demo_aliases()
    demo_strict_mode()
    demo_frozen_fields()
    demo_discriminated_unions()
    demo_validate_default()
    demo_serialization_control()
    demo_json_schema()
    demo_deprecated()
    demo_complete_example()

    print("=" * 70)
    print("ALL EXAMPLES COMPLETED")
    print("=" * 70)


if __name__ == "__main__":
    main()

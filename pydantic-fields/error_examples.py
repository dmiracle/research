"""
error_examples.py

Focused examples showing what goes WRONG when you don't use Field properly.
Each section contrasts correct usage with incorrect usage that leads to bugs or errors.

Run with: python3 error_examples.py
"""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import List, Dict, Optional, Literal, Union
from uuid import UUID, uuid4

from pydantic import (
    BaseModel,
    Field,
    ValidationError,
    ConfigDict,
    AliasPath,
    AliasChoices,
)


# ============================================================================
# ERROR 1: The Shared Mutable Default Bug
# ============================================================================

def demo_shared_mutable_bug():
    """
    Classic Python bug: mutable defaults are shared across instances.
    In Pydantic v2, this raises an error to protect you.
    """
    print("\n" + "="*70)
    print("ERROR 1: The Shared Mutable Default Bug")
    print("="*70)

    # This demonstrates the bug conceptually using plain Python
    class PlainPythonBug:
        def __init__(self, items=None):
            self.items = items if items is not None else []

    # Now without the protection (simulating the bug)
    class PlainPythonBugActual:
        def __init__(self, items=[]):  # noqa: B006 - intentional bug demo
            self.items = items

    a = PlainPythonBugActual()
    b = PlainPythonBugActual()

    a.items.append("from_a")
    print("Plain Python bug demonstration:")
    print(f"  a.items = {a.items}")
    print(f"  b.items = {b.items}")
    print(f"  Same object? {a.items is b.items}")
    print("  -> BUG: Both instances share the same list!")

    # In Pydantic v2, trying to use mutable defaults raises an error
    print("\nPydantic v2 protection:")
    try:
        class BadModel(BaseModel):
            items: List[str] = []  # This will raise!
    except Exception as e:
        print(f"  Pydantic raises: {type(e).__name__}")
        print("  -> Pydantic protects you from this bug!")

    # The correct way
    class GoodModel(BaseModel):
        items: List[str] = Field(default_factory=list)

    g1 = GoodModel()
    g2 = GoodModel()
    g1.items.append("from_g1")
    print(f"\nCorrect usage with default_factory:")
    print(f"  g1.items = {g1.items}")
    print(f"  g2.items = {g2.items}")
    print(f"  Same object? {g1.items is g2.items}")
    print()


# ============================================================================
# ERROR 2: Static Evaluation Bug (UUID, datetime, etc.)
# ============================================================================

def demo_static_evaluation_bug():
    """
    Defaults like uuid4() or datetime.now() are evaluated ONCE at class
    definition time, not per-instance.
    """
    print("\n" + "="*70)
    print("ERROR 2: Static Evaluation Bug (UUID, datetime)")
    print("="*70)

    class BuggySession(BaseModel):
        # BUG: These are evaluated when the CLASS is defined, not instances
        id: UUID = uuid4()
        created_at: datetime = datetime.now()

    # Create instances
    s1 = BuggySession()
    s2 = BuggySession()
    s3 = BuggySession()

    print("Buggy implementation (static defaults):")
    print(f"  s1.id = {s1.id}")
    print(f"  s2.id = {s2.id}")
    print(f"  s3.id = {s3.id}")
    print(f"  All same? {s1.id == s2.id == s3.id}")
    print("  -> BUG: All instances have the SAME UUID!")

    class CorrectSession(BaseModel):
        id: UUID = Field(default_factory=uuid4)
        created_at: datetime = Field(default_factory=datetime.now)

    c1 = CorrectSession()
    c2 = CorrectSession()
    c3 = CorrectSession()

    print(f"\nCorrect implementation (default_factory):")
    print(f"  c1.id = {c1.id}")
    print(f"  c2.id = {c2.id}")
    print(f"  c3.id = {c3.id}")
    print(f"  All same? {c1.id == c2.id == c3.id}")
    print("  -> Correct: Each instance has a unique UUID!")
    print()


# ============================================================================
# ERROR 3: Missing Constraints Allow Invalid Data
# ============================================================================

def demo_missing_constraints():
    """
    Without Field constraints, invalid data silently passes validation.
    """
    print("\n" + "="*70)
    print("ERROR 3: Missing Constraints Allow Invalid Data")
    print("="*70)

    class UserNoConstraints(BaseModel):
        """Accepts any values that match the types."""
        username: str
        age: int
        email: str

    class UserWithConstraints(BaseModel):
        """Validates business rules."""
        username: str = Field(min_length=3, max_length=20, pattern=r'^[a-z0-9]+$')
        age: int = Field(ge=0, le=150)
        email: str = Field(pattern=r'^[\w.-]+@[\w.-]+\.\w+$')

    # Invalid data that violates business rules
    invalid_data = {
        "username": "X",           # Too short, has uppercase
        "age": -5,                 # Negative age
        "email": "not-an-email"   # Invalid format
    }

    print("Invalid data:", invalid_data)

    # Without constraints - silently accepts bad data
    no_constraints = UserNoConstraints(**invalid_data)
    print(f"\nWithout constraints: {no_constraints}")
    print("  -> Problem: Invalid data is accepted without error!")
    print("  -> This can corrupt your database or cause downstream bugs.")

    # With constraints - properly rejects
    print(f"\nWith constraints:")
    try:
        UserWithConstraints(**invalid_data)
    except ValidationError as e:
        for error in e.errors():
            print(f"  {error['loc'][0]}: {error['type']}")
    print("  -> Correct: Invalid data is rejected at the boundary!")
    print()


# ============================================================================
# ERROR 4: Type Coercion Surprises Without strict=True
# ============================================================================

def demo_type_coercion_surprises():
    """
    Without strict=True, Pydantic coerces types which can cause surprises.
    """
    print("\n" + "="*70)
    print("ERROR 4: Type Coercion Surprises")
    print("="*70)

    class LooseTypes(BaseModel):
        count: int
        price: float
        is_active: bool

    class StrictTypes(BaseModel):
        count: int = Field(strict=True)
        price: float = Field(strict=True)
        is_active: bool = Field(strict=True)

    # Data with "wrong" types that can be coerced
    data = {
        "count": "42",        # String that looks like int
        "price": "19.99",     # String that looks like float
        "is_active": 1        # Int that can be bool
    }

    print(f"Input data: {data}")

    # Loose - coerces without warning
    loose = LooseTypes(**data)
    print(f"\nLoose model accepts and coerces:")
    print(f"  count: '{data['count']}' -> {loose.count} ({type(loose.count).__name__})")
    print(f"  price: '{data['price']}' -> {loose.price} ({type(loose.price).__name__})")
    print(f"  is_active: {data['is_active']} -> {loose.is_active} ({type(loose.is_active).__name__})")
    print("  -> This might be fine, but could hide bugs in upstream data!")

    # Strict - rejects wrong types
    print(f"\nStrict model rejects wrong types:")
    try:
        StrictTypes(**data)
    except ValidationError as e:
        for error in e.errors():
            print(f"  {error['loc'][0]}: {error['msg']}")
    print("  -> Catches data quality issues early!")

    # Real-world bug: truthy values becoming True
    print(f"\nReal-world coercion surprise:")
    tricky_data = {"count": 1, "price": 1, "is_active": "yes"}  # "yes" -> True
    loose_tricky = LooseTypes(**tricky_data)
    print(f"  Input is_active='yes' -> {loose_tricky.is_active}")
    print("  -> Any non-empty string becomes True!")
    print()


# ============================================================================
# ERROR 5: Alias Mismatch Causes Validation Failure
# ============================================================================

def demo_alias_mismatch():
    """
    When input data uses different field names, you need aliases.
    """
    print("\n" + "="*70)
    print("ERROR 5: Alias Mismatch Causes Validation Failure")
    print("="*70)

    class UserNoAlias(BaseModel):
        user_id: int
        user_name: str
        email_address: str

    class UserWithAlias(BaseModel):
        model_config = ConfigDict(populate_by_name=True)

        user_id: int = Field(alias="userId")
        user_name: str = Field(validation_alias=AliasChoices("userName", "user_name", "name"))
        email_address: str = Field(validation_alias="emailAddress")

    # API sends camelCase (common in JavaScript)
    api_data = {
        "userId": 123,
        "userName": "johndoe",
        "emailAddress": "john@example.com"
    }

    print(f"API data (camelCase): {api_data}")

    # Without aliases - fails
    print(f"\nWithout aliases:")
    try:
        UserNoAlias(**api_data)
    except ValidationError as e:
        for error in e.errors():
            print(f"  Missing: {error['loc'][0]}")
    print("  -> Validation fails! Field names don't match.")

    # With aliases - works
    user = UserWithAlias(**api_data)
    print(f"\nWith aliases:")
    print(f"  Parsed successfully: {user}")
    print(f"  Python attribute: user.user_name = '{user.user_name}'")
    print()


# ============================================================================
# ERROR 6: Nested Data Access Without AliasPath
# ============================================================================

def demo_nested_data_access():
    """
    AliasPath is needed to extract data from nested structures.
    """
    print("\n" + "="*70)
    print("ERROR 6: Nested Data Access Without AliasPath")
    print("="*70)

    # API response with nested data
    api_response = {
        "user": {
            "profile": {
                "name": "John Doe",
                "email": "john@example.com"
            }
        },
        "metadata": {
            "created": "2024-01-01"
        }
    }

    class FlattenedNoPath(BaseModel):
        """Without AliasPath - can't access nested data."""
        name: str
        email: str
        created: str

    class FlattenedWithPath(BaseModel):
        """With AliasPath - extracts from nested structure."""
        name: str = Field(validation_alias=AliasPath("user", "profile", "name"))
        email: str = Field(validation_alias=AliasPath("user", "profile", "email"))
        created: str = Field(validation_alias=AliasPath("metadata", "created"))

    print(f"Nested API response structure:")
    print(f"  {api_response}")

    # Without AliasPath - fails
    print(f"\nWithout AliasPath:")
    try:
        FlattenedNoPath(**api_response)
    except ValidationError as e:
        for error in e.errors()[:3]:  # Show first 3
            print(f"  Missing: {error['loc'][0]}")
    print("  -> Cannot access nested fields!")

    # With AliasPath - works
    flat = FlattenedWithPath(**api_response)
    print(f"\nWith AliasPath:")
    print(f"  Flattened: name='{flat.name}', email='{flat.email}', created='{flat.created}'")
    print()


# ============================================================================
# ERROR 7: Discriminated Union Confusion
# ============================================================================

def demo_discriminator_issues():
    """
    Without discriminator, union validation is slower and error messages unclear.
    """
    print("\n" + "="*70)
    print("ERROR 7: Discriminated Union Issues")
    print("="*70)

    class Dog(BaseModel):
        type: Literal["dog"] = "dog"
        barks: bool

    class Cat(BaseModel):
        type: Literal["cat"] = "cat"
        meows: bool

    class Fish(BaseModel):
        type: Literal["fish"] = "fish"
        swims: bool

    class PetOwnerNoDiscriminator(BaseModel):
        """Without discriminator - tries each type in order."""
        pet: Dog | Cat | Fish

    class PetOwnerWithDiscriminator(BaseModel):
        """With discriminator - uses type field to pick correct model."""
        pet: Dog | Cat | Fish = Field(discriminator="type")

    # Invalid data
    bad_data = {"pet": {"type": "dragon", "breathes_fire": True}}

    print("Invalid pet data:", bad_data)

    # Without discriminator - confusing error
    print(f"\nWithout discriminator:")
    try:
        PetOwnerNoDiscriminator(**bad_data)
    except ValidationError as e:
        print(f"  Errors: {len(e.errors())} validation errors")
        print(f"  Error types: {[err['type'] for err in e.errors()[:3]]}")
    print("  -> Confusing: tried each union member, all failed!")

    # With discriminator - clear error
    print(f"\nWith discriminator:")
    try:
        PetOwnerWithDiscriminator(**bad_data)
    except ValidationError as e:
        error = e.errors()[0]
        print(f"  Clear error: {error['msg']}")
    print("  -> Clear: 'dragon' is not a valid tag!")
    print()


# ============================================================================
# ERROR 8: Decimal Precision Loss
# ============================================================================

def demo_decimal_precision_loss():
    """
    Without decimal constraints, you can lose precision or accept invalid values.
    """
    print("\n" + "="*70)
    print("ERROR 8: Decimal Precision Loss")
    print("="*70)

    class MoneyNoConstraints(BaseModel):
        amount: Decimal

    class MoneyWithConstraints(BaseModel):
        amount: Decimal = Field(max_digits=10, decimal_places=2, ge=0)

    # Various problematic inputs
    test_cases = [
        Decimal("99999999999.99"),    # Too many digits
        Decimal("123.456"),            # Too many decimal places
        Decimal("-50.00"),             # Negative
        Decimal("0.001"),              # More precision than needed
    ]

    print("Testing various decimal inputs:")

    for value in test_cases:
        print(f"\n  Input: {value}")

        # Without constraints - accepts anything
        no_constraints = MoneyNoConstraints(amount=value)
        print(f"    No constraints: accepted as {no_constraints.amount}")

        # With constraints - validates
        try:
            with_constraints = MoneyWithConstraints(amount=value)
            print(f"    With constraints: accepted as {with_constraints.amount}")
        except ValidationError as e:
            print(f"    With constraints: REJECTED - {e.errors()[0]['msg']}")

    print("\n  -> Without constraints, invalid money values slip through!")
    print()


# ============================================================================
# ERROR 9: Mutable Field Assignment Without frozen
# ============================================================================

def demo_mutable_assignment():
    """
    Without frozen=True, fields can be accidentally modified.
    """
    print("\n" + "="*70)
    print("ERROR 9: Accidental Field Modification")
    print("="*70)

    class MutableRecord(BaseModel):
        id: int
        created_at: datetime = Field(default_factory=datetime.now)

    class ImmutableRecord(BaseModel):
        id: int = Field(frozen=True)
        created_at: datetime = Field(default_factory=datetime.now, frozen=True)

    # Create mutable record
    record = MutableRecord(id=1)
    print(f"Mutable record: id={record.id}, created_at={record.created_at}")

    # Oops - accidentally modified!
    record.id = 999
    record.created_at = datetime(2000, 1, 1)
    print(f"After modification: id={record.id}, created_at={record.created_at}")
    print("  -> Problem: ID and timestamp were silently modified!")

    # Immutable record
    immutable = ImmutableRecord(id=1)
    print(f"\nImmutable record: id={immutable.id}")

    print("Trying to modify frozen fields:")
    try:
        immutable.id = 999
    except ValidationError:
        print("  id: BLOCKED - Field is frozen")

    try:
        immutable.created_at = datetime(2000, 1, 1)
    except ValidationError:
        print("  created_at: BLOCKED - Field is frozen")
    print()


# ============================================================================
# ERROR 10: Sensitive Data Exposure Without exclude/repr
# ============================================================================

def demo_sensitive_data_exposure():
    """
    Without exclude and repr=False, sensitive data can be accidentally exposed.
    """
    print("\n" + "="*70)
    print("ERROR 10: Sensitive Data Exposure")
    print("="*70)

    class UserExposed(BaseModel):
        username: str
        password: str
        api_key: str

    class UserProtected(BaseModel):
        username: str
        password: str = Field(repr=False, exclude=True)
        api_key: str = Field(repr=False, exclude=True)

    data = {
        "username": "admin",
        "password": "super_secret_123",
        "api_key": "sk-abc123xyz789"
    }

    exposed = UserExposed(**data)
    protected = UserProtected(**data)

    print("User data with sensitive fields:")

    print(f"\nExposed model:")
    print(f"  repr: {repr(exposed)}")
    print(f"  dict: {exposed.model_dump()}")
    print("  -> DANGER: Password and API key visible in logs/responses!")

    print(f"\nProtected model:")
    print(f"  repr: {repr(protected)}")
    print(f"  dict: {protected.model_dump()}")
    print("  -> Safe: Sensitive fields hidden from repr and serialization!")

    # But you can still access them directly when needed
    print(f"\n  Direct access still works: protected.password = '{protected.password}'")
    print()


# ============================================================================
# ERROR 11: Pattern Validation Missing
# ============================================================================

def demo_pattern_validation_missing():
    """
    Without pattern validation, malformed strings pass through.
    """
    print("\n" + "="*70)
    print("ERROR 11: Pattern Validation Missing")
    print("="*70)

    class DataNoPattern(BaseModel):
        phone: str
        zip_code: str
        ssn: str

    class DataWithPattern(BaseModel):
        phone: str = Field(pattern=r'^\+?1?\d{10}$')
        zip_code: str = Field(pattern=r'^\d{5}(-\d{4})?$')
        ssn: str = Field(pattern=r'^\d{3}-\d{2}-\d{4}$')

    invalid_inputs = {
        "phone": "call-me-maybe",
        "zip_code": "ABCDE",
        "ssn": "1234567890"
    }

    print(f"Invalid format inputs: {invalid_inputs}")

    # Without patterns - accepts garbage
    no_pattern = DataNoPattern(**invalid_inputs)
    print(f"\nWithout patterns:")
    print(f"  Accepted: {no_pattern}")
    print("  -> Problem: Invalid formats accepted, will cause issues later!")

    # With patterns - rejects
    print(f"\nWith patterns:")
    try:
        DataWithPattern(**invalid_inputs)
    except ValidationError as e:
        for error in e.errors():
            print(f"  {error['loc'][0]}: string_pattern_mismatch")
    print("  -> Correct: Invalid formats rejected at validation!")
    print()


# ============================================================================
# MAIN
# ============================================================================

def main():
    print("=" * 70)
    print("PYDANTIC FIELD ERROR EXAMPLES")
    print("What goes wrong when you don't use Field properly")
    print("=" * 70)

    demo_shared_mutable_bug()
    demo_static_evaluation_bug()
    demo_missing_constraints()
    demo_type_coercion_surprises()
    demo_alias_mismatch()
    demo_nested_data_access()
    demo_discriminator_issues()
    demo_decimal_precision_loss()
    demo_mutable_assignment()
    demo_sensitive_data_exposure()
    demo_pattern_validation_missing()

    print("=" * 70)
    print("ALL ERROR EXAMPLES COMPLETED")
    print("=" * 70)


if __name__ == "__main__":
    main()

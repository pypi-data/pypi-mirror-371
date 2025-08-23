"""Test the ergonomic Duck API with correct structural typing."""

from pydantic import BaseModel, Field

from duckdantic import Duck, DuckModel, DuckRootModel, as_duck, is_duck_of


class User(BaseModel):
    id: int
    email: str
    name: str | None = None


class Customer(BaseModel):
    id: int
    email: str
    company: str


def test_duck_structural_checking():
    """Test Duck for structural type checking between classes."""
    # Create duck type
    UserDuck = Duck(User)
    
    # Customer class has all User fields (structural match)
    assert UserDuck.validate(Customer)
    
    # Plain class with required fields
    class Person:
        id: int
        email: str
        phone: str = "555-1234"
    
    assert UserDuck.validate(Person)
    
    # Missing required field
    class BadModel:
        id: int
        # missing email
    
    assert not UserDuck.validate(BadModel)


def test_duck_generic_syntax():
    """Test Duck[Model] syntax."""
    # Generic syntax
    UserDuck = Duck[User]
    
    # Check structural compatibility
    assert UserDuck.validate(Customer)
    
    # Can also check instances of compatible models
    customer = Customer(id=1, email="c@example.com", company="ACME")
    assert UserDuck.validate(customer)


def test_duck_abc_isinstance():
    """Test isinstance with ABC from Duck."""
    UserDuck = Duck(User)
    
    # Check class subtyping
    assert issubclass(Customer, UserDuck.abc)
    
    # Check instance
    customer = Customer(id=1, email="c@example.com", company="ACME")
    assert isinstance(customer, UserDuck.abc)


def test_duck_convert():
    """Test converting objects with Duck."""
    UserDuck = Duck(User)
    
    # Convert from compatible instance
    customer = Customer(id=1, email="user@example.com", company="ACME", name="John")
    user = UserDuck.convert(customer.model_dump())
    assert isinstance(user, User)
    assert user.id == 1
    assert user.email == "user@example.com"


def test_basemodel_duck_methods():
    """Test duck methods added to BaseModel."""
    # Check if Customer class satisfies User structure
    assert User.__duck_validates__(Customer)
    
    # Convert from compatible instance
    customer = Customer(id=1, email="c@example.com", company="Corp")
    user = User.__duck_convert__(customer.model_dump(), name="Default")
    assert user.name == "Default"


def test_is_duck_of():
    """Test is_duck_of convenience function."""
    # Class checking
    assert is_duck_of(Customer, User)  # Customer has User fields
    
    # Instance checking
    customer = Customer(id=2, email="c@example.com", company="Corp")
    assert is_duck_of(customer, User)
    
    # Bad class
    class BadModel:
        name: str  # missing required fields
    
    assert not is_duck_of(BadModel, User)


def test_as_duck():
    """Test as_duck conversion function."""
    # Convert from model instance
    customer = Customer(id=2, email="c@example.com", company="ACME")
    user = as_duck(User, customer.model_dump())
    assert isinstance(user, User)
    assert user.id == 2
    assert user.email == "c@example.com"


def test_duck_model_class():
    """Test DuckModel base class."""
    class Person(DuckModel):
        id: int
        name: str
        age: int | None = None
    
    # Check structural compatibility
    class Employee:
        id: int
        name: str
        department: str
        age: int = 30
    
    assert Person.is_duck(Employee)
    
    # Create from compatible instance
    emp = Employee()
    emp.id = 1
    emp.name = "Alice"
    emp.department = "HR"
    
    person = Person.from_duck(emp)
    assert person.id == 1
    assert person.name == "Alice"
    assert person.age == 30
    
    # Get duck type
    PersonDuck = Person.duck_type()
    assert PersonDuck.validate(Employee)


def test_duck_with_field_aliases():
    """Test duck typing with field aliases."""
    class Product(BaseModel):
        id: int
        name: str = Field(alias="product_name")
        price: float
    
    ProductDuck = Duck(Product)
    
    # Another model with same field names
    class Item(BaseModel):
        id: int
        name: str  # Same field name
        price: float
        
    # Should validate - has required fields
    assert ProductDuck.validate(Item)
    
    # Test actual alias usage in data
    product_data = {"id": 1, "product_name": "Widget", "price": 9.99}
    product = Product.model_validate(product_data)
    assert product.name == "Widget"


def test_duck_root_model():
    """Test DuckRootModel functionality."""
    from typing import List
    
    class UserList(DuckRootModel[List[User]]):
        pass
    
    # Test validation of data
    data = [
        {"id": 1, "email": "a@b.com"},
        {"id": 2, "email": "c@d.com"}
    ]
    
    assert UserList.__duck_validates__(data)
    
    # Convert data
    users = UserList.from_duck(data)
    assert len(users.root) == 2
    assert users.root[0].id == 1


def test_duck_with_methods():
    """Test duck typing combined with method checking."""
    from duckdantic import MethodSpec, methods_satisfy
    
    # Define a model with expected structure
    class StorageModel(BaseModel):
        name: str
        capacity: int
    
    # And expected methods
    storage_methods = [
        MethodSpec(name="save", params=[str], returns=bool),
        MethodSpec(name="load", params=[str], returns=dict),
    ]
    
    # A class that satisfies both
    class FileStorage:
        name: str
        capacity: int
        
        def __init__(self, name: str, capacity: int):
            self.name = name
            self.capacity = capacity
        
        def save(self, path: str) -> bool:
            return True
        
        def load(self, path: str) -> dict:
            return {}
    
    # Check structural compatibility
    StorageDuck = Duck(StorageModel)
    assert StorageDuck.validate(FileStorage)
    
    # Check method compatibility
    assert methods_satisfy(FileStorage, storage_methods)
"""
Pydantic Model Introspection for FluidKit V2

Discovers and introspects Pydantic models referenced by FastAPI routes
using runtime introspection within project boundaries only.
External types become 'any' with JSDoc context.
"""

import inspect
from enum import Enum
from pathlib import Path
from pydantic import BaseModel
from typing import List, Dict, Any, Optional

from fluidkit.core.utils import format_annotation_for_display
from fluidkit.core.type_conversion import python_type_to_field_annotation
from fluidkit.core.schema import ModelNode, RouteNode, Field, FieldAnnotation, ModuleLocation, BaseType


def discover_models_from_routes(route_nodes: List[RouteNode], project_root: Optional[str] = None) -> List[ModelNode]:
    """
    Discover Pydantic models referenced by FastAPI routes.
    
    Only introspects project types - external types become 'any'.
    
    Args:
        route_nodes: List of RouteNode objects from FastAPI introspection
        project_root: Project root directory for boundary detection (optional)
        
    Returns:
        List of discovered ModelNode objects (project types only)
    """
    discovered = {}
    project_path = Path(project_root).resolve() if project_root else None
    
    for route in route_nodes:
        for param in route.parameters:
            _discover_from_field_annotation(param.annotation, discovered, project_path)
        
        if route.return_type:
            _discover_from_field_annotation(route.return_type, discovered, project_path)
    
    return list(discovered.values())


def _discover_from_field_annotation(annotation: FieldAnnotation, discovered: Dict[str, ModelNode], 
                                  project_path: Optional[Path]):
    """
    Discover models from FieldAnnotation - project types only.
    
    Args:
        annotation: FieldAnnotation to process
        discovered: Dictionary to track discovered models
        project_path: Project root path for boundary detection
    """
    if annotation.class_reference and annotation.custom_type:
        model_name = annotation.custom_type
        cls = annotation.class_reference
        
        # Check for name collision before adding
        if model_name in discovered:
            existing_model = discovered[model_name]
            # Same class reference = no collision, just skip
            if existing_model.location.module_path == cls.__module__:
                return
            
            # Different modules with same name = collision
            _raise_import_collision_error(model_name, existing_model, cls)
        
        # No collision - proceed with normal discovery
        module_name = cls.__module__
        
        from fluidkit.core.utils import classify_module
        module_type = classify_module(module_name, str(project_path) if project_path else None)
        
        # Only introspect project types
        if module_type != 'project':
            return
        
        model_node = _introspect_class_to_model_node(cls)
        if model_node:
            discovered[model_name] = model_node
            
            # Recursively discover from this model's fields
            for field in model_node.fields:
                _discover_from_field_annotation(field.annotation, discovered, project_path)
    
    # Recursively check nested annotations
    for arg in annotation.args:
        _discover_from_field_annotation(arg, discovered, project_path)


def _raise_import_collision_error(model_name: str, existing_model: ModelNode, new_class: type):
    """Raise descriptive error for import name collisions."""
    
    error_lines = [
        f"FluidKit detected a model name collision for '{model_name}':",
        "",
        "The same model name is used by classes from different modules:",
        f"  1. {existing_model.location.module_path} ({existing_model.location.file_path})",
        f"  2. {new_class.__module__} ({getattr(new_class, '__file__', 'unknown')})",
        "",
        "This collision occurs because both classes resolve to the same TypeScript interface name.",
        "Import aliases don't solve this since FluidKit resolves aliases to original class names.",
        "",
        "Solutions:",
        "1. Rename one of the conflicting classes:",
        f"   class {model_name} -> class Core{model_name}  (in one of the modules)",
        "",
        "2. Avoid importing both classes in files that FluidKit processes:",
        "   - Don't use both models in the same route file or related model files",
        "   - Restructure to use only one of the models",
        "",
        "3. Reorganize your model structure to avoid name conflicts"
    ]
    
    raise ValueError("\n".join(error_lines))


def _introspect_class_to_model_node(cls: type) -> Optional[ModelNode]:
    """Convert Python class to ModelNode using runtime introspection."""
    try:
        from fluidkit.core.utils import create_module_location_from_object
        location = create_module_location_from_object(cls, is_external=False)
        
        if _is_pydantic_model(cls):
            return _introspect_pydantic_model(cls, location)
        elif _is_enum_class(cls):
            return _introspect_enum_model(cls, location)
        else:
            return None
            
    except Exception as e:
        print(f"Warning: Failed to introspect class {cls.__name__}: {e}")
        return None


def _is_pydantic_model(cls: type) -> bool:
    """Check if class is a Pydantic model."""
    try:
        return issubclass(cls, BaseModel)
    except TypeError:
        return False


def _is_enum_class(cls: type) -> bool:
    """Check if class is an Enum."""
    try:
        return issubclass(cls, Enum)
    except TypeError:
        return False


def _introspect_pydantic_model(cls: type, location: ModuleLocation) -> ModelNode:
    """
    Introspect Pydantic model using Pydantic's field introspection.
    
    Handles both Pydantic V1 and V2 field access patterns.
    
    Args:
        cls: Pydantic model class
        location: ModuleLocation for the class
        
    Returns:
        ModelNode with introspected fields
    """
    fields = []
    model_fields = _get_pydantic_fields(cls)
    
    for field_name, field_info in model_fields.items():
        try:
            field_annotation = _extract_field_annotation_from_pydantic_field(cls, field_name, field_info)
            default_value = _extract_default_from_pydantic_field(field_info)
            description = _extract_description_from_pydantic_field(field_info)
            
            field_obj = Field(
                name=field_name,
                annotation=field_annotation,
                default=default_value,
                description=description
            )
            fields.append(field_obj)
            
        except Exception as e:
            print(f"Warning: Failed to introspect field {field_name} in {cls.__name__}: {e}")
            continue
    
    inheritance = [base.__name__ for base in cls.__bases__ if base != object]
    
    return ModelNode(
        name=cls.__name__,
        fields=fields,
        location=location,
        docstring=cls.__doc__,
        inheritance=inheritance,
        is_enum=False
    )


def _introspect_enum_model(cls: type, location: ModuleLocation) -> ModelNode:
    """
    Introspect Enum class to ModelNode.
    
    Args:
        cls: Enum class
        location: ModuleLocation for the class
        
    Returns:
        ModelNode representing the enum
    """
    fields = []
    
    # Extract enum members
    for member_name, member_value in cls.__members__.items():
        # Create field for each enum value
        value_annotation = python_type_to_field_annotation(type(member_value.value))
        
        field_obj = Field(
            name=member_name,
            annotation=value_annotation,
            default=member_value.value
        )
        fields.append(field_obj)
    
    # Extract inheritance information
    inheritance = [base.__name__ for base in cls.__bases__ if base != object]
    
    return ModelNode(
        name=cls.__name__,
        fields=fields,
        location=location,
        docstring=cls.__doc__,
        inheritance=inheritance,
        is_enum=True
    )


def _get_pydantic_fields(cls: type) -> Dict[str, Any]:
    """
    Get Pydantic fields, handling both V1 and V2.
    
    Args:
        cls: Pydantic model class
        
    Returns:
        Dictionary of field_name -> field_info
    """
    # Try Pydantic V2 first
    if hasattr(cls, 'model_fields'):
        return cls.model_fields
    
    # Fall back to Pydantic V1
    elif hasattr(cls, '__fields__'):
        return cls.__fields__
    
    # No fields found
    else:
        return {}


def _extract_field_annotation_from_pydantic_field(cls: type, field_name: str, field_info: Any) -> FieldAnnotation:
    """
    Extract type annotation from Pydantic field information.
    
    Args:
        cls: Pydantic model class
        field_name: Name of the field
        field_info: Pydantic field information object
        
    Returns:
        FieldAnnotation representing the field type
    """
    # Try to get annotation from class annotations
    if hasattr(cls, '__annotations__') and field_name in cls.__annotations__:
        py_type = cls.__annotations__[field_name]
        return python_type_to_field_annotation(py_type)
    
    # Try to get from field_info annotation (Pydantic V2)
    elif hasattr(field_info, 'annotation'):
        return python_type_to_field_annotation(field_info.annotation)
    
    # Try to get from field_info type_ (Pydantic V1)
    elif hasattr(field_info, 'type_'):
        return python_type_to_field_annotation(field_info.type_)
    
    # Fallback to Any
    else:
        return FieldAnnotation(base_type=BaseType.ANY)


def _extract_default_from_pydantic_field(field_info: Any) -> Any:
    """
    Extract default value from Pydantic field information.
    
    Args:
        field_info: Pydantic field information object
        
    Returns:
        Default value or None if field is required
    """
    # Handle Pydantic V2
    if hasattr(field_info, 'default'):
        default = field_info.default
        # Check for Pydantic's special "required" markers
        if hasattr(default, '__class__'):
            class_name = default.__class__.__name__
            if 'PydanticUndefined' in class_name or 'Undefined' in class_name:
                return None
        return default
    
    # Handle Pydantic V1
    elif hasattr(field_info, 'default'):
        default = field_info.default
        if default is ...:  # Ellipsis means required
            return None
        return default
    
    # No default found
    return None


def _extract_description_from_pydantic_field(field_info: Any) -> Optional[str]:
    """
    Extract description from Pydantic field information.
    
    Args:
        field_info: Pydantic field information object
        
    Returns:
        Field description or None
    """
    # Try direct description attribute
    if hasattr(field_info, 'description'):
        return field_info.description
    
    # Try field_info (for older Pydantic versions)
    elif hasattr(field_info, 'field_info') and hasattr(field_info.field_info, 'description'):
        return field_info.field_info.description
    
    return None


def test_pydantic_introspection():
    """Test Pydantic model introspection with various scenarios."""
    from enum import Enum
    from typing import Optional, List
    from pydantic import BaseModel, Field
    
    # Test models
    class UserStatus(str, Enum):
        ACTIVE = "active"
        INACTIVE = "inactive"
    
    class Profile(BaseModel):
        bio: str = Field(..., description="User biography")
        website: Optional[str] = None
    
    class User(BaseModel):
        id: int
        name: str = Field(..., description="User's full name")
        email: Optional[str] = None
        status: UserStatus = UserStatus.ACTIVE
        profile: Optional[Profile] = None
    
    # Test individual model introspection
    print("=== PYDANTIC INTROSPECTION TEST ===")
    
    # Test Enum introspection
    from fluidkit.core.utils import create_module_location_from_object
    location = create_module_location_from_object(UserStatus)
    status_model = _introspect_enum_model(UserStatus, location)
    print(f"UserStatus Enum: {status_model.name}")
    print(f"  Fields: {[f.name for f in status_model.fields]}")
    print(f"  Is Enum: {status_model.is_enum}")
    print()
    
    # Test Pydantic model introspection
    location = create_module_location_from_object(User)
    user_model = _introspect_pydantic_model(User, location)
    print(f"User Model: {user_model.name}")
    print(f"  Fields: {len(user_model.fields)}")
    for field in user_model.fields:
        print(f"    {field.name}: {field.annotation.custom_type or field.annotation.base_type}")
        if field.description:
            print(f"      Description: {field.description}")
        if field.default is not None:
            print(f"      Default: {field.default}")
    print()


if __name__ == "__main__":
    test_pydantic_introspection()

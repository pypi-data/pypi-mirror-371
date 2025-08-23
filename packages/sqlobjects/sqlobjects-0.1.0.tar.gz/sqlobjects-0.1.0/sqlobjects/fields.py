"""SQLObjects Fields Module - Enhanced SQLAlchemy Core types with function chaining"""

import builtins
import inspect
from collections.abc import Callable
from functools import lru_cache
from typing import TYPE_CHECKING, Any, Generic, NotRequired, Type, TypedDict, TypeVar, overload

from sqlalchemy import Column as CoreColumn
from sqlalchemy import func
from sqlalchemy.sql.elements import ColumnElement
from sqlalchemy.sql.sqltypes import (
    ARRAY,
    JSON,
    BigInteger,
    Boolean,
    Date,
    DateTime,
    Double,
    Enum,
    Float,
    Integer,
    Interval,
    LargeBinary,
    Numeric,
    SmallInteger,
    String,
    Text,
    Time,
    TypeEngine,
    Uuid,
)

from .expressions import (
    DateTimeFunctionMixin,
    FunctionExpression,
    FunctionMixin,
    NumericFunctionMixin,
    StringFunctionMixin,
)
from .relations import relationship


if TYPE_CHECKING:
    from sqlalchemy.sql.sqltypes import TypeEngine  # noqa


__all__ = [
    # Core
    "Column",
    "column",
    "ColumnAttribute",
    "Auto",
    # Type system
    "register_field_type",
    "create_type_instance",
    "get_type_definition",
    # Shortcut functions
    "str_column",
    "int_column",
    "bool_column",
    "json_column",
    # shortcuts
    "datetime_column",
    "numeric_column",
    "text_column",
    "binary_column",
    # Relationship fields
    "relationship",
    # Validation utilities
    "get_field_validators",
    "get_model_metadata",
]

# === Type System ===

T = TypeVar("T")


class TypeArgument(TypedDict):
    name: str
    type: type[Any]
    required: bool
    default: Any
    transform: NotRequired[Callable[[Any], Any]]
    positional: NotRequired[bool]


class TypeDefinition(TypedDict):
    type: type[Any]
    arguments: list[TypeArgument]


def _transform_array_item_type(item_type: str | type[Any]) -> type[Any]:
    """Transform array item_type from string to SQLAlchemy type."""
    if isinstance(item_type, str):
        type_def = _registry.get_type(item_type)
        if type_def:
            return type_def["type"]()
        else:
            raise ValueError(f"Unknown array item type: {item_type}")
    return item_type


def _extract_constructor_params(type_class: type[Any]) -> list[TypeArgument]:
    """Extract constructor parameters using inspect."""
    try:
        sig = inspect.signature(type_class.__init__)
        arguments = []
        for param_name, param in sig.parameters.items():
            if param_name == "self":
                continue
            arguments.append(
                {
                    "name": param_name,
                    "type": Any,
                    "required": param.default == inspect.Parameter.empty,
                    "default": param.default if param.default != inspect.Parameter.empty else None,
                }
            )
        return arguments
    except Exception:  # noqa
        return []


def _get_type_params(type_def: TypeDefinition, kwargs: dict[str, Any]) -> dict[str, Any]:
    """Extract type construction parameters from kwargs

    Args:
        type_def: Type definition containing parameter specifications
        kwargs: Keyword arguments to extract from

    Returns:
        Dictionary of type parameters with transformed values
    """
    type_params = {}
    type_param_names = {arg["name"] for arg in type_def["arguments"]}

    for key, value in kwargs.items():
        if key in type_param_names:
            arg_def = next(arg for arg in type_def["arguments"] if arg["name"] == key)
            if "transform" in arg_def and arg_def["transform"]:
                value = arg_def["transform"](value)
            type_params[key] = value

    # Apply default values
    for arg in type_def["arguments"]:
        if arg["name"] not in type_params and not arg["required"] and arg["default"] is not None:
            default_value = arg["default"]
            if "transform" in arg and arg["transform"]:
                default_value = arg["transform"](default_value)
            type_params[arg["name"]] = default_value

    return type_params


class TypeRegistry:
    """Type registry with caching and lazy loading support

    Manages registration and lookup of field types with LRU caching
    for performance optimization.
    """

    def __init__(self):
        self._types: dict[str, TypeDefinition] = {}
        self._aliases: dict[str, str] = {}
        self._initialized = False

    @lru_cache(maxsize=128)  # noqa: B019
    def get_type(self, name: str) -> TypeDefinition:
        """Cached type lookup with lazy initialization

        Args:
            name: Type name or alias to look up

        Returns:
            Type definition for the requested type

        Raises:
            ValueError: If type is not found
        """
        if not self._initialized:
            self._init_builtin_types()

        type_def = self._types.get(self._resolve_alias(name))
        if not type_def:
            available_types = list(self._types.keys())
            raise ValueError(f"Unknown type: '{name}'. Available types: {available_types}")

        return type_def

    def register(self, type_def: TypeDefinition | type[Any], type_name: str | None, aliases: list[str] | None = None):
        """Register a type with optional aliases

        Args:
            type_def: Type definition or type class to register
            type_name: Name to register the type under
            aliases: Optional list of alias names
        """
        if isinstance(type_def, type):
            type_def = self._create_type_definition(type_def)

        name = type_name or type_def["type"].__name__.lower()

        self._types[name] = type_def

        if aliases:
            for alias in aliases:
                self._aliases[alias] = name

    def create_type_instance(self, type_name: str, type_params: dict[str, Any]):
        """Create type instance with parameters

        Args:
            type_name: Name of the type to create
            type_params: Parameters for type construction

        Returns:
            Instantiated SQLAlchemy type object
        """
        type_def = self.get_type(type_name)

        positional_args = []
        keyword_args = {}

        for arg_def in type_def["arguments"]:
            param_name = arg_def["name"]
            if param_name not in type_params:
                continue

            value = type_params[param_name]

            # Check if it's a positional parameter (default False)
            if arg_def.get("positional", False):
                positional_args.append(value)
            else:
                keyword_args[param_name] = value

        return type_def["type"](*positional_args, **keyword_args)

    def _create_type_definition(self, type_class: Type[Any]) -> TypeDefinition:  # noqa
        """Create type definition from type class

        Args:
            type_class: Type class to analyze

        Returns:
            Type definition with extracted parameters
        """
        try:
            arguments = _extract_constructor_params(type_class)
            return {"type": type_class, "arguments": arguments}
        except Exception:  # noqa
            return {"type": type_class, "arguments": []}

    def _resolve_alias(self, name: str) -> str:
        """Resolve type alias to actual type name

        Args:
            name: Type name or alias

        Returns:
            Actual type name
        """
        return self._aliases.get(name, name)

    def _init_builtin_types(self):
        """Initialize all built-in enhanced types

        Registers all standard SQLAlchemy types with enhanced functionality.
        """
        builtin_types = [
            # Auto type (automatic inference)
            (Auto, "auto", []),
            # String abstract types
            (EnhancedString, "string", ["str"]),
            (EnhancedText, "text"),
            # Numeric abstract types
            (EnhancedInteger, "integer", ["int"]),
            (EnhancedBigInteger, "bigint"),
            (EnhancedSmallInteger, "smallint"),
            (EnhancedFloat, "float"),
            (EnhancedDouble, "double"),
            (EnhancedNumeric, "numeric", ["decimal"]),
            # Boolean abstract types
            (EnhancedBoolean, "boolean", ["bool"]),
            # Date/time abstract types
            (EnhancedDate, "date"),
            (EnhancedDateTime, "datetime"),
            (EnhancedTime, "time"),
            (EnhancedInterval, "interval"),
            # Binary abstract types
            (EnhancedLargeBinary, "binary", ["bytes"]),
            # UUID abstract types
            (EnhancedUuid, "uuid"),
            # Special types
            (EnhancedJSON, "json", ["dict"]),
        ]

        # Special types
        special_types = [
            (
                {
                    "type": ARRAY,
                    "arguments": [
                        {
                            "name": "item_type",
                            "type": Any,
                            "required": True,
                            "default": None,
                            "transform": _transform_array_item_type,
                            "positional": True,
                        },
                        {"name": "dimensions", "type": int, "required": False, "default": 1},
                    ],
                },
                "array",
                None,
            ),
            (
                {
                    "type": Enum,
                    "arguments": [
                        {"name": "enum_class", "type": type[Any], "required": True, "default": None, "positional": True}
                    ],
                },
                "enum",
                None,
            ),
        ]

        # Register all types
        for type_info in builtin_types + special_types:
            field_type = type_info[0]
            type_name = type_info[1]
            aliases = type_info[2] if len(type_info) > 2 else []
            self.register(field_type, type_name, aliases=aliases)

        self._initialized = True


def register_field_type(
    type_def: TypeDefinition | type[Any], type_name: str, *, aliases: list[str] | None = None
) -> None:
    """Register a field type in the global registry

    Args:
        type_def: Type definition or type class to register
        type_name: Name to register the type under
        aliases: Optional list of alias names
    """
    _registry.register(type_def, type_name, aliases=aliases)


def create_type_instance(type_name: str, kwargs: dict[str, Any]) -> Any:
    """Create type instance from name and parameters

    Args:
        type_name: Name of the type to create
        kwargs: Parameters for type construction

    Returns:
        Instantiated SQLAlchemy type object
    """
    type_def = _registry.get_type(type_name)
    type_params = _get_type_params(type_def, kwargs)
    return _registry.create_type_instance(type_name, type_params)


def get_type_definition(type_name: str) -> TypeDefinition:
    """Get type definition by name

    Args:
        type_name: Name of the type to look up

    Returns:
        Type definition for the requested type
    """
    return _registry.get_type(type_name)


# Global registry instance
_registry = TypeRegistry()


# === Auto Type ===


class Auto(TypeEngine):
    """Automatic type inference placeholder, similar to SQLAlchemy's NullType

    Used as a placeholder for automatic type inference based on default values
    or other context clues.
    """

    def __init__(self):
        super().__init__()

    def get_col_spec(self):  # noqa
        return "AUTO"

    def bind_processor(self, dialect):
        return None

    def result_processor(self, dialect, coltype):
        return None

    def __repr__(self):
        return "Auto()"


# === Enhanced Types ===


class EnhancedStringComparator(String.Comparator, StringFunctionMixin):  # pyright: ignore[reportIncompatibleMethodOverride]
    """Enhanced string comparator with direct function call support

    Provides string-specific comparison methods and function chaining.
    """

    def matches(self, pattern: str) -> ColumnElement[bool]:
        return self.expr.op("~")(pattern)

    def length_between(self, min_len: int, max_len: int) -> ColumnElement[bool]:
        return func.length(self.expr).between(min_len, max_len)


class EnhancedIntegerComparator(Integer.Comparator, NumericFunctionMixin):
    """Enhanced integer comparator with numeric functions

    Provides integer-specific comparison methods and numeric function chaining.
    """

    pass


class EnhancedNumericComparator(Numeric.Comparator, NumericFunctionMixin):
    """Enhanced numeric comparator with mathematical functions

    Provides numeric-specific comparison methods and mathematical function chaining.
    """

    pass


class EnhancedDateTimeComparator(DateTime.Comparator, DateTimeFunctionMixin):
    """Enhanced datetime comparator with date/time functions

    Provides datetime-specific comparison methods and date/time function chaining.
    """

    def is_today(self) -> ColumnElement[bool]:
        return func.date(self.expr) == func.current_date()  # noqa

    def is_past(self) -> ColumnElement[bool]:
        return self.expr < func.now()

    def is_future(self) -> ColumnElement[bool]:
        return self.expr > func.now()

    def year_equals(self, year: int) -> ColumnElement[bool]:
        return func.extract("year", self.expr) == year  # noqa

    def month_equals(self, month: int) -> ColumnElement[bool]:
        return func.extract("month", self.expr) == month  # noqa


class EnhancedBooleanComparator(Boolean.Comparator, FunctionMixin):
    """Enhanced boolean comparator with general functions

    Provides boolean-specific comparison methods and general function support.
    """

    def _get_expression(self):
        """Get current expression - uses Comparator's expr attribute

        Returns:
            The expression object for function operations
        """
        return self.expr

    def is_true(self) -> ColumnElement[bool]:
        return self.expr.is_(True)

    def is_false(self) -> ColumnElement[bool]:
        return self.expr.is_(False)


class EnhancedJSONComparator(JSON.Comparator):
    """Enhanced JSON comparator with JSON-specific operations

    Provides JSON path operations and key existence checks.
    """

    def has_key(self, key: str) -> ColumnElement[bool]:
        return self.expr.op("?")(key)

    def has_keys(self, *keys) -> ColumnElement[bool]:
        return self.expr.op("?&")(list(keys))

    def has_any_key(self, *keys) -> ColumnElement[bool]:
        return self.expr.op("?|")(list(keys))

    def path_exists(self, path: str) -> ColumnElement[bool]:
        return func.json_extract_path(self.expr, path).is_not(None)

    def extract_text(self, path: str) -> "FunctionExpression":
        return FunctionExpression(func.json_extract_path_text(self.expr, path))


class EnhancedString(String):
    """Enhanced string type with function chaining support"""

    comparator_factory = EnhancedStringComparator


class EnhancedText(Text):
    """Enhanced text type with function chaining support"""

    comparator_factory = EnhancedStringComparator


class EnhancedInteger(Integer):
    """Enhanced integer type with numeric function chaining support"""

    comparator_factory = EnhancedIntegerComparator


class EnhancedBigInteger(BigInteger):
    """Enhanced big integer type with numeric function chaining support"""

    comparator_factory = EnhancedIntegerComparator


class EnhancedSmallInteger(SmallInteger):
    """Enhanced small integer type with numeric function chaining support"""

    comparator_factory = EnhancedIntegerComparator


class EnhancedFloat(Float):
    """Enhanced float type with numeric function chaining support"""

    comparator_factory = EnhancedNumericComparator


class EnhancedNumeric(Numeric):
    """Enhanced numeric type with mathematical function chaining support"""

    comparator_factory = EnhancedNumericComparator


class EnhancedDateTime(DateTime):
    """Enhanced datetime type with date/time function chaining support"""

    comparator_factory = EnhancedDateTimeComparator


class EnhancedDate(Date):
    """Enhanced date type with date function chaining support"""

    comparator_factory = EnhancedDateTimeComparator


class EnhancedTime(Time):
    """Enhanced time type with time function chaining support"""

    comparator_factory = EnhancedDateTimeComparator


class EnhancedBoolean(Boolean):
    """Enhanced boolean type with boolean-specific operations"""

    comparator_factory = EnhancedBooleanComparator


class EnhancedJSON(JSON):
    """Enhanced JSON type with JSON path operations"""

    comparator_factory = EnhancedJSONComparator


class EnhancedDouble(Double):
    """Enhanced double precision float type with numeric function chaining support"""

    comparator_factory = EnhancedNumericComparator


class EnhancedUuid(Uuid):
    """Enhanced UUID type with string function chaining support"""

    comparator_factory = EnhancedStringComparator


class EnhancedLargeBinary(LargeBinary):
    """Enhanced binary type for large binary data"""

    comparator_factory = LargeBinary.Comparator


class EnhancedInterval(Interval):
    """Enhanced interval type for time intervals"""

    comparator_factory = Interval.Comparator


# === Column Classes ===


EnhancedType = TypeVar("EnhancedType")


class ColumnAttribute(Generic[EnhancedType], FunctionMixin):
    """Enhanced chaining operations for Core Column

    Provides function chaining, type-specific operations, and metadata access
    for SQLAlchemy Core columns.
    """

    def __init__(self, column: CoreColumn, model_class: type[Any]):  # noqa
        self.column = column  # Public attribute: users can access underlying SQLAlchemy Column
        self.model_class = model_class  # Public attribute: for introspection and debugging
        self._comparator = self._create_comparator()

        self._enhanced_params = self._get_info_params("_enhanced")
        self._performance_params = self._get_info_params("_performance")
        self._codegen_params = self._get_info_params("_codegen")

    def _get_expression(self):
        """Get current expression - returns column object

        Returns:
            The underlying SQLAlchemy column for function operations
        """
        return self.column

    def _create_comparator(self) -> Any:
        """Create appropriate comparator based on column type

        Returns:
            Type-specific comparator instance or None
        """
        column_type = self.column.type

        # Get comparator factory class
        comparator_class = getattr(column_type, "comparator_factory", None)
        if comparator_class:
            # Create comparator instance, passing column as expr
            return comparator_class(self.column)

        # If no custom comparator, return None
        return None

    def __getattr__(self, name: str) -> Any:
        """Smart attribute lookup: comparator -> FunctionMixin -> column

        Args:
            name: Attribute name to look up

        Returns:
            Attribute value from the appropriate source

        Raises:
            AttributeError: If attribute is not found
        """
        # 1. Try comparator first (type-specific methods)
        if self._comparator and hasattr(self._comparator, name):
            return getattr(self._comparator, name)

        # 2. Try FunctionMixin (general methods) - handled automatically through MRO
        try:
            return super().__getattribute__(name)
        except AttributeError:
            pass

        # 3. Try column native methods (except already exposed attributes)
        if name not in ("column", "model_class", "name", "type") and hasattr(self.column, name):
            return getattr(self.column, name)

        raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")

    # Proxy common query operations
    def __eq__(self, other) -> ColumnElement[bool]:  # type: ignore[reportIncompatibleMethodOverride]
        return self.column == other

    def __ne__(self, other) -> ColumnElement[bool]:  # type: ignore[reportIncompatibleMethodOverride]
        return self.column != other

    def __lt__(self, other) -> ColumnElement[bool]:
        return self.column < other

    def __le__(self, other) -> ColumnElement[bool]:
        return self.column <= other

    def __gt__(self, other) -> ColumnElement[bool]:
        return self.column > other

    def __ge__(self, other) -> ColumnElement[bool]:
        return self.column >= other

    @property
    def name(self) -> str | None:
        """Get field name

        Returns:
            Field name or None if not set
        """
        return self.column.name

    @property
    def type(self):
        """Get field type

        Returns:
            SQLAlchemy type instance
        """
        return self.column.type

    def _get_info_params(self, key: str) -> dict[str, Any]:
        """Get parameters from column info

        Args:
            key: Info key to retrieve

        Returns:
            Parameter dictionary or empty dict
        """
        return self.column.info.get(key, {}) if self.column.info else {}

    # Essential functionality parameter access
    @property
    def validators(self) -> list[Any]:
        """Field validators

        Returns:
            List of validator functions
        """
        return self._enhanced_params.get("validators", [])

    def get_default_factory(self) -> Callable[[], Any] | None:
        """Get default value factory function

        Returns:
            Default factory function or None
        """
        return self._enhanced_params.get("default_factory")

    def get_insert_default(self) -> Any:
        """Get insert-time default value

        Returns:
            Insert default value or None
        """
        return self._enhanced_params.get("insert_default")

    def has_insert_default(self) -> bool:
        """Check if field has insert default value

        Returns:
            True if insert default is set
        """
        return "insert_default" in self._enhanced_params

    def get_effective_default(self) -> Any:
        """Get effective default value (by priority)

        Priority: default > default_factory > insert_default

        Returns:
            Effective default value or None
        """
        # Priority: default > default_factory > insert_default
        if self.column.default is not None:
            return self.column.default

        default_factory = self.get_default_factory()
        if default_factory is not None:
            return default_factory

        insert_default = self.get_insert_default()
        if insert_default is not None:
            return insert_default

        return None

    def validate_value(self, value: Any, field_name: str) -> Any:
        """Validate field value using registered validators

        Args:
            value: Value to validate
            field_name: Name of the field being validated

        Returns:
            Validated value
        """
        validators = self.validators
        if validators:
            from .validators import validate_field_value

            return validate_field_value(validators, value, field_name)
        return value

    @property
    def is_deferred(self) -> bool:
        """Whether field is deferred loading

        Returns:
            True if field is deferred
        """
        return self._performance_params.get("deferred", False)

    # Experience enhancement parameter access
    @property
    def deferred_group(self) -> str | None:
        """Deferred loading group name

        Returns:
            Deferred group name or None
        """
        return self._performance_params.get("deferred_group")

    @property
    def include_in_init(self) -> bool | None:
        """Whether to include in __init__ method

        Returns:
            True/False or None for default behavior
        """
        return self._codegen_params.get("init")

    @property
    def include_in_repr(self) -> bool | None:
        """Whether to include in __repr__ method

        Returns:
            True/False or None for default behavior
        """
        return self._codegen_params.get("repr")

    @property
    def include_in_compare(self) -> bool | None:
        """Whether to use for comparison operations

        Returns:
            True/False or None for default behavior
        """
        return self._codegen_params.get("compare")

    @property
    def has_active_history(self) -> bool:
        """Whether active history tracking is enabled

        Returns:
            True if active history is enabled
        """
        return self._performance_params.get("active_history", False)

    @property
    def deferred_raiseload(self) -> bool | None:
        """Deferred loading exception handling

        Returns:
            True/False or None for default behavior
        """
        return self._performance_params.get("deferred_raiseload")

    @property
    def include_in_hash(self) -> bool | None:
        """Whether to use for hash calculation

        Returns:
            True/False or None for default behavior
        """
        return self._codegen_params.get("hash")

    @property
    def is_kw_only(self) -> bool | None:
        """Whether field is keyword-only parameter

        Returns:
            True/False or None for default behavior
        """
        return self._codegen_params.get("kw_only")

    # General parameter access methods
    def get_param(self, category: str, name: str, default: Any = None) -> Any:
        """Get parameter from specified category

        Args:
            category: Parameter category (enhanced, performance, codegen)
            name: Parameter name
            default: Default value if not found

        Returns:
            Parameter value or default
        """
        param_dict = getattr(self, f"_{category}_params", {})
        return param_dict.get(name, default)

    def get_codegen_params(self) -> dict[str, Any]:
        """Get code generation parameters

        Returns:
            Dictionary of code generation parameters
        """
        return self._codegen_params

    def get_field_metadata(self) -> dict[str, Any]:
        """Get complete field metadata information

        Returns:
            Dictionary containing all field metadata
        """
        metadata = {
            "name": self.name,
            "type": str(self.type),
            "nullable": getattr(self.column, "nullable", True),
            "primary_key": getattr(self.column, "primary_key", False),
            "unique": getattr(self.column, "unique", False),
            "index": getattr(self.column, "index", False),
        }

        # Add comments and documentation
        if hasattr(self.column, "comment") and self.column.comment:
            metadata["comment"] = self.column.comment
        if hasattr(self.column, "doc") and self.column.doc:
            metadata["doc"] = self.column.doc

        # Add extended parameters
        if self._enhanced_params:
            metadata["enhanced"] = self._enhanced_params
        if self._performance_params:
            metadata["performance"] = self._performance_params
        if self._codegen_params:
            metadata["codegen"] = self._codegen_params

        return metadata

    def __set_name__(self, owner: builtins.type[Any], name: str) -> None:
        """Proxy to column's __set_name__ method if it exists

        Args:
            owner: Owner class
            name: Attribute name
        """
        set_name_attr = getattr(self.column, "__set_name__", None)
        if set_name_attr is not None and callable(set_name_attr):
            set_name_attr(owner, name)


class Column(Generic[T]):
    """Field descriptor supporting type annotations and field access

    Provides a descriptor interface for SQLAlchemy columns with type safety
    and enhanced functionality.
    """

    def __init__(self, column: CoreColumn):  # noqa
        self.column = column
        self.name: str | None = None
        self._private_name: str | None = None

    def __set_name__(self, owner: type[Any], name: str) -> None:
        """Called when descriptor is assigned to class attribute

        Args:
            owner: Owner class
            name: Attribute name
        """
        self.name = name
        self._private_name = f"_{name}"

        # If column has no name, use field name
        if self.column.name is None:
            self.column.name = name

    @overload
    def __get__(self, instance: None, owner: type[Any]) -> "ColumnAttribute[TypeEngine[T]]": ...

    @overload
    def __get__(self, instance: Any, owner: type[Any]) -> T: ...

    def __get__(self, instance: Any, owner: type[Any]) -> Any:
        """Get field value

        Args:
            instance: Model instance or None for class access
            owner: Owner class

        Returns:
            ColumnAttribute for class access, field value for instance access
        """
        if instance is None:
            # Class access: return enhanced Column proxy for queries
            return ColumnAttribute(self.column, owner)
        else:
            # Instance access: return actual stored value
            if self._private_name is None:
                return None
            return getattr(instance, self._private_name, None)

    def __set__(self, instance: Any, value: T) -> None:
        """Set field value

        Args:
            instance: Model instance
            value: Value to set
        """
        if instance is None:
            raise AttributeError("Cannot set attribute on class")

        # Instance assignment: store to private attribute
        if self._private_name is not None:
            setattr(instance, self._private_name, value)

    def __delete__(self, instance: Any) -> None:
        """Delete field value

        Args:
            instance: Model instance
        """
        if instance is None:
            raise AttributeError("Cannot delete attribute on class")

        if self._private_name is not None and hasattr(instance, self._private_name):
            delattr(instance, self._private_name)


def _apply_codegen_defaults(codegen_params: dict, column_kwargs: dict) -> dict:
    """应用代码生成参数的智能默认值"""
    # 定义基于 ORM 字段特性的智能默认值
    defaults = {"init": True, "repr": True, "compare": False, "hash": None, "kw_only": False}

    # 主键字段：不参与初始化，但参与比较和显示
    if column_kwargs.get("primary_key"):
        defaults.update({"init": False, "repr": True, "compare": True})

    # 自增字段：只有当它是 True 时才不参与初始化（"auto" 不算）
    if column_kwargs.get("autoincrement") is True:  # noqa
        defaults["init"] = False

    # 服务器默认值字段：不参与初始化
    if column_kwargs.get("server_default") is not None:
        defaults["init"] = False

    # 只为未显式设置的参数应用默认值
    for key, default_value in defaults.items():
        if key not in codegen_params:
            codegen_params[key] = default_value

    return codegen_params


def column(
    *,
    type: str = "auto",  # noqa
    name: str | None = None,
    # SQLAlchemy Column parameters
    primary_key: bool = False,
    nullable: bool = True,
    default: Any = None,
    index: bool = False,
    unique: bool = False,
    autoincrement: str | bool = "auto",
    doc: str | None = None,
    key: str | None = None,
    onupdate: Any = None,
    comment: str | None = None,
    system: bool = False,
    server_default: Any = None,
    server_onupdate: Any = None,
    quote: bool | None = None,
    info: dict[str, Any] | None = None,
    # Essential functionality parameters
    default_factory: Callable[[], Any] | None = None,
    validators: list[Any] | None = None,
    deferred: bool = False,
    # Experience enhancement parameters
    deferred_group: str | None = None,
    insert_default: Any = None,
    init: bool | None = None,
    repr: bool | None = None,  # noqa
    compare: bool | None = None,
    # Advanced functionality parameters
    active_history: bool = False,
    deferred_raiseload: bool | None = None,
    hash: bool | None = None,  # noqa
    kw_only: bool | None = None,
    # Type parameters (passed through **kwargs)
    **kwargs: Any,
) -> "Column[Any]":
    """Create field descriptor with automatic type inference by default

    Args:
        type: Field type, defaults to "auto" for automatic inference
        name: Field name
        primary_key: Whether field is primary key
        nullable: Whether field allows NULL values
        default: Default value
        index: Whether to create index
        unique: Whether field is unique
        autoincrement: Auto-increment setting
        doc: Documentation string
        key: Field key name
        onupdate: Default value on update
        comment: Field comment
        system: Whether field is system field
        server_default: Server-side default value
        server_onupdate: Server-side update default
        quote: Whether to quote field name
        info: Additional info dictionary
        default_factory: Default value factory function
        validators: Field validator list
        deferred: Whether to defer loading
        deferred_group: Deferred loading group
        insert_default: Insert-time default value
        init: Whether to include in __init__
        repr: Whether to include in __repr__
        compare: Whether to use for comparison
        active_history: Whether to enable history tracking
        deferred_raiseload: Deferred loading exception handling
        hash: Whether to use for hash calculation
        kw_only: Whether keyword-only parameter
        **kwargs: Type-specific parameters (like length, precision, etc.)
    """
    # Prepare info dictionary to store extended parameters
    column_info = info.copy() if info else {}

    # Collect codegen parameters
    codegen_params = {}
    if init is not None:
        codegen_params["init"] = init
    if repr is not None:
        codegen_params["repr"] = repr
    if compare is not None:
        codegen_params["compare"] = compare
    if hash is not None:
        codegen_params["hash"] = hash
    if kw_only is not None:
        codegen_params["kw_only"] = kw_only

    # Build column kwargs for intelligent defaults
    column_kwargs = {
        "primary_key": primary_key,
        "autoincrement": autoincrement,
        "server_default": server_default,
    }

    # Apply intelligent defaults for codegen parameters
    codegen_params = _apply_codegen_defaults(codegen_params, column_kwargs)

    # Store parameters by category
    _store_performance_params(column_info, deferred, deferred_group, deferred_raiseload, active_history)
    _store_codegen_params(
        column_info,
        codegen_params.get("init"),
        codegen_params.get("repr"),
        codegen_params.get("compare"),
        codegen_params.get("hash"),
        codegen_params.get("kw_only"),
    )
    _store_enhanced_params(column_info, default_factory, insert_default, validators)

    # Handle default value logic
    final_default = _resolve_default_value(default, default_factory, insert_default)

    # Get type definition and parameters
    type_def = _registry.get_type(type)
    type_params = _extract_type_params(type_def, kwargs)

    # Create type instance
    type_instance = _registry.create_type_instance(type, type_params)

    # Build Column parameters
    column_params = {
        "primary_key": primary_key,
        "nullable": nullable,
        "default": final_default,
        "index": index,
        "unique": unique,
        "autoincrement": autoincrement,
        "doc": doc,
        "key": key,
        "onupdate": onupdate,
        "comment": comment,
        "system": system,
        "server_default": server_default,
        "server_onupdate": server_onupdate,
        "quote": quote,
        "info": column_info,
    }

    # Handle quote parameter - only pass if name is provided
    if quote is not None and name is None:
        # Remove quote parameter if no name is provided (SQLAlchemy requirement)
        column_params.pop("quote", None)

    # Remove None value parameters (except nullable and info)
    column_params = {k: v for k, v in column_params.items() if v is not None or k in ("nullable", "info")}

    # Create Core Column
    if name is not None:
        core_column = CoreColumn(name, type_instance, **column_params)
    else:
        core_column = CoreColumn(type_instance, **column_params)

    return Column(core_column)


# === Model Integration Utilities ===


def str_column(
    *,
    length: int | None = None,
    default_factory: Callable[[], Any] | None = None,
    validators: list[Any] | None = None,
    deferred: bool = False,
    deferred_group: str | None = None,
    insert_default: Any = None,
    init: bool | None = None,
    repr: bool | None = None,  # noqa
    compare: bool | None = None,
    primary_key: bool = False,
    nullable: bool = True,
    default: Any = None,
    index: bool = False,
    unique: bool = False,
    **kwargs: Any,
) -> "Column[Any]":
    """String field shortcut function

    Creates a string column with enhanced functionality and type safety.

    Args:
        length: Maximum string length
        default_factory: Default value factory function
        validators: Field validator list
        deferred: Whether to defer loading
        deferred_group: Deferred loading group
        insert_default: Insert-time default value
        init: Whether to include in __init__
        repr: Whether to include in __repr__
        compare: Whether to use for comparison
        primary_key: Whether field is primary key
        nullable: Whether field allows NULL values
        default: Default value
        index: Whether to create index
        unique: Whether field is unique
        **kwargs: Additional type-specific parameters

    Returns:
        Column descriptor for string field
    """
    return column(
        type="string",
        length=length,
        default_factory=default_factory,
        validators=validators,
        deferred=deferred,
        deferred_group=deferred_group,
        insert_default=insert_default,
        init=init,
        repr=repr,
        compare=compare,
        primary_key=primary_key,
        nullable=nullable,
        default=default,
        index=index,
        unique=unique,
        **kwargs,
    )


def int_column(
    *,
    default_factory: Callable[[], Any] | None = None,
    validators: list[Any] | None = None,
    deferred: bool = False,
    primary_key: bool = False,
    nullable: bool = True,
    default: Any = None,
    index: bool = False,
    unique: bool = False,
    **kwargs: Any,
) -> "Column[Any]":
    """Integer field shortcut function

    Creates an integer column with enhanced functionality and type safety.

    Args:
        default_factory: Default value factory function
        validators: Field validator list
        deferred: Whether to defer loading
        primary_key: Whether field is primary key
        nullable: Whether field allows NULL values
        default: Default value
        index: Whether to create index
        unique: Whether field is unique
        **kwargs: Additional type-specific parameters

    Returns:
        Column descriptor for integer field
    """
    return column(
        type="integer",
        default_factory=default_factory,
        validators=validators,
        deferred=deferred,
        primary_key=primary_key,
        nullable=nullable,
        default=default,
        index=index,
        unique=unique,
        **kwargs,
    )


def bool_column(
    *,
    default_factory: Callable[[], Any] | None = None,
    validators: list[Any] | None = None,
    deferred: bool = False,
    primary_key: bool = False,
    nullable: bool = True,
    default: Any = None,
    index: bool = False,
    unique: bool = False,
    **kwargs: Any,
) -> "Column[Any]":
    """Boolean field shortcut function

    Creates a boolean column with enhanced functionality and type safety.

    Args:
        default_factory: Default value factory function
        validators: Field validator list
        deferred: Whether to defer loading
        primary_key: Whether field is primary key
        nullable: Whether field allows NULL values
        default: Default value
        index: Whether to create index
        unique: Whether field is unique
        **kwargs: Additional type-specific parameters

    Returns:
        Column descriptor for boolean field
    """
    return column(
        type="boolean",
        default_factory=default_factory,
        validators=validators,
        deferred=deferred,
        primary_key=primary_key,
        nullable=nullable,
        default=default,
        index=index,
        unique=unique,
        **kwargs,
    )


def json_column(
    *,
    default_factory: Callable[[], Any] | None = None,
    validators: list[Any] | None = None,
    deferred: bool = False,
    primary_key: bool = False,
    nullable: bool = True,
    default: Any = None,
    index: bool = False,
    unique: bool = False,
    **kwargs: Any,
) -> "Column[Any]":
    """JSON field shortcut function

    Creates a JSON column with enhanced functionality and type safety.

    Args:
        default_factory: Default value factory function
        validators: Field validator list
        deferred: Whether to defer loading
        primary_key: Whether field is primary key
        nullable: Whether field allows NULL values
        default: Default value
        index: Whether to create index
        unique: Whether field is unique
        **kwargs: Additional type-specific parameters

    Returns:
        Column descriptor for JSON field
    """
    return column(
        type="json",
        default_factory=default_factory,
        validators=validators,
        deferred=deferred,
        primary_key=primary_key,
        nullable=nullable,
        default=default,
        index=index,
        unique=unique,
        **kwargs,
    )


def datetime_column(
    *,
    default_factory: Callable[[], Any] | None = None,
    validators: list[Any] | None = None,
    deferred: bool = False,
    deferred_group: str | None = None,
    insert_default: Any = None,
    init: bool | None = None,
    repr: bool | None = None,  # noqa
    compare: bool | None = None,
    primary_key: bool = False,
    nullable: bool = True,
    default: Any = None,
    index: bool = False,
    unique: bool = False,
    **kwargs: Any,
) -> "Column[Any]":
    """DateTime field shortcut function

    Creates a datetime column with enhanced functionality and type safety.

    Args:
        default_factory: Default value factory function
        validators: Field validator list
        deferred: Whether to defer loading
        deferred_group: Deferred loading group
        insert_default: Insert-time default value
        init: Whether to include in __init__
        repr: Whether to include in __repr__
        compare: Whether to use for comparison
        primary_key: Whether field is primary key
        nullable: Whether field allows NULL values
        default: Default value
        index: Whether to create index
        unique: Whether field is unique
        **kwargs: Additional type-specific parameters

    Returns:
        Column descriptor for datetime field
    """
    return column(
        type="datetime",
        default_factory=default_factory,
        validators=validators,
        deferred=deferred,
        deferred_group=deferred_group,
        insert_default=insert_default,
        init=init,
        repr=repr,
        compare=compare,
        primary_key=primary_key,
        nullable=nullable,
        default=default,
        index=index,
        unique=unique,
        **kwargs,
    )


def numeric_column(
    *,
    precision: int | None = None,
    scale: int | None = None,
    default_factory: Callable[[], Any] | None = None,
    validators: list[Any] | None = None,
    deferred: bool = False,
    deferred_group: str | None = None,
    insert_default: Any = None,
    init: bool | None = None,
    repr: bool | None = None,  # noqa
    compare: bool | None = None,
    primary_key: bool = False,
    nullable: bool = True,
    default: Any = None,
    index: bool = False,
    unique: bool = False,
    **kwargs: Any,
) -> "Column[Any]":
    """Numeric field shortcut function

    Creates a numeric/decimal column with enhanced functionality and type safety.

    Args:
        precision: Total number of digits
        scale: Number of digits after decimal point
        default_factory: Default value factory function
        validators: Field validator list
        deferred: Whether to defer loading
        deferred_group: Deferred loading group
        insert_default: Insert-time default value
        init: Whether to include in __init__
        repr: Whether to include in __repr__
        compare: Whether to use for comparison
        primary_key: Whether field is primary key
        nullable: Whether field allows NULL values
        default: Default value
        index: Whether to create index
        unique: Whether field is unique
        **kwargs: Additional type-specific parameters

    Returns:
        Column descriptor for numeric field
    """
    return column(
        type="numeric",
        precision=precision,
        scale=scale,
        default_factory=default_factory,
        validators=validators,
        deferred=deferred,
        deferred_group=deferred_group,
        insert_default=insert_default,
        init=init,
        repr=repr,
        compare=compare,
        primary_key=primary_key,
        nullable=nullable,
        default=default,
        index=index,
        unique=unique,
        **kwargs,
    )


def text_column(
    *,
    default_factory: Callable[[], Any] | None = None,
    validators: list[Any] | None = None,
    deferred: bool = False,
    deferred_group: str | None = None,
    insert_default: Any = None,
    init: bool | None = None,
    repr: bool | None = None,  # noqa
    compare: bool | None = None,
    active_history: bool = False,
    deferred_raiseload: bool | None = None,
    hash: bool | None = None,  # noqa
    kw_only: bool | None = None,
    primary_key: bool = False,
    nullable: bool = True,
    default: Any = None,
    index: bool = False,
    unique: bool = False,
    **kwargs: Any,
) -> "Column[Any]":
    """Text field shortcut function (supports all advanced features)

    Creates a text column with full advanced functionality support.

    Args:
        default_factory: Default value factory function
        validators: Field validator list
        deferred: Whether to defer loading
        deferred_group: Deferred loading group
        insert_default: Insert-time default value
        init: Whether to include in __init__
        repr: Whether to include in __repr__
        compare: Whether to use for comparison
        active_history: Whether to enable history tracking
        deferred_raiseload: Deferred loading exception handling
        hash: Whether to use for hash calculation
        kw_only: Whether keyword-only parameter
        primary_key: Whether field is primary key
        nullable: Whether field allows NULL values
        default: Default value
        index: Whether to create index
        unique: Whether field is unique
        **kwargs: Additional type-specific parameters

    Returns:
        Column descriptor for text field
    """
    return column(
        type="text",
        default_factory=default_factory,
        validators=validators,
        deferred=deferred,
        deferred_group=deferred_group,
        insert_default=insert_default,
        init=init,
        repr=repr,
        compare=compare,
        active_history=active_history,
        deferred_raiseload=deferred_raiseload,
        hash=hash,
        kw_only=kw_only,
        primary_key=primary_key,
        nullable=nullable,
        default=default,
        index=index,
        unique=unique,
        **kwargs,
    )


def binary_column(
    *,
    length: int | None = None,
    default_factory: Callable[[], Any] | None = None,
    validators: list[Any] | None = None,
    deferred: bool = False,
    deferred_group: str | None = None,
    insert_default: Any = None,
    init: bool | None = None,
    repr: bool | None = None,  # noqa
    compare: bool | None = None,
    active_history: bool = False,
    deferred_raiseload: bool | None = None,
    hash: bool | None = None,  # noqa
    kw_only: bool | None = None,
    primary_key: bool = False,
    nullable: bool = True,
    default: Any = None,
    index: bool = False,
    unique: bool = False,
    **kwargs: Any,
) -> "Column[Any]":
    """Binary field shortcut function (supports all advanced features)

    Creates a binary column with full advanced functionality support.

    Args:
        length: Maximum binary data length
        default_factory: Default value factory function
        validators: Field validator list
        deferred: Whether to defer loading
        deferred_group: Deferred loading group
        insert_default: Insert-time default value
        init: Whether to include in __init__
        repr: Whether to include in __repr__
        compare: Whether to use for comparison
        active_history: Whether to enable history tracking
        deferred_raiseload: Deferred loading exception handling
        hash: Whether to use for hash calculation
        kw_only: Whether keyword-only parameter
        primary_key: Whether field is primary key
        nullable: Whether field allows NULL values
        default: Default value
        index: Whether to create index
        unique: Whether field is unique
        **kwargs: Additional type-specific parameters

    Returns:
        Column descriptor for binary field
    """
    return column(
        type="binary",
        length=length,
        default_factory=default_factory,
        validators=validators,
        deferred=deferred,
        deferred_group=deferred_group,
        insert_default=insert_default,
        init=init,
        repr=repr,
        compare=compare,
        active_history=active_history,
        deferred_raiseload=deferred_raiseload,
        hash=hash,
        kw_only=kw_only,
        primary_key=primary_key,
        nullable=nullable,
        default=default,
        index=index,
        unique=unique,
        **kwargs,
    )


def _extract_type_params(type_def: TypeDefinition, kwargs: dict) -> dict:
    """Extract type construction parameters from kwargs

    Args:
        type_def: Type definition containing parameter specifications
        kwargs: Keyword arguments to filter

    Returns:
        Dictionary of type-specific parameters
    """
    type_param_names = {arg["name"] for arg in type_def["arguments"]}
    return {k: v for k, v in kwargs.items() if k in type_param_names}


def _store_performance_params(
    info: dict[str, Any],
    deferred: bool,
    deferred_group: str | None,
    deferred_raiseload: bool | None,
    active_history: bool,
) -> None:
    """Store performance optimization related parameters

    Args:
        info: Info dictionary to store parameters in
        deferred: Whether field is deferred
        deferred_group: Deferred loading group
        deferred_raiseload: Deferred loading exception handling
        active_history: Whether to enable active history
    """
    performance_params = info.setdefault("_performance", {})

    if deferred:
        performance_params["deferred"] = True
        if deferred_group is not None:
            performance_params["deferred_group"] = deferred_group
        if deferred_raiseload is not None:
            performance_params["deferred_raiseload"] = deferred_raiseload

    if active_history:
        performance_params["active_history"] = True


def _store_codegen_params(
    info: dict[str, Any],
    init: bool | None,
    repr: bool | None,  # noqa
    compare: bool | None,
    hash: bool | None,  # noqa
    kw_only: bool | None,
) -> None:
    """Store code generation related parameters

    Args:
        info: Info dictionary to store parameters in
        init: Whether to include in __init__
        repr: Whether to include in __repr__
        compare: Whether to use for comparison
        hash: Whether to use for hash calculation
        kw_only: Whether keyword-only parameter
    """
    codegen_params = info.setdefault("_codegen", {})

    if init is not None:
        codegen_params["init"] = init
    if repr is not None:
        codegen_params["repr"] = repr
    if compare is not None:
        codegen_params["compare"] = compare
    if hash is not None:
        codegen_params["hash"] = hash
    if kw_only is not None:
        codegen_params["kw_only"] = kw_only


def _store_enhanced_params(
    info: dict[str, Any],
    default_factory: Callable[[], Any] | None,
    insert_default: Any,
    validators: list[Any] | None,
) -> None:
    """Store functionality enhancement related parameters

    Args:
        info: Info dictionary to store parameters in
        default_factory: Default value factory function
        insert_default: Insert-time default value
        validators: Field validator list
    """
    enhanced_params = info.setdefault("_enhanced", {})

    if default_factory is not None:
        enhanced_params["default_factory"] = default_factory
    if insert_default is not None:
        enhanced_params["insert_default"] = insert_default
    if validators is not None:
        enhanced_params["validators"] = validators


def _resolve_default_value(
    default: Any,
    default_factory: Callable[[], Any] | None,
    insert_default: Any,
) -> Any:
    """Resolve default value priority: default > default_factory > insert_default

    Args:
        default: Direct default value
        default_factory: Default value factory function
        insert_default: Insert-time default value

    Returns:
        Resolved default value or None
    """
    if default is not None:
        return default

    if default_factory is not None:
        # Wrap as SQLAlchemy compatible callable
        return lambda: default_factory()

    if insert_default is not None:
        # Support SQLAlchemy function expressions
        return insert_default

    return None


# === Validation and Metadata Utilities ===


def get_field_validators(model_class: type, field_name: str) -> list[Any]:
    """Get validator list for specified field

    Args:
        model_class: Model class to inspect
        field_name: Name of the field

    Returns:
        List of validator functions for the field
    """
    if hasattr(model_class, "_field_validators"):
        return model_class._field_validators.get(field_name, [])  # noqa
    return []


def get_model_metadata(model_class: type) -> dict[str, Any]:
    """Get complete metadata information for model

    Args:
        model_class: Model class to inspect

    Returns:
        Dictionary containing complete model metadata
    """
    metadata = {
        "model_name": model_class.__name__,
        "table_name": getattr(model_class.__table__, "name", None) if hasattr(model_class, "__table__") else None,
        "fields": {},
        "validators": getattr(model_class, "_field_validators", {}),
    }

    # Collect field metadata
    for name in dir(model_class):
        if name.startswith("_"):
            continue
        try:
            attr = getattr(model_class, name)
            if hasattr(attr, "get_field_metadata"):
                metadata["fields"][name] = attr.get_field_metadata()
        except Exception:  # noqa
            continue

    # Add model configuration information
    if hasattr(model_class, "Config"):
        config_attrs = {}
        config_class = model_class.Config
        for attr_name in dir(config_class):
            if not attr_name.startswith("_") and not callable(getattr(config_class, attr_name, None)):
                try:
                    value = getattr(config_class, attr_name)
                    if not callable(value):
                        config_attrs[attr_name] = (
                            str(value) if hasattr(value, "__iter__") and not isinstance(value, str | bytes) else value
                        )
                except Exception:  # noqa
                    continue
        if config_attrs:
            metadata["config"] = config_attrs

    return metadata

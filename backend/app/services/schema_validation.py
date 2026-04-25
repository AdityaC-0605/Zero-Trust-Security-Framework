from functools import wraps
from flask import request, jsonify
from pydantic import BaseModel, ValidationError
import bleach
import shlex

class SchemaValidator:
    @staticmethod
    def validate_schema(schema_class: type[BaseModel]):
        def decorator(f):
            @wraps(f)
            def decorated_function(*args, **kwargs):
                data = request.get_json(silent=True) or {}
                try:
                    schema_class(**data)
                except ValidationError as e:
                    return jsonify({"error": "Schema validation failed", "details": e.errors()}), 400
                return f(*args, **kwargs)
            return decorated_function
        return decorator

    @staticmethod
    def sanitize_input(val: str) -> str:
        """Sanitize string inputs using bleach (HTML) and shlex.quote (shell)"""
        if not isinstance(val, str):
            return val
        clean_html = bleach.clean(val)
        clean_shell = shlex.quote(clean_html)
        if clean_shell.startswith("'") and clean_shell.endswith("'"):
            clean_shell = clean_shell[1:-1]
        return clean_shell

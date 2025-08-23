import hashlib
import json
from pydantic import BaseModel, model_validator

class Config(BaseModel):
    model_config = {
        "validate_assignment": True
    }

    @model_validator(mode="after")
    def strict_type_check(cls, values):
        def check_field(name, value, expected_type):

            if isinstance(expected_type, type) and not isinstance(value, expected_type):
                raise TypeError(
                    f"Invalid value for '{name}': expected {expected_type.__name__}, got {type(value).__name__}"
                )

            # Nested BaseModel
            if isinstance(value, BaseModel):
                for sub_name, sub_value in value.model_dump().items():
                    sub_type = value.model_fields[sub_name].annotation
                    check_field(f"{name}.{sub_name}", sub_value, sub_type)

        for field_name, value in values.__dict__.items():
            expected_type = cls.model_fields[field_name].annotation
            check_field(field_name, value, expected_type)

        return values



    def write_to_json_file(self, file_path: str) -> None:
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(self.model_dump_json(indent=2))
            print(f"Successfully wrote config to {file_path}")
        except Exception as e:
            print("Error writing file:", e)

    def stable_config_hash(self) -> str:
        data = self.parameter.model_dump()
        json_repr = json.dumps(data, sort_keys=True, default=str)
        return hashlib.sha256(bytes(json_repr, "utf-8")).hexdigest()

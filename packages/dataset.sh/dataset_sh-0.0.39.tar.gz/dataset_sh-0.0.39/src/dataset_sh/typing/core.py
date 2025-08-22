from typing import Union, Optional, List

# import easytype.core as etc  # Deprecated - using Typelang now
from pydantic import BaseModel


class EnumEntry(BaseModel):
    name: str
    value: str


class FieldType(BaseModel):
    is_parametric: bool
    name: str
    children: Optional[List['FieldType']] = None

    @staticmethod
    def simple(name):
        return FieldType(is_parametric=False, name=name)

    @staticmethod
    def typed(name, children):
        return FieldType(is_parametric=True, name=name, children=children)

    def to_new_type_system(self):
        # Deprecated - using Typelang now
        raise NotImplementedError("This method is deprecated. Use Typelang instead.")

    def get_types_to_build(self) -> List[str]:
        pass


class PydanticFieldDefinition(BaseModel):
    name: str
    type: FieldType

    def to_new_type_system(self):
        # Deprecated - using Typelang now
        raise NotImplementedError("This method is deprecated. Use Typelang instead.")

    def get_types_to_build(self) -> List[str]:
        pass


class EnumDefinition(BaseModel):
    name: str
    enum_entries: Optional[List[EnumEntry]]
    doc_str: Optional[str] = None

    def is_int(self):
        if self.enum_entries is not None and len(self.enum_entries) > 0:
            return isinstance(self.enum_entries[0].value, int)
        return False

    def to_new_type_system(self):
        # Deprecated - using Typelang now
        raise NotImplementedError("This method is deprecated. Use Typelang instead.")

    def get_types_to_build(self) -> List[str]:
        pass


class ClassDefinition(BaseModel):
    name: str
    fields: List[PydanticFieldDefinition]
    doc_str: Optional[str] = None

    def to_new_type_system(self):
        # Deprecated - using Typelang now
        raise NotImplementedError("This method is deprecated. Use Typelang instead.")

    def get_types_to_build(self) -> List[str]:
        pass


class DatasetSchema(BaseModel):
    entry_point: str
    classes: List[Union[EnumDefinition, ClassDefinition]]

    def to_new_type_system(self):
        # Deprecated - using Typelang now
        raise NotImplementedError("This method is deprecated. Use Typelang instead.")

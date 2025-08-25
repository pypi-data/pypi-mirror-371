#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Pydantic models for RCK API requests and responses.
"""
from __future__ import annotations
import json
import inspect
from enum import Enum
from pydantic import BaseModel, Field, ConfigDict, model_validator
from typing import Optional, List, Dict, Any, Union, Type, Generic, TypeVar

# --- Base Models ---

class EndpointModel(BaseModel):
    """
    Base model for defining structured outputs (endpoint classes).
    Users can subclass this to define their desired output structure.
    """
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    @classmethod
    def to_json_schema_dict(cls) -> Dict[str, Any]:
        """Returns the Pydantic model as a JSON Schema dictionary."""
        return cls.model_json_schema()

    @classmethod
    def to_json_schema_str(cls) -> str:
        """Serializes the Pydantic model to a JSON Schema string."""
        return json.dumps(cls.model_json_schema(), ensure_ascii=False)

# --- Config Models ---

class EngineEnum(str, Enum):
    STANDARD = "standard"
    ATTRACTOR = "attractor"
    IMAGE = "image"
    PURE = "pure"
    LOCAL_STANDARD = "local_standard"
    LOCAL_PURE = "local_pure"

class SpeedEnum(str, Enum):
    FAST = "fast"
    BALANCED = "balanced"
    QUALITY = "quality"
    LOCAL_FAST = "local_fast"
    LOCAL_BALANCED = "local_balanced"

class ScaleEnum(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

class RCKConfig(BaseModel):
    """RCK API Configuration Model."""
    engine: Optional[EngineEnum] = None
    speed: Optional[SpeedEnum] = None
    scale: Optional[ScaleEnum] = None
    temperature: Optional[float] = Field(None, ge=0.0, le=1.0)
    base_url: str = "https://rck-aehhddpisa.us-west-1.fcapp.run"
    api_key: Optional[str] = None

# --- Program Component Models ---

class Resource(BaseModel):
    key: str

class StartPoint(BaseModel):
    startPoint: str
    resource: Optional[List[Resource]] = None

# --- Path Models ---

class BasePath(BaseModel):
    """Base model for Path."""
    pathName: Optional[str] = None
    customFields: Optional[Dict[str, Any]] = None

    @model_validator(mode='before')
    @classmethod
    def _stringify_custom_fields_values(cls, data: Any) -> Any:
        if isinstance(data, dict):
            custom_fields = data.get('customFields')
            if isinstance(custom_fields, dict):
                for key, value in custom_fields.items():
                    if not isinstance(value, str):
                        custom_fields[key] = json.dumps(value, ensure_ascii=False)
        return data

class StandardPath(BasePath):
    endpointClass: Union[str, Dict[str, Any], Type[EndpointModel]]
    expectPath: str

class PurePath(BasePath):
    endpointClass: str
    expectPath: str

class ImagePath(BaseModel):
    frame_Composition: str = Field(..., alias="frame_Composition")
    lighting: str
    style: str

# --- Intuitive Attractor Models ---

AttractorInputBase = BaseModel
AttractorOutputBase = EndpointModel

class AttractorExample:
    def __init__(self, input: AttractorInputBase, output: AttractorOutputBase):
        if not isinstance(input, AttractorInputBase):
            raise TypeError("The 'input' must be an instance of AttractorInputBase.")
        if not isinstance(output, AttractorOutputBase):
            raise TypeError("The 'output' must be an instance of AttractorOutputBase.")
        self.input = input
        self.output = output

class AttractorPath:
    def __init__(self,
                 examples: List[AttractorExample],
                 pathName: Optional[str] = None,
                 customFields: Optional[Dict[str, Any]] = None):
        if not examples:
            raise ValueError("The 'examples' list cannot be empty.")
        self.pathName = pathName
        self.examples = examples
        self.customFields = customFields
        self._input_type = type(examples[0].input)
        self._output_type = type(examples[0].output)
        for ex in examples[1:]:
            if type(ex.input) is not self._input_type or type(ex.output) is not self._output_type:
                raise TypeError("All examples must use the same input and output model types.")

# --- Program Builders ---

class BaseProgram(BaseModel):
    start_point: StartPoint
    config: RCKConfig
    path: Any  # The specific path object
    model_config = ConfigDict(arbitrary_types_allowed=True)

    def get_path_payload(self) -> Dict[str, Any]:
        raise NotImplementedError

class StandardProgram(BaseProgram):
    path: StandardPath
    def __init__(self, start_point: StartPoint, path: StandardPath, **config_kwargs):
        config_kwargs.setdefault('engine', EngineEnum.STANDARD)
        cfg = RCKConfig(**config_kwargs)
        super().__init__(start_point=start_point, path=path, config=cfg)
    
    def get_path_payload(self) -> Dict[str, Any]:
        payload = self.path.model_dump(by_alias=True, exclude_none=True)
        schema_obj = self.path.endpointClass
        if inspect.isclass(schema_obj) and issubclass(schema_obj, EndpointModel):
            payload['endpointClass'] = schema_obj.to_json_schema_str()
        elif isinstance(schema_obj, dict):
            payload['endpointClass'] = json.dumps(schema_obj, ensure_ascii=False)
        return payload

class PureProgram(BaseProgram):
    path: PurePath
    def __init__(self, start_point: StartPoint, path: PurePath, **config_kwargs):
        config_kwargs.setdefault('engine', EngineEnum.PURE)
        cfg = RCKConfig(**config_kwargs)
        super().__init__(start_point=start_point, path=path, config=cfg)
    
    def get_path_payload(self) -> Dict[str, Any]:
        return self.path.model_dump(by_alias=True, exclude_none=True)

class AttractorProgram(BaseProgram):
    path: AttractorPath
    def __init__(self, start_point: StartPoint, path: AttractorPath, **config_kwargs):
        try:
            path._input_type.model_validate_json(start_point.startPoint)
        except Exception as e:
            raise ValueError(f"start_point is not valid for input model '{path._input_type.__name__}': {e}") from e
        config_kwargs.setdefault('engine', EngineEnum.ATTRACTOR)
        cfg = RCKConfig(**config_kwargs)
        super().__init__(start_point=start_point, path=path, config=cfg)

    def get_path_payload(self) -> Dict[str, Any]:
        serialized_examples = [{
            "initial_state": ex.input.model_dump_json(by_alias=True),
            "final_state": ex.output.model_dump_json(by_alias=True)
        } for ex in self.path.examples]
        payload = {"state_examples": serialized_examples}
        if self.path.pathName: payload["pathName"] = self.path.pathName
        if self.path.customFields: payload["customFields"] = self.path.customFields
        return payload

class ImageProgram(BaseProgram):
    path: ImagePath
    def __init__(self, start_point: StartPoint, path: ImagePath, **config_kwargs):
        config_kwargs.setdefault('engine', EngineEnum.IMAGE)
        cfg = RCKConfig(**config_kwargs)
        super().__init__(start_point=start_point, path=path, config=cfg)

    def get_path_payload(self) -> Dict[str, Any]:
        return self.path.model_dump(by_alias=True, exclude_none=True)

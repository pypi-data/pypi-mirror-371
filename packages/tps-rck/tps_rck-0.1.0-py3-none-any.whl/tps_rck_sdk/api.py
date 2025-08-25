#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RCK SDK High-Level API.
Provides simplified, user-friendly functions for common RCK operations.
"""
from typing import Type, TypeVar, Optional, Dict, Any, List, Tuple
from pydantic import BaseModel
import json

from .config import get_client
from .exceptions import RCKAPIError
from .model import (
    EndpointModel, StartPoint, Resource,
    StandardPath, StandardProgram,
    PurePath, PureProgram,
    AttractorPath, AttractorProgram, AttractorExample, AttractorInputBase, AttractorOutputBase,
    ImagePath, ImageProgram
)

T = TypeVar("T", bound=EndpointModel)
InputT = TypeVar("InputT", bound=AttractorInputBase)
OutputT = TypeVar("OutputT", bound=EndpointModel)


def structured_transform(
    start_point: str,
    output_schema: Type[T],
    instructions: str,
    resources: Optional[List[Dict]] = None,
    config_overrides: Optional[Dict[str, Any]] = None,
    custom_fields: Optional[Dict[str, Any]] = None,
    timeout: Optional[float] = None,
) -> T:
    """
    Transforms unstructured text into a structured Pydantic object. (Standard Engine)

    Args:
        start_point: The input text to transform.
        output_schema: The Pydantic class (subclass of EndpointModel) to structure the output into.
        instructions: Natural language instructions for the transformation.
        resources: Optional list of resources associated with the start point.
        config_overrides: A dictionary to override global config settings for this call (e.g., speed, temperature).
        custom_fields: Optional custom fields to pass to the RCK path.
        timeout: Optional request timeout in seconds for this specific call.

    Returns:
        An instance of the provided Pydantic output_schema class.
        
    Raises:
        RCKAPIError: If the API call fails or the response cannot be parsed.
    """
    client = get_client()
    
    sp = StartPoint(startPoint=start_point, resource=resources)
    
    path = StandardPath(
        endpointClass=output_schema,
        expectPath=instructions,
        customFields=custom_fields
    )
    
    program = StandardProgram(start_point=sp, path=path, **(config_overrides or {}))
    
    response = client.unified_compute(program, timeout=timeout)
    
    if not response.success or not response.text:
        raise RCKAPIError(f"API call failed: {response.text or 'No response text'}", response_body=response.raw)
        
    try:
        data = json.loads(response.text)
        if isinstance(data, dict) and output_schema.__name__ in data:
            return output_schema.model_validate(data[output_schema.__name__])
        return output_schema.model_validate(data)
    except json.JSONDecodeError:
        raise RCKAPIError(f"Failed to parse API JSON response: {response.text}", response_body=response.raw)


def learn_from_examples(
    start_point: InputT,
    output_schema: Type[OutputT],
    examples: List[Tuple[InputT, OutputT]],
    config_overrides: Optional[Dict[str, Any]] = None,
    custom_fields: Optional[Dict[str, Any]] = None,
    path_name: Optional[str] = None,
    timeout: Optional[float] = None,
) -> OutputT:
    """
    Transforms data by learning from examples. (Attractor Engine)

    Args:
        start_point: An instance of the input Pydantic model.
        output_schema: The Pydantic class for the output.
        examples: A list of (input_model, output_model) tuples.
        config_overrides: A dictionary to override global config settings.
        custom_fields: Optional custom fields for the RCK path.
        path_name: Optional name for the RCK path.
        timeout: Optional request timeout in seconds for this specific call.

    Returns:
        An instance of the provided Pydantic output_schema class.
    """
    client = get_client()

    sp = StartPoint(startPoint=start_point.model_dump_json())
    attractor_examples = [AttractorExample(input=ex_in, output=ex_out) for ex_in, ex_out in examples]

    path = AttractorPath(
        examples=attractor_examples,
        pathName=path_name,
        customFields=custom_fields
    )

    program = AttractorProgram(start_point=sp, path=path, **(config_overrides or {}))
    response = client.unified_compute(program, timeout=timeout)

    if not response.success or not response.text:
        raise RCKAPIError(f"API call failed: {response.text or 'No response text'}", response_body=response.raw)

    try:
        data = json.loads(response.text)
        if isinstance(data, dict) and output_schema.__name__ in data:
            return output_schema.model_validate(data[output_schema.__name__])
        return output_schema.model_validate(data)
    except json.JSONDecodeError:
        raise RCKAPIError(f"Failed to parse API JSON response: {response.text}", response_body=response.raw)


def generate_text(
    start_point: str,
    instructions: str,
    context: str = "Generate a textual response based on the start point and instructions.",
    resources: Optional[List[Dict]] = None,
    config_overrides: Optional[Dict[str, Any]] = None,
    custom_fields: Optional[Dict[str, Any]] = None,
    timeout: Optional[float] = None,
) -> str:
    """
    Generates free-form text. (Pure Engine)

    Args:
        start_point: The input text or prompt.
        instructions: The primary instruction for what to generate (e.g., 'Generate Python code').
        context: Broader context for the generation task.
        resources: Optional list of associated resources.
        config_overrides: A dictionary to override global config settings.
        custom_fields: Optional custom fields for the RCK path.
        timeout: Optional request timeout in seconds for this specific call.

    Returns:
        The generated text as a string.
    """
    client = get_client()
    
    cfg_overrides = config_overrides or {}
    cfg_overrides.setdefault('engine', 'pure')

    sp = StartPoint(startPoint=start_point, resource=resources)

    path = PurePath(
        endpointClass=instructions,
        expectPath=context,
        customFields=custom_fields
    )

    program = PureProgram(start_point=sp, path=path, **cfg_overrides)
    response = client.unified_compute(program, timeout=timeout)

    if not response.success:
        raise RCKAPIError(f"API call failed: {response.text or 'No response'}", response_body=response.raw)

    return response.text


class ImageDetails(BaseModel):
    """Details of a single generated image."""
    mimeType: str
    imageData: str  # base64 encoded string
    index: int
    size: int


class ImageResponse(BaseModel):
    """The response structure for an image generation request."""
    images: List[ImageDetails]
    count: int


def generate_image(
    subject: str,
    composition: str,
    lighting: str,
    style: str,
    config_overrides: Optional[Dict[str, Any]] = None,
    timeout: Optional[float] = None,
) -> ImageResponse:
    """
    Generates an image from a structured description. (Image Engine)

    Args:
        subject: The main subject or concept of the image.
        composition: Description of the camera angle, framing, etc.
        lighting: Description of the lighting conditions.
        style: The artistic style of the image.
        config_overrides: A dictionary to override global config settings.
        timeout: Optional request timeout in seconds for this specific call.

    Returns:
        An ImageResponse object containing the image data.
    """
    client = get_client()
    
    cfg_overrides = config_overrides or {}
    cfg_overrides['engine'] = 'image'

    sp = StartPoint(startPoint=subject)

    path = ImagePath(
        frame_Composition=composition,
        lighting=lighting,
        style=style
    )

    program = ImageProgram(start_point=sp, path=path, **cfg_overrides)
    response = client.unified_compute(program, timeout=timeout)

    if not response.success or not response.raw.get("end_point"):
        raise RCKAPIError(f"API call failed or returned invalid image data", response_body=response.raw)

    end_point_data = response.raw.get("end_point")
    if not end_point_data:
        raise RCKAPIError(f"Invalid image response format. 'end_point' not found in: {response.raw}", response_body=response.raw)
        
    return ImageResponse.model_validate(end_point_data)

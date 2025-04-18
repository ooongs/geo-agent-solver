"""
GeoGebra Command Schemas Module

This module defines pydantic schemas for GeoGebra command generation tools.
These schemas represent the input data structures for various geometric commands
like points, lines, circles, angles, and measurements.
"""

from typing import Dict, Any, List, Optional, Union
from pydantic import BaseModel, Field



class RetrieveGeoGebraCommandInput(BaseModel):
    """Schema for input to retrieve GeoGebra commands from database."""
    query: str = Field(
        description="The GeoGebra command name or query to search for (e.g., 'Segment', 'Point', 'Circle')."
    )
    top_k: int = Field(
        default=3,
        description="Number of command examples to retrieve (default: 3)."
    )


# class GenerateGeoGebraCommandInput(BaseModel):
#     """Schema for generating any type of GeoGebra command."""
#     command_type: str = Field(
#         description="Type of command to generate (point, line, circle, angle, polygon, measurement, etc.)"
#     )
#     parameters: Dict[str, Any] = Field(
#         description="Parameters needed for command generation, varies by command_type",
#         default={}
#     )
#     description: Optional[str] = Field(
#         description="Optional description of what this command should accomplish",
#         default=None
#     ) 
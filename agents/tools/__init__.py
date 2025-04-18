"""
Common tools for all agents in the geo-solver system.

This module provides shared tools that can be used by multiple agents,
including validation agent, command generation agent, and command regeneration agent.
"""

from langchain.tools import StructuredTool
from typing import List

from agents.schemas.geogebra_command_schemas import RetrieveGeoGebraCommandInput
from agents.wrappers.geogebra_command_wrappers import retrieve_geogebra_command_wrapper


def get_common_tools() -> List[StructuredTool]:
    """
    공통으로 사용할 수 있는 도구 목록을 반환합니다.
    
    Returns:
        도구 목록 (StructuredTool 형태)
    """
    tools = [
        StructuredTool.from_function(
            func=retrieve_geogebra_command_wrapper,
            name="retrieve_geogebra_command",
            description="Retrieve information about GeoGebra commands from the vector database. Use this when you want to know the exact syntax and examples of a command.",
            args_schema=RetrieveGeoGebraCommandInput,
            coroutine=retrieve_geogebra_command_wrapper,
            handle_tool_error=True
        ),

    ]
    
    return tools 

#         StructuredTool.from_function(
#             func=generate_geogebra_command_wrapper,
#             name="generate_geogebra_command",
#             description="""Generate any type of GeoGebra command based on command_type and parameters.
            
# Examples:
# 1. Point: 
#    command_type: "point", 
#    parameters: {"name": "A", "x": 1, "y": 2}
   
# 2. Line: 
#    command_type: "line", 
#    parameters: {"name": "a", "point1": "A", "point2": "B"}
   
# 3. Circle: 
#    command_type: "circle", 
#    parameters: {"name": "c", "center": "A", "radius": 3}
   
# 4. Angle: 
#    command_type: "angle", 
#    parameters: {"name": "α", "points": ["A", "B", "C"]}
   
# 5. Polygon: 
#    command_type: "polygon", 
#    parameters: {"name": "poly", "vertices": ["A", "B", "C", "D"]}
   
# 6. Measurement: 
#    command_type: "measurement", 
#    parameters: {"name": "d", "measure_type": "distance", "objects": ["A", "B"]}
#             """,
#             args_schema=GenerateGeoGebraCommandInput,
#             handle_tool_error=True
#         )
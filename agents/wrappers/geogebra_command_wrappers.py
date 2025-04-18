"""
GeoGebra Command Wrappers Module

This module provides wrapper functions for GeoGebra command generation tools.
These wrappers accept pydantic schema inputs and handle the conversion between
schema objects and the expected input format for the underlying tools.
"""

import json
from langchain_core.tools import ToolException
from db.retrieval import CommandRetrieval

from ..schemas.geogebra_command_schemas import (
    RetrieveGeoGebraCommandInput,
)




def retrieve_geogebra_command_wrapper(query: str, top_k: int = 3) -> str:
    """
    벡터 DB에서 GeoGebra 명령어 검색
    
    Args:
        input_data: 도구 입력 데이터 (query: 검색할 명령어명, top_k: 검색 결과 수)
        
    Returns:
        관련 명령어 정보를 JSON 형식으로 반환
    """
    try:
        # CommandRetrieval 인스턴스 생성
        retriever = CommandRetrieval()
        
        # 명령어 기반 검색 수행 (정확한 명령어 이름으로 검색)
        commands = retriever.search_commands_by_command(query, top_k=top_k)
        
        # 정확한 명령어가 없는 경우 코사인 유사도 검색 수행
        if not commands:
            commands = retriever.cosine_search(query, top_k=top_k)
        
        # 필요한 속성만 포함하도록 결과 필터링
        filtered_commands = []
        for cmd in commands:
            filtered_commands.append({
                "command": cmd.get("command", ""),
                "syntax": cmd.get("syntax", ""),
                "description": cmd.get("description", ""),
                "examples": cmd.get("examples", ""),
                "note": cmd.get("note", "")
            })
        
        return json.dumps({"commands": filtered_commands})
    
    except Exception as e:
        raise ToolException(f"Error retrieving GeoGebra commands: {str(e)}")


# def generate_geogebra_command_wrapper(input_data: GenerateGeoGebraCommandInput) -> str:
#     """
#     범용 GeoGebra 명령어 생성 래퍼
    
#     Args:
#         input_data: 명령어 생성에 필요한 정보 (command_type, parameters, description)
        
#     Returns:
#         String containing GeoGebra commands
        
#     Raises:
#         ToolException: If there's an error generating the commands
#     """
#     try:
#         command_type = input_data.command_type.lower()
#         params = input_data.parameters
        
#         # 명령어 유형에 따른 처리
#         if command_type == 'point':
#             # 점 명령어 생성
#             name = params.get('name', 'A')
#             x = params.get('x', 0)
#             y = params.get('y', 0)
            
#             if 'coordinates' in params:
#                 coords = params['coordinates']
#                 if isinstance(coords, (list, tuple)) and len(coords) >= 2:
#                     x, y = coords[0], coords[1]
            
#             return f"{name} = ({x}, {y})"
            
#         elif command_type == 'line':
#             # 선 명령어 생성
#             name = params.get('name', 'a')
#             point1 = params.get('point1', 'A')
#             point2 = params.get('point2', 'B')
            
#             return f"{name} = Line({point1}, {point2})"
            
#         elif command_type == 'segment':
#             # 선분 명령어 생성
#             name = params.get('name', 'a')
#             point1 = params.get('point1', 'A')
#             point2 = params.get('point2', 'B')
            
#             return f"{name} = Segment({point1}, {point2})"
            
#         elif command_type == 'circle':
#             # 원 명령어 생성
#             name = params.get('name', 'c')
#             center = params.get('center', 'A')
            
#             if 'radius' in params:
#                 radius = params['radius']
#                 return f"{name} = Circle({center}, {radius})"
#             elif 'point' in params:
#                 point = params['point']
#                 return f"{name} = Circle({center}, {point})"
#             else:
#                 return f"{name} = Circle({center}, 1)"
                
#         elif command_type == 'angle':
#             # 각도 명령어 생성
#             name = params.get('name', 'α')
#             points = params.get('points', ['A', 'B', 'C'])
            
#             if len(points) >= 3:
#                 return f"{name} = Angle({points[0]}, {points[1]}, {points[2]})"
#             else:
#                 return f"{name} = Angle({', '.join(points)})"
                
#         elif command_type == 'polygon':
#             # 다각형 명령어 생성
#             name = params.get('name', 'poly')
#             vertices = params.get('vertices', ['A', 'B', 'C'])
            
#             return f"{name} = Polygon({', '.join(vertices)})"
            
#         elif command_type == 'measurement':
#             # 측정 명령어 생성
#             name = params.get('name', 'm')
#             measure_type = params.get('measure_type', 'distance')
#             objects = params.get('objects', ['A', 'B'])
            
#             if measure_type == 'distance':
#                 return f"{name} = Distance({', '.join(objects)})"
#             elif measure_type == 'area':
#                 return f"{name} = Area({objects[0]})"
#             elif measure_type == 'length':
#                 return f"{name} = Length({objects[0]})"
#             else:
#                 return f"{name} = {measure_type.capitalize()}({', '.join(objects)})"
                
#         else:
#             return f"Command type '{command_type}' not supported"
            
#     except Exception as e:
#         raise ToolException(f"Error generating GeoGebra command: {str(e)}") 
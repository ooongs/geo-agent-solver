"""
JSON 템플릿 모듈

이 모듈은 여러 프롬프트에서 공통으로 사용하는 JSON 템플릿을 정의합니다.
"""

# 플래너 JSON 템플릿 (언어별 제공되는 템플릿의 통합 버전)
PLANNER_CALCULATION_JSON_TEMPLATE = '''
{
  "requires_calculation": true,
  "reasoning": "Explain why construction is insufficient and which advanced calculations are required.",
  "suggested_tasks_reasoning": "Detailed reasoning for each required operation.",
  "suggested_tasks": [
    {
      "task_type": "angle",
      "operation_type": "angle_bisector",
      "parameters": {
        "point1": "E",
        "point2": "A",
        "point3": "B"
      },
      "dependencies": [],
      "description": "Divide angle EAB into three equal parts",
      "geogebra_alternatives": true,
      "geogebra_command": "AngleBisector[E, A, B]"
    }
  ]
}
'''

PLANNER_NO_CALCULATION_JSON_TEMPLATE = '''
{
  "requires_calculation": false,
  "reasoning": "Explain why all operations can be performed with ruler and compass (or GeoGebra).",
  "construction_plan": {
    "title": "Construction plan title",
    "description": "Overall strategy description",
    "steps": [
      {
        "step_id": "step_1",
        "description": "Construct equilateral triangle ABC",
        "task_type": "triangle",
        "operation_type": "polygon",
        "geometric_elements": ["A", "B", "C"],
        "command_type": "Polygon",
        "parameters": {
          "points": ["A", "B", "C"]
        },
        "geogebra_alternatives": true,
        "geogebra_command": "Polygon[A, B, C]"
      }
    ],
    "final_result": "Expected final result"
  }
}
'''

COMMAND_SELECTION_TEMPLATE = '''
{
  "selected_commands": [
    {"step_id": <Step ID>, "command_id": <Command ID>, "reason": "<Selection reason>", "command_syntax": "<Command syntax>"},
    {"step_id": <Step ID>, "command_id": <Command ID>, "reason": "<Selection reason>", "command_syntax": "<Command syntax>"},
    ...
  ]
}
'''

COMMAND_GENERATION_TEMPLATE ='''
{
  "commands": [ "GeoGebra command 1", "GeoGebra command 2", ... ],
  "explanation": "Explanation of command generation (1. Explanation of the first command,\n 2. Explanation of the second command,\n ...)"
}
'''

# 유효성 검사 JSON 템플릿
VALIDATION_JSON_TEMPLATE = '''
{
  "analysis": "Extremely detailed analysis of the validation results, analyzing the correctness of each command line by line, clearly pointing out all issues (in Markdown format)",
  "is_valid": boolean,  // Only true when there are absolutely no errors
  "errors": ["Error 1", "Error 2", ...],  // All discovered errors, precisely described
  "warnings": ["Warning 1", "Warning 2", ...],  // Potential issues or inelegant implementations
  "suggestions": ["Suggestion 1", "Suggestion 2", ...],  // Improvement suggestions, can be provided even if the commands are correct
  "command_by_command_analysis": [  // Detailed analysis of each command
    {
      "command": "GeoGebra command",
      "analysis": "Analysis of the command",
    }
  ],
  "construction_plan": { // Re-planned construction plan
    "title": "Construction plan title",
    "description": "Overall description of the construction plan",
    "steps": [
      {
        "step_id": "step_1",
        "description": "Step description",
        "task_type": "point_construction/line_construction/etc",
        "geometric_elements": ["A", "B", "Line_AB"],
        "geogebra_command": "Point/Line/Segment/etc",
        "parameters": {
          "param1": "value1"
        },
        ... // More steps
    ],
    "final_result": "Expected final result"
  }
}
'''

# Command Regeneration JSON Template ------------------------------------------------------------
COMMAND_REGENERATION_JSON_TEMPLATE = '''
{
  "analysis": "Detailed analysis of the reasons for validation failure (in Markdown format, analyzing issues item by item)",
  "fixed_issues": ["Fixed issue 1", "Fixed issue 2", ...],
  "commands": ["GeoGebra command 1", "GeoGebra command 2", ...]
}
'''

# Calculation JSON Template ------------------------------------------------------------

# Construction Manager Prompt

# JSON template update
MANAGER_JSON_TEMPLATE = """{
  "analysis": {
    "problem_type": "equilateral_triangle_angle_trisection", // 
    "special_properties": ["angle_trisection"],
    "reasoning": "This problem involves an equilateral triangle ABC with angle trisection at A, requiring specialized calculation methods."
  },
  "dependency_graph": {
    "nodes": {
      "angle_trisection_1": {
        "dependencies": [],
        "status": "pending"
      },
      "coordinate_D": {
        "dependencies": ["angle_trisection_1"],
        "status": "pending"
      }
      // Other nodes omitted for brevity
    },
    "execution_order": ["angle_trisection_1", "coordinate_D"]
  },
  "geometric_constraints": {
    "angle_trisection": {
      "type": "equal_angles",
      "vertex": "A",
      "rays": ["AC", "AD", "AE", "AB"],
      "properties": "Each angle (CAD, DAE, EAB) must be exactly 1/3 of CAB"
    },
    "regular_polygon": {
      "type": "equilateral_triangle",
      "vertices": ["A", "B", "C"],
      "properties": "All sides equal, all angles 60°"
    },
    "point_constraints": {
      "D": "Must lie on segment BC",
      "E": "Must lie on segment BC"
    }
  },
  "tasks": [
    {
      "task_id": "coordinate_initialization", // First set up basic coordinates
      "task_type": "coordinate",
      "operation_type": "initial_setup", 
      "specific_method": "equilateral_triangle_placement",
      "required_precision": "high",
      "parameters": {
        "side_length": 1.0,  // Use unit side length for simplicity
        "orientation": "standard",  // Place with one side horizontal
        "position": "origin_centered"  // Center at origin or other specific placement
      },
      "dependencies": [],
      "description": "Initialize coordinates for equilateral triangle ABC",
      "geogebra_alternatives": true,
      "geogebra_command": "Polygon[A, B, C]",
      "available_tools": {
        "math_tools": ["vector_calculation", "linear_algebra", "coordinate_geometry"],
        "geometric_tools": ["intersect", "midpoint", "perpendicular", "parallel"],
        "visualization_tools": ["plot_point", "plot_line", "plot_segment"]
      }
    },
    {
      "task_id": "angle_1", // After coordinates are established, work on angle trisection
      "task_type": "angle",
      "operation_type": "angle_trisection",
      "specific_method": "trigonometric_solution",
      "required_precision": "high",
      "parameters": {
        "point1": "C",
        "point2": "A", 
        "point3": "B",
        "special_property": "equilateral_triangle"
      },
      "dependencies": ["coordinate_initialization"],
      "description": "Trisect angle CAB to determine rays AD and AE",
      "geogebra_alternatives": false,
      "available_tools": {
        "math_tools": ["trigonometry", "angle_calculation", "radian_degree_conversion"],
        "geometric_tools": ["angle_bisector", "angle_trisector", "special_angles"],
        "visualization_tools": ["plot_angle", "plot_ray"]
      }
    },
    {
      "task_id": "coordinate_1",
      "task_type": "coordinate",
      "operation_type": "ray_intersection",
      "parameters": {
        "ray_start": "A",
        "ray_angle": "first_trisection_angle",
        "line_segment": "BC"
      },
      "dependencies": ["angle_1", "coordinate_initialization"],
      "description": "Find coordinates of point D where the first trisection ray intersects BC",
      "geogebra_alternatives": false,
      "available_tools": {
        "math_tools": ["vector_calculation", "linear_algebra", "coordinate_geometry"],
        "geometric_tools": ["intersect", "midpoint", "perpendicular", "parallel"],
        "visualization_tools": ["plot_point", "plot_line", "plot_segment"]
      }
    }
    // Other tasks omitted for brevity
  ],
  "completed_task_ids": [], // ["angle_1", "coordinate_1"]
  "next_calculation_type": "angle" // "coordinate", "triangle", "circle", "length", "area", null
}"""


# 삼각형 계산 JSON 템플릿
TRIANGLE_JSON_TEMPLATE = '''
{
  "task_id": "triangle_calculation_task_id", // <task_type>_<task_id> e.g. triangle_1, triangle_2 ...
  "success": true,
  "coordinates": {"A": [x1, y1], "B": [x2, y2], "C": [x3, y3]},  // Basic point coordinates
  "lengths": {"AB": 5.0, "BC": 7.0, "AC": 8.0},  // Length measurements
  "angles": {"A": 30.0, "B": 60.0, "C": 90.0},  // Angle measurements
  "areas": {"ABC": 25.0},  // Area measurements
  
  "geometric_elements": {  // Specialized geometric elements
    "medians": [...],  // Triangle medians
    "altitudes": [...],  // Triangle altitudes
    "special_lines": [...]  // Other special lines
  },
  
  "derived_data": {  // Processed calculation results
    "special_points": {
      "centroid": [x, y],
      "orthocenter": [x, y]
    },
    "properties": {
      "triangle_type": "right"
    }
  },
  
  "explanation": "Calculation process and results explanation"
}
'''

# 더 범용적인 각도 계산 JSON 템플릿
ANGLE_JSON_TEMPLATE = '''
{
  "task_id": "angle_calculation_task_id", // <task_type>_<task_id> e.g. angle_1, angle_2 ...
  "success": true,
  "coordinates": {"A": [x1, y1], "B": [x2, y2], "C": [x3, y3]},  // Basic point coordinates
  "lengths": {"AB": 5.0, "BC": 7.0, "AC": 8.0},  // Length measurements
  "angles": {"ABC": 60.0, "CBD": 45.0, ...},  // Basic angle measurements
  "areas": {"triangle_ABC": 25.0, ...},  // Area measurements if relevant
  
  // General container for arbitrary geometric elements
  "geometric_elements": {
    "rays": [
      {"name": "AD", "angle": 20.0, "direction_vector": [0.9397, -0.3420]},
      {"name": "AE", "angle": 40.0, "direction_vector": [0.7660, -0.6428]}
    ]
  },
  
  // General container for derived data
  "derived_data": {
    // Example: specific geometric properties, relationships, calculation results
    "new_points": {
      "D": [x4, y4],
      "E": [x5, y5]
    },
    "special_properties": {
      "angle_type": "trisection"
    }
  },
  
  "explanation": "Calculation process and results explanation"
}
'''

# 더 범용적인 좌표 계산 JSON 템플릿
COORDINATE_JSON_TEMPLATE = '''
{
  "task_id": "coordinate_calculation_task_id", // <task_type>_<task_id> e.g. coordinate_1, coordinate_2 ...
  "success": true,
  "coordinates": {"A": [x1, y1], "B": [x2, y2], ...},  // Basic point coordinates
  "lengths": {"AB": 5.0, "BC": 7.0, ...},  // Length measurements
  "angles": {"ABC": 60.0, "BCD": 45.0, ...},  // Angle measurements 
  "areas": {"triangle_ABC": 25.0, ...},  // Area measurements if relevant
  
  "geometric_elements": {  // Specialized geometric elements
    "lines": [...],  // Line equations
    "segments": [...],  // Line segments
    "intersections": [...]  // Intersection points
  },
  
  "derived_data": {  // Processed calculation results
    "equations": {...},  // Mathematical equations
    "relationships": {...}  // Geometric relationships
  },
  
  "explanation": "Calculation process and results explanation"
}
'''

# 길이 계산 JSON 템플릿
LENGTH_JSON_TEMPLATE = '''
{
  "task_id": "length_calculation_task_id", // <task_type>_<task_id> e.g. length_1, length_2 ...
  "success": true,
  "coordinates": {"A": [x1, y1], "B": [x2, y2], ...},  // Basic point coordinates
  "lengths": {"AB": 5.0, "BC": 7.0, ...},  // Length measurements
  "angles": {"ABC": 60.0, "BCD": 45.0, ...},  // Angle measurements if relevant
  "areas": {"triangle_ABC": 25.0, ...},  // Area measurements if relevant
  
  "geometric_elements": {  // Specialized geometric elements
    "segments": [...],  // Line segments
    "distances": [...]  // Distance measurements
  },
  
  "derived_data": {  // Processed calculation results
    "ratios": {...},  // Length ratios
    "properties": {...}  // Special properties
  },
  
  "explanation": "Calculation process and results explanation"
}
'''

# 면적 계산 JSON 템플릿
AREA_JSON_TEMPLATE = '''
{
  "task_id": "area_calculation_task_id", // <task_type>_<task_id> e.g. area_1, area_2 ...
  "success": true,
  "coordinates": {"A": [x1, y1], "B": [x2, y2], "C": [x3, y3], ...},  // Basic point coordinates
  "lengths": {"AB": 5.0, "BC": 7.0, ...},  // Length measurements if relevant
  "angles": {"ABC": 60.0, "BCD": 45.0, ...},  // Angle measurements if relevant
  "areas": {"triangle_ABC": 25.0, "rectangle_ABCD": 40.0, ...},  // Area measurements
  
  "geometric_elements": {  // Specialized geometric elements
    "polygons": [...],  // Polygon definitions
    "regions": [...]  // Region definitions
  },
  
  "derived_data": {  // Processed calculation results
    "area_relationships": {...},  // Area relationships
    "properties": {...}  // Special properties
  },
  
  "explanation": "Calculation process and results explanation"
}
'''

# 원 계산 JSON 템플릿
CIRCLE_JSON_TEMPLATE = '''
{
  "task_id": "circle_calculation_task_id", // <task_type>_<task_id> e.g. circle_1, circle_2 ...
  "success": true,
  "coordinates": {"center": [x, y], "point_A": [x1, y1], ...},  // Basic point coordinates
  "lengths": {"radius": 5.0, "diameter": 10.0, ...},  // Length measurements
  "angles": {"central_angle": 60.0, "inscribed_angle": 30.0, ...},  // Angle measurements if relevant
  "areas": {"circle": 78.5, "sector": 15.7, ...},  // Area measurements if relevant
  
  "geometric_elements": {  // Specialized geometric elements
    "circles": [{
      "center": [x, y],
      "radius": 5.0
    }],
    "tangents": [...],  // Tangent lines
    "chords": [...]  // Circle chords
  },
  
  "derived_data": {  // Processed calculation results
    "circle_properties": {
      "radius": 5.0,
      "diameter": 10.0,
      "circumference": 31.4,
      "area": 78.5
    },
    "relationships": {...}  // Geometric relationships
  },
  
  "explanation": "Calculation process and results explanation"
}
'''

MERGER_JSON_TEMPLATE = '''
{
  "coordinates": {"A": [x1, y1], "B": [x2, y2], ...},  // Basic point coordinates
  "lengths": {"AB": 5.0, "BC": 7.0, ...},  // Length measurements
  "angles": {"ABC": 60.0, "BCD": 45.0, ...},  // Angle measurements
  "areas": {"triangle_ABC": 25.0, ...},  // Area measurements
  
  "geometric_elements": {  // Specialized geometric elements
    "rays": [...],  // Angle trisection rays, etc.
    "lines": [...],  // Line equations, etc.
    "circles": [...],  // Circle definitions
    "polygons": [...]  // Polygon definitions
  },
  
  "derived_data": {  // Processed calculation results
    "special_points": {...},  // Centroids, orthocenters, etc.
    "relationships": {...},  // Geometric relationships
    "properties": {...}  // Special properties
  },
  
  "other_results": {
    "final_answer": "The area of triangle ABC is 25 square units",
    "explanation": "By calculating the sides and angles of triangle ABC, we determined that it is a 3-4-5 right triangle with an area of 25 square units"
  },
  
  "construction_plan": {
    "title": "Construction Plan: [Brief Problem Description]",
    "description": "This plan constructs [geometric figure] based on the given conditions and calculated properties.",
    "steps": [
      {
        "step_id": "step_1", // <step_id> e.g. step_1, step_2 ...
        "description": "Define point A at coordinates (x1, y1)",
        "task_type": "point_construction", // point_construction, line_construction, etc.
        "geometric_elements": ["A"],
        "command_type": "Point",
        "parameters": {
          "coordinates": [x1, y1]
        },
        "geogebra_command": "A = (x1, y1)"
      },
      {
        "step_id": "step_2",
        "description": "Create a line segment from point A to point B",
        "task_type": "line_construction",
        "geometric_elements": ["A", "B", "AB"],
        "command_type": "Segment",
        "parameters": {
          "point1": "A",
          "point2": "B"
        },
        "geogebra_command": "Segment[A, B]"
      }
      // Additional steps as needed
    ],
    "final_result": "The construction produces [description of result]"
  }
}
'''
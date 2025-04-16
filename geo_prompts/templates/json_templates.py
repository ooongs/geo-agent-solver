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
      "operation_type": "angleBisector",
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
        }                         
    ],
    "final_result": "Expected final result"
  },
    // ... more command analyses
  ]
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
MANAGER_JSON_TEMPLATE = '''
{
  "tasks": [
    {
      "task_id": "triangle_1",
      "task_type": "triangle",
      "parameters": {
        "point_A": [1, 2],
        "point_B": [3, 4],
        "point_C": [5, 6],
        "length_AB": 5.0,
        "angle_ABC": 60.0
      },
      "description": "Triangle construction task",
      "dependencies": [],
      "geogebra_alternatives": false
    },
    {
      "task_id": "midpoint_1",
      "task_type": "coordinate",
      "parameters": {
        "point_A": "A",
        "point_B": "B"
      },
      "description": "Calculate the midpoint of AB",
      "dependencies": ["triangle_1"],
      "geogebra_alternatives": true,
      "geogebra_command": "Midpoint(A, B)"
    }
  ],
  "next_calculation_type": "triangle",
  "completed_task_ids": ["midpoint_1"],
  "skip_calculations": []
}
'''

# Triangle calculation JSON 템플릿
TRIANGLE_JSON_TEMPLATE = '''
{
  "coordinates": {"A": [x1, y1], "B": [x2, y2], "C": [x3, y3], ...},  // Triangle vertex coordinates
  "lengths": {"AB": 5.0, "BC": 7.0, "AC": 8.0, ...},  // Side length information
  "angles": {"A": 30.0, "B": 60.0, "C": 90.0, ...},  // Angle information
  "areas": {"ABC": 25.0, ...},  // Area information
  "perimeters": {"ABC": 20.0, ...},  // Perimeter information
  "special_points": {"centroid": [x, y], "orthocenter": [x, y], ...},  // Special point information
  "other_results": {
    "triangle_type": "right triangle",
    "is_congruent": true,
    "explanation": "This is a 3-4-5 right triangle, which can be verified using the Pythagorean theorem: 3² + 4² = 5²"
  }  // Other triangle-related results, including explanatory text
}
'''

# 각도 계산 JSON 템플릿
# JSON template definition
ANGLE_JSON_TEMPLATE = '''
{
  "coordinates": {"A": [x1, y1], "B": [x2, y2], "C": [x3, y3], ...},  // Point coordinates
  "angles": {"ABC": 60.0, "CBD": 45.0, ...},  // Various angle values
  "other_results": {
    "angle_type": "acute angle",
    "is_complementary": false, 
    "is_supplementary": true,
    "explanation": "Angle ABC is formed by vectors BA and BC, calculated to be 60 degrees, which is an acute angle"
  }  // Other angle-related results, including explanatory text
}
'''


COORDINATE_JSON_TEMPLATE = '''
{
  "coordinates": {"A": [x1, y1], "B": [x2, y2], "M": [x3, y3], ...},  // Point coordinates
  "lengths": {"AB": 5.0, "BC": 7.0, ...},  // Calculated length information
  "other_results": {
    "slope_AB": 0.5,
    "line_equation": "y = 0.5x + 2",
    "is_collinear": true,
    "is_parallel": false,
    "explanation": "Calculated that the midpoint M of segment AB has coordinates (3, 4), the slope of AB is 0.5, and the equation of line AB is y = 0.5x + 2"
  }  // Other coordinate geometry-related results, including explanatory text
}
'''

# 길이 계산 JSON 템플릿
LENGTH_JSON_TEMPLATE = '''
{
  "lengths": {"AB": 5.0, "BC": 7.0, ...},  // Various length values
  "coordinates": {"A": [x1, y1], "B": [x2, y2], ...},  // Point coordinates (optional)
  "other_results": {
    "length_type": "segment",
    "is_equal": true,
    "explanation": "Using the Pythagorean theorem, we calculated AC = sqrt(AB^2 + BC^2) = sqrt(9 + 16) = sqrt(25) = 5"
  }  // Other length-related results, including explanatory text
}
'''
AREA_JSON_TEMPLATE = '''
{
  "coordinates": {"A": [x1, y1], "B": [x2, y2], "C": [x3, y3], ...},  // Point coordinates
  "areas": {"triangle_ABC": 25.0, "rectangle_ABCD": 40.0, ...},  // Various area values
  "other_results": {
    "area_type": "triangle",
    "calculation_method": "Heron's formula",
    "explanation": "Used Heron's formula to calculate the area of triangle ABC: S = √(s(s-a)(s-b)(s-c)), where s=(a+b+c)/2, resulting in an area of 25 square units"
  }  // Other area-related results, including explanatory text
}
'''


CIRCLE_JSON_TEMPLATE = '''
{
  "coordinates": {"center": [x, y], "point_A": [x1, y1], ...},  // Point coordinates
  "circle_properties": {
    "radius": 5.0,
    "diameter": 10.0,
    "circumference": 31.4,
    "area": 78.5,
    "chord_length": 8.0
  },  // Circle property information
  "other_results": {
    "point_position": "interior",
    "is_tangent": false,
    "explanation": "Calculated that circle O has radius 5, diameter 10, area 78.5 square units, and circumference 31.4 units. Point A is inside the circle, with a distance of 3 units from the center."
  }  // Other circle-related results, including explanatory text
}
'''

MERGER_JSON_TEMPLATE = '''
{
  "coordinates": {"A": [x1, y1], "B": [x2, y2], ...},
  "lengths": {"AB": 5.0, "BC": 7.0, ...},
  "angles": {"ABC": 60.0, "BCD": 45.0, ...},
  "areas": {"triangle_ABC": 25.0, ...},
  "perimeters": {"triangle_ABC": 20.0, ...},
  "special_points": {"centroid": [x, y], "orthocenter": [x, y], ...},
  "circle_properties": {"radius": 5.0, "center": [x, y], ...},
  "ratios": {"AB:BC": 2.5, ...},
  "other_results": {
    "final_answer": "The area of triangle ABC is 25 square units",
    "explanation": "By calculating the sides and angles of triangle ABC, we determined that it is a 3-4-5 right triangle with an area of 25 square units"
  },
  "construction_plan": {
    "title": "Construction plan title",
    "description": "Overall description of the construction plan",
    "steps": [
      {
        "step_id": "step_1",
        "description": "Step description",
        "task_type": "point_construction/line_construction/etc",
        "geometric_elements": ["A", "B", "Line_AB"],
        "command_type": "Point/Line/Segment/etc",
        "parameters": {
          "param1": "value1"
        },
        "geogebra_command": "Optional direct GeoGebra command"
      }
    ],
    "final_result": "Expected final result"
  }
}
'''
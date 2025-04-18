from typing import Dict, Any
from models.state_models import GeometryState
from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain.tools import StructuredTool
from agents.calculation.tools.angle_tools import AngleTools
from agents.calculation.wrappers.angle_wrappers import (
    calculate_angle_three_points_wrapper,
    calculate_angle_two_lines_wrapper,
    calculate_angle_two_vectors_wrapper,
    calculate_interior_angles_triangle_wrapper,
    calculate_exterior_angles_triangle_wrapper,
    calculate_inscribed_angle_wrapper,
    calculate_angle_bisector_wrapper,
    calculate_angle_trisection_wrapper,
    angle_classification_wrapper,
    calculate_rotation_wrapper,
    calculate_angle_with_direction_wrapper,
    normalize_angle_wrapper,
    calculate_angle_complement_wrapper,
    calculate_angle_supplement_wrapper,
    calculate_regular_polygon_angle_wrapper,
    is_angle_acute_wrapper,
    is_angle_right_wrapper,
    is_angle_obtuse_wrapper,
    is_angle_straight_wrapper,
    is_angle_reflex_wrapper,
    is_triangle_acute_wrapper,
    is_triangle_right_wrapper,
    is_triangle_obtuse_wrapper,
    is_triangle_equiangular_wrapper,
    are_angles_equal_wrapper,
    are_angles_complementary_wrapper,
    are_angles_supplementary_wrapper,
    radians_to_degrees_wrapper,
    degrees_to_radians_wrapper
)
from agents.calculation.schemas.angle_schemas import (
    RadiansToDegreesInput, 
    DegreesToRadiansInput, 
    AngleInput,
    TwoAnglesInput,
    RotationInput,
    RegularPolygonInput,
    NormalizeAngleInput,
    AngleClassificationInput,
    AngleBetweenPointsInput, 
    AngleBetweenLinesInput, 
    AngleBetweenVectorsInput,
    AngleTriangleInput,
    InscribedAngleInput,
    AngleComplementInput,
    AngleSupplementInput
)
from langchain_core.output_parsers import JsonOutputParser
from models.calculation_result_model import CalculationResult
from geo_prompts import ANGLE_CALCULATION_PROMPT, ANGLE_JSON_TEMPLATE
from utils.llm_manager import LLMManager
from utils.json_parser import safe_parse_llm_json_output
from agents.calculation.utils.result_utils import update_calculation_results

def angle_calculation_agent(state: GeometryState) -> GeometryState:
    """
    Angle calculation agent
    
    Executes angle-related geometric calculations
    
    Args:
        state: Current state object
    
    Returns:
        Updated state object
    """
    print("[DEBUG] Starting angle_calculation_agent")
    
    # Get current task ID
    current_task_id = state.calculation_queue.current_task_id
    print(f"[DEBUG] Current task ID: {current_task_id}")
    
    if not current_task_id:
        print("[DEBUG] No current_task_id set. Setting it to the first pending angle task.")
        # Set the first pending angle task if no task ID
        for task in state.calculation_queue.tasks:
            if task.task_type == "angle" and task.status == "pending":
                state.calculation_queue.current_task_id = task.task_id
                task.status = "running"
                current_task_id = task.task_id
                print(f"[DEBUG] Set current_task_id to {current_task_id}")
                break
    
    if not current_task_id or not current_task_id.startswith("angle_"):
        # No task ID or not an angle task
        print(f"[DEBUG] Task ID not set or not a angle task: {current_task_id}. Returning state.")
        return state
    
    # Find current task
    current_task = None
    for task in state.calculation_queue.tasks:
        if task.task_id == current_task_id:
            current_task = task
            break
            
    if not current_task:
        print(f"[DEBUG] Could not find task with ID {current_task_id}. Returning state.")
        return state
    
    # Create tools
    tools = [
        # Basic angle calculations
        StructuredTool.from_function(
            name="calculate_angle_three_points",
            func=calculate_angle_three_points_wrapper,
            description="Calculate the angle formed by three points with the middle point as vertex",
            args_schema=AngleBetweenPointsInput,
            handle_tool_error=True
        ),
        StructuredTool.from_function(
            name="calculate_angle_with_direction",
            func=calculate_angle_with_direction_wrapper,
            description="Calculate the angle formed by three points with direction (counter-clockwise is positive)",
            args_schema=AngleBetweenPointsInput,
            handle_tool_error=True
        ),
        StructuredTool.from_function(
            name="calculate_angle_two_vectors",
            func=calculate_angle_two_vectors_wrapper,
            description="Calculate the angle between two vectors",
            args_schema=AngleBetweenVectorsInput,
            handle_tool_error=True
        ),
        StructuredTool.from_function(
            name="calculate_angle_two_lines",
            func=calculate_angle_two_lines_wrapper,
            description="Calculate the angle between two lines",
            args_schema=AngleBetweenLinesInput,
            handle_tool_error=True
        ),
        
        # Triangle angle calculations
        StructuredTool.from_function(
            name="calculate_triangle_interior_angles",
            func=calculate_interior_angles_triangle_wrapper,
            description="Calculate the interior angles of a triangle",
            args_schema=AngleTriangleInput,
            handle_tool_error=True
        ),
        StructuredTool.from_function(
            name="calculate_triangle_exterior_angles",
            func=calculate_exterior_angles_triangle_wrapper,
            description="Calculate the exterior angles of a triangle",
            args_schema=AngleTriangleInput,
            handle_tool_error=True
        ),
        
        # Special angle calculations
        StructuredTool.from_function(
            name="calculate_inscribed_angle",
            func=calculate_inscribed_angle_wrapper,
            description="Calculate the inscribed angle in a circle",
            args_schema=InscribedAngleInput,
            handle_tool_error=True
        ),
        StructuredTool.from_function(
            name="calculate_angle_bisector",
            func=calculate_angle_bisector_wrapper,
            description="Calculate the angle bisector for an angle formed by three points",
            args_schema=AngleBetweenPointsInput,
            handle_tool_error=True
        ),
        StructuredTool.from_function(
            name="calculate_angle_trisection",
            func=calculate_angle_trisection_wrapper,
            description="Calculate the angle trisection lines for an angle formed by three points",
            args_schema=AngleBetweenPointsInput,
            handle_tool_error=True
        ),
        StructuredTool.from_function(
            name="calculate_regular_polygon_angle",
            func=calculate_regular_polygon_angle_wrapper,
            description="Calculate the interior and exterior angles of a regular polygon",
            args_schema=RegularPolygonInput,
            handle_tool_error=True
        ),
        
        # Angle transformations
        StructuredTool.from_function(
            name="calculate_angle_complement",
            func=calculate_angle_complement_wrapper,
            description="Calculate the complement of an angle (90° - angle)",
            args_schema=AngleComplementInput,
            handle_tool_error=True
        ),
        StructuredTool.from_function(
            name="calculate_angle_supplement",
            func=calculate_angle_supplement_wrapper,
            description="Calculate the supplement of an angle (180° - angle)",
            args_schema=AngleSupplementInput,
            handle_tool_error=True
        ),
        StructuredTool.from_function(
            name="normalize_angle",
            func=normalize_angle_wrapper,
            description="Normalize an angle to the range [0, 2π)",
            args_schema=NormalizeAngleInput,
            handle_tool_error=True
        ),
        StructuredTool.from_function(
            name="calculate_rotation",
            func=calculate_rotation_wrapper,
            description="Rotate a point around a center by a given angle",
            args_schema=RotationInput,
            handle_tool_error=True
        ),
        
        # Angle conversions
        StructuredTool.from_function(
            name="radians_to_degrees",
            func=radians_to_degrees_wrapper,
            description="Convert angle from radians to degrees",
            args_schema=RadiansToDegreesInput,
            handle_tool_error=True
        ),
        StructuredTool.from_function(
            name="degrees_to_radians",
            func=degrees_to_radians_wrapper,
            description="Convert angle from degrees to radians",
            args_schema=DegreesToRadiansInput,
            handle_tool_error=True
        ),
        
        # Angle validation and classification
        StructuredTool.from_function(
            name="classify_angle",
            func=angle_classification_wrapper,
            description="Classify an angle as acute, right, obtuse, straight, or reflex",
            args_schema=AngleClassificationInput,
            handle_tool_error=True
        ),
        StructuredTool.from_function(
            name="is_angle_acute",
            func=is_angle_acute_wrapper,
            description="Check if an angle is acute (less than 90°)",
            args_schema=AngleInput,
            handle_tool_error=True
        ),
        StructuredTool.from_function(
            name="is_angle_right",
            func=is_angle_right_wrapper,
            description="Check if an angle is right (equal to 90°)",
            args_schema=AngleInput,
            handle_tool_error=True
        ),
        StructuredTool.from_function(
            name="is_angle_obtuse",
            func=is_angle_obtuse_wrapper,
            description="Check if an angle is obtuse (greater than 90° but less than 180°)",
            args_schema=AngleInput,
            handle_tool_error=True
        ),
        StructuredTool.from_function(
            name="is_angle_straight",
            func=is_angle_straight_wrapper,
            description="Check if an angle is straight (equal to 180°)",
            args_schema=AngleInput,
            handle_tool_error=True
        ),
        StructuredTool.from_function(
            name="is_angle_reflex",
            func=is_angle_reflex_wrapper,
            description="Check if an angle is reflex (greater than 180° but less than 360°)",
            args_schema=AngleInput,
            handle_tool_error=True
        ),
        
        # Triangle validation
        StructuredTool.from_function(
            name="is_triangle_acute",
            func=is_triangle_acute_wrapper,
            description="Check if a triangle is acute (all angles less than 90°)",
            args_schema=AngleTriangleInput,
            handle_tool_error=True
        ),
        StructuredTool.from_function(
            name="is_triangle_right",
            func=is_triangle_right_wrapper,
            description="Check if a triangle is right (one angle equal to 90°)",
            args_schema=AngleTriangleInput,
            handle_tool_error=True
        ),
        StructuredTool.from_function(
            name="is_triangle_obtuse",
            func=is_triangle_obtuse_wrapper,
            description="Check if a triangle is obtuse (one angle greater than 90°)",
            args_schema=AngleTriangleInput,
            handle_tool_error=True
        ),
        StructuredTool.from_function(
            name="is_triangle_equiangular",
            func=is_triangle_equiangular_wrapper,
            description="Check if a triangle is equiangular (all angles equal)",
            args_schema=AngleTriangleInput,
            handle_tool_error=True
        ),
        
        # Angle comparison
        StructuredTool.from_function(
            name="are_angles_equal",
            func=are_angles_equal_wrapper,
            description="Check if two angles are equal within a given tolerance",
            args_schema=TwoAnglesInput,
            handle_tool_error=True
        ),
        StructuredTool.from_function(
            name="are_angles_complementary",
            func=are_angles_complementary_wrapper,
            description="Check if two angles are complementary (sum to 90°)",
            args_schema=TwoAnglesInput,
            handle_tool_error=True
        ),
        StructuredTool.from_function(
            name="are_angles_supplementary",
            func=are_angles_supplementary_wrapper,
            description="Check if two angles are supplementary (sum to 180°)",
            args_schema=TwoAnglesInput,
            handle_tool_error=True
        )
    ]
    
    # Create output parser
    output_parser = JsonOutputParser(pydantic_object=CalculationResult)
    
    # Initialize LLM
    llm = LLMManager.get_angle_calculation_llm()
    
    # Create prompt (with parser instructions)
    prompt = ANGLE_CALCULATION_PROMPT.partial(
        format_instructions=output_parser.get_format_instructions()
    )
    
    # Create agent
    agent = create_openai_functions_agent(llm, tools, prompt)
    agent_executor = AgentExecutor(agent=agent, tools=tools)
    
    # Prepare dependency data
    task_dependencies = {}
    if current_task.dependencies:
        for dep_id in current_task.dependencies:
            if dep_id in state.calculation_results:
                task_dependencies[dep_id] = state.calculation_results[dep_id]
    
    # Process dependency data - add required data to task parameters
    enhanced_task = current_task.model_dump()
    if current_task.parameters and task_dependencies:
        # Specific logic for transforming dependency data
        for dep_id, dep_data in task_dependencies.items():
            # Example: Use coordinate data for angle calculation
            if "coordinates" in dep_data:
                enhanced_task["parameters"]["coordinates"] = dep_data["coordinates"]
            # Example: Use angle data for angle calculation
            if "angles" in dep_data:
                enhanced_task["parameters"]["angles"] = dep_data["angles"]
    
    # Execute agent
    result = agent_executor.invoke({
        "problem": state.input_problem,
        "current_task": str(enhanced_task),
        "calculation_results": str(state.calculation_results),
        "dependencies": str(task_dependencies),  # Pass dependency data
        "json_template": ANGLE_JSON_TEMPLATE,
        "agent_scratchpad": ""
    })
    
    # Parse and store calculation result
    try:
        print(f"[DEBUG] Starting parsing: output type = {type(result)}")
        
        # Check for output field and handle accordingly
        result_output = None
        if isinstance(result, dict) and "output" in result:
            result_output = result["output"]
            print(f"[DEBUG] Extracted output field from dictionary: {type(result_output)}")
        elif hasattr(result, 'output'):
            result_output = result.output
            print(f"[DEBUG] Extracted output attribute from object: {type(result_output)}")
        elif hasattr(result, 'content'):
            result_output = result.content
            print(f"[DEBUG] Extracted content attribute from object: {type(result_output)}")
        else:
            result_output = result
            print(f"[DEBUG] Using result directly: {type(result_output)}")
            
        # Try to parse user-provided JSON format
        # If it's already a dictionary, use it directly
        if isinstance(result_output, dict):
            print("[DEBUG] Result is already a dictionary")
            parsed_result = result_output
        else:
            # Use safe parsing function to parse JSON from string
            print("[DEBUG] Attempting to parse with safe_parse_llm_json_output")
            parsed_result = safe_parse_llm_json_output(result_output, dict)
        
        print(f"[DEBUG] Parsing result: {type(parsed_result)}")
        
        if parsed_result:
            # If parsed result is a dictionary
            if isinstance(parsed_result, dict):
                print(f"[DEBUG] Using parsed dictionary as result: {list(parsed_result.keys())[:5] if parsed_result else 'empty dictionary'}")
                current_task.result = parsed_result
            # If parsed result is a CalculationResult instance
            else:
                print("[DEBUG] Converting CalculationResult object to dictionary")
                current_task.result = parsed_result.to_dict()
        else:
            print("[WARNING] No parsing result, storing original output as raw_output")
            current_task.result = {"raw_output": str(result_output), "success": False}
    except Exception as e:
        print(f"[ERROR] Error parsing calculation result: {e}")
        # In case of error, store original output content and set success to False
        if isinstance(result, dict) and "output" in result:
            raw_output = result["output"]
        else:
            raw_output = str(result)
        current_task.result = {"raw_output": raw_output, "success": False, "error": str(e)}
    
    # Update task status - set to completed
    current_task.status = "completed"
    
    # Add this task to completed tasks list and remove from queue
    if current_task_id not in state.calculation_queue.completed_task_ids:
        state.calculation_queue.completed_task_ids.append(current_task_id)
    
    # Remove task from queue
    for i, task in enumerate(state.calculation_queue.tasks[:]):
        if task.task_id == current_task_id:
            state.calculation_queue.tasks.pop(i)
            print(f"[DEBUG] Removed completed task {current_task_id} from queue")
            break
    
    # Clear current task ID
    state.calculation_queue.current_task_id = None
    
    # Add to overall calculation results
    update_calculation_results(state, current_task)
    
    return state 
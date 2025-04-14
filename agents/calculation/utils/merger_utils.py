"""
결과 병합 에이전트 유틸리티 모듈

이 모듈은 결과 병합 에이전트에서 사용하는 유틸리티 함수들을 정의합니다.
"""

import re
import json
from typing import Dict, Any

def parse_merger_result(output: str, existing_results: Dict[str, Any]) -> Dict[str, Any]:
    """
    병합 결과 파싱
    
    Args:
        output: 에이전트 출력 문자열
        existing_results: 기존 계산 결과
        
    Returns:
        최종 계산 결과
    """
    # JSON 형식 결과가 있는지 확인
    json_pattern = r'```json\n(.*?)\n```'
    json_matches = re.findall(json_pattern, output, re.DOTALL)
    
    if json_matches:
        try:
            return json.loads(json_matches[0])
        except json.JSONDecodeError:
            pass
    
    # 기존 결과가 없으면 새로 생성
    if not existing_results:
        existing_results = {}
    
    # 결과 복사 (기존 결과를 유지하기 위해)
    final_results = {k: v for k, v in existing_results.items()}
    
    # 계산 단계 추출
    steps = []
    step_pattern = r'(?:步骤|step)\s*\d+[.:]\s*(.+?)(?=(?:步骤|step)|$)'
    step_matches = re.findall(step_pattern, output, re.DOTALL)
    if step_matches:
        steps = [step.strip() for step in step_matches]
    
    # 단계가 추출됐으면 추가
    if steps:
        if "steps" not in final_results:
            final_results["steps"] = []
        final_results["steps"].extend(steps)
    
    # 문제 유형 정보 추가
    problem_type = {}
    if "triangle" in output.lower() or "三角形" in output:
        problem_type["triangle"] = True
    if "circle" in output.lower() or "圆" in output:
        problem_type["circle"] = True
    if "angle" in output.lower() or "角" in output:
        problem_type["angle"] = True
    if "coordinate" in output.lower() or "坐标" in output:
        problem_type["coordinate"] = True
    
    if problem_type:
        final_results["problem_type"] = problem_type
    
    # 종합 결론 추출
    conclusion = re.search(r'(?:结论|conclusion)[：:]\s*(.*?)(?=\n\n|\Z)', output, re.DOTALL)
    if conclusion:
        final_results["conclusion"] = conclusion.group(1).strip()
    
    return final_results 
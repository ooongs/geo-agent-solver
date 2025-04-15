import os
import json
from main import save_result

def test_save():
    """기존 JSON 파일을 로드하여 명령어 저장 함수 테스트"""
    # 기존 JSON 파일 로드
    json_path = "output/△ABC为正三角形，D、E为BC上的点，_20_commands.json"
    
    with open(json_path, 'r', encoding='utf-8') as f:
        result = json.load(f)
    
    # 결과 저장 (테스트용 디렉토리에)
    test_dir = "test_output"
    os.makedirs(test_dir, exist_ok=True)
    
    # 저장 함수 호출
    save_result(result, test_dir)
    
    print(f"결과가 {test_dir} 디렉토리에 저장되었습니다.")
    
    # 저장된 텍스트 파일 내용 출력
    txt_path = f"{test_dir}/△ABC为正三角形，D、E为BC上的点，_20_commands.txt"
    if os.path.exists(txt_path):
        with open(txt_path, 'r', encoding='utf-8') as f:
            content = f.read()
        print("\n저장된 명령어:")
        print(content)
    else:
        print(f"오류: {txt_path} 파일이 생성되지 않았습니다.")

if __name__ == "__main__":
    test_save() 
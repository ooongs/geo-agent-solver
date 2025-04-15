"""
GeoGebra 명령어 검색 기능 테스트 모듈

이 모듈은 retrieval.py의 CommandRetrieval 클래스 기능을 테스트합니다.
"""

import argparse
from db.retrieval import CommandRetrieval

def test_search_by_command(retrieval, command):
    """
    명령어로 검색하는 기능 테스트
    """
    print(f"\n==== 명령어 '{command}' 로 검색 테스트 ====")
    results = retrieval.search_commands_by_command(command)
    
    if not results:
        print(f"'{command}' 명령어에 대한 검색 결과가 없습니다.")
        return
    
    print(f"총 {len(results)}개 결과 찾음:")
    for i, result in enumerate(results, 1):
        print(f"\n결과 {i}:")
        print(f"  명령어: {result['command']}")
        print(f"  구문: {result['syntax']}")
        print(f"  설명: {result['description']}")
        print(f"  점수: {result['score']:.4f}")

def test_hybrid_search(retrieval, query, category=None):
    """
    하이브리드 검색 기능 테스트
    """
    print(f"\n==== '{query}' 하이브리드 검색 테스트 ====")
    
    results = retrieval.hybrid_search(query)
    
    if not results:
        print(f"'{query}' 에 대한 검색 결과가 없습니다.")
        return
    
    print(f"총 {len(results)}개 결과 찾음:")
    for i, result in enumerate(results, 1):
        print(f"\n결과 {i}:")
        print(f"  명령어: {result['command']}")
        print(f"  구문: {result['syntax']}")
        print(f"  설명: {result['description']}")
        print(f"  카테고리: {result['category']}")
        print(f"  예제: {result['examples']}")
        print(f"  점수: {result['score']:.4f}")

def test_suggest_commands(retrieval, query):
    """
    문제 텍스트에 대한 명령어 추천 테스트
    """
    print(f"\n==== 문제 텍스트에 대한 명령어 추천 테스트 ====")
    print(f"문제: {query}")
    
    results = retrieval.suggest_commands_for_problem(query)
    
    if not results:
        print("추천 명령어가 없습니다.")
        return
    
    print(f"총 {len(results)}개 명령어 추천:")
    for i, result in enumerate(results, 1):
        print(f"\n추천 {i}:")
        print(f"  명령어: {result['command']}")
        print(f"  구문: {result['syntax']}")
        print(f"  설명: {result['description']}")
        print(f"  예제: {result['examples']}")
        print(f"  카테고리: {result['category']}")
        print(f"  점수: {result['score']:.4f}")

def main():
    """
    메인 함수 - 명령행 인자를 처리하고 테스트 실행
    """
    parser = argparse.ArgumentParser(description='GeoGebra 명령어 검색 테스트')
    parser.add_argument('--mode', choices=['command', 'hybrid', 'suggest', 'all'], 
                        default='all', help='테스트 모드 선택')
    parser.add_argument('--query', default='画出半径为2的圆', help='검색할 쿼리 또는 명령어')
    parser.add_argument('--command', default='Circle', help='카테고리 필터')
    
    args = parser.parse_args()
    
    # CommandRetrieval 인스턴스 생성
    print("검색 모듈 초기화 중...")
    retrieval = CommandRetrieval()
    print("초기화 완료!")
    
    # 선택된 모드에 따라 테스트 실행
    if args.mode == 'command' or args.mode == 'all':
        test_search_by_command(retrieval, args.command)
    
    if args.mode == 'hybrid' or args.mode == 'all':
        test_hybrid_search(retrieval, args.query, args.command)
    
if __name__ == "__main__":
    main() 
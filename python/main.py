import os
from python.process import process
from python.config import env_result

def main():
    # 환경 변수 로드 결과 확인
    if not env_result.get("success", False):
        print(f"오류: 환경 변수 로드 실패 - {env_result.get('message', '알 수 없는 오류')}")
        return
    
    # 정상적으로 환경 변수가 로드되었으면 프로세스 실행
    process()
    
if __name__ == "__main__":
    main()
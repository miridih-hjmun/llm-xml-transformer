import os
import json
from dotenv import load_dotenv

# 환경 변수 로드 함수
def load_environment_variables():
    """
    .env 파일에서 환경 변수를 로드하는 함수
    
    Returns:
        dict: 로드된 환경 변수 정보
    """
    # python 디렉토리 경로 계산
    python_dir = os.path.dirname(os.path.abspath(__file__))
    dotenv_path = os.path.join(python_dir, '.env')
    
    # .env 파일 존재 여부 확인
    if not os.path.exists(dotenv_path):
        print(f"경고: .env 파일을 찾을 수 없습니다. 경로: {dotenv_path}")
        return {"success": False, "message": "환경 변수 파일을 찾을 수 없습니다."}
    
    # .env 파일 로드
    try:
        load_dotenv(dotenv_path=dotenv_path)
        
        # 필수 환경 변수 확인
        required_vars = ['OPENAI_API_KEY']
        missing_vars = [var for var in required_vars if not os.getenv(var)]
        
        if missing_vars:
            print(f"경고: 다음 필수 환경 변수가 설정되지 않았습니다: {', '.join(missing_vars)}")
            return {
                "success": False, 
                "message": f"필수 환경 변수가 설정되지 않았습니다: {', '.join(missing_vars)}"
            }
        
        # API 키 마스킹하여 출력
        api_key = os.getenv('OPENAI_API_KEY')
        if api_key:
            masked_key = f"{api_key[:5]}...{api_key[-4:]}" if len(api_key) > 10 else "***"
            print(f"OPENAI_API_KEY 환경 변수가 설정되었습니다. 값: {masked_key}")
        
        return {"success": True, "message": "환경 변수 로드 성공"}
        
    except Exception as e:
        print(f"환경 변수 로드 중 오류 발생: {e}")
        return {"success": False, "message": f"환경 변수 로드 중 오류 발생: {e}"}

# 환경 변수 가져오기 함수
def get_env(key, default=None):
    """
    환경 변수 값을 가져오는 함수
    
    Args:
        key (str): 환경 변수 키
        default: 환경 변수가 없을 경우 반환할 기본값
        
    Returns:
        환경 변수 값 또는 기본값
    """
    return os.getenv(key, default)

# 모듈 로드 시 자동으로 환경 변수 로드
env_result = load_environment_variables()
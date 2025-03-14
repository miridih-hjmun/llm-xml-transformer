import os
import json
import argparse
import subprocess
from pathlib import Path

from python.process import process
from python.config import env_result

def main():
    # 디버깅 모드 확인
    DEBUG_MODE = os.environ.get('DEBUG_MODE', 'False').lower() == 'true'
    
    if DEBUG_MODE:
        # 디버깅용 정적 인자값 설정
        print("디버깅 모드: 정적 인자값 사용")
        input_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "/Users/munhyeokjun/Desktop/develop-env/250228/input-dev")
        output_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "/Users/munhyeokjun/Desktop/develop-env/250228/output-dev")
    else:
        # 명령줄 인자 파서 생성
        parser = argparse.ArgumentParser(description='XML 변환 및 LLM 처리 도구')
        parser.add_argument('--input', '-i', required=True, help='입력 파일 또는 디렉토리 경로')
        parser.add_argument('--output', '-o', required=True, help='출력 디렉토리 경로')
        
        # 명령줄 인자 파싱
        args = parser.parse_args()
        
        # 입력 및 출력 경로 설정
        input_path = os.path.abspath(args.input)
        output_path = os.path.abspath(args.output)
    
    # 환경 변수 로드 결과 확인
    if not env_result.get("success", False):
        print(f"오류: 환경 변수 로드 실패 - {env_result.get('message', '알 수 없는 오류')}")
        return
    
    # 환경 변수 설정 (process.py에서 사용)
    os.environ['INPUT_PATH'] = input_path
    os.environ['OUTPUT_PATH'] = output_path
    
    print(f"입력 경로: {input_path}")
    print(f"출력 경로: {output_path}")
    
    # 출력 디렉토리가 없으면 생성
    if not os.path.exists(output_path):
        os.makedirs(output_path)
    
    # Python 처리 단계: XML 추출 및 처리
    print("Python 처리 단계: XML 추출 및 처리 중...")
    process()
    
    # batches_meta.json 파일 경로
    meta_json_path = os.path.join(output_path, "batches_meta.json")
    
    # Node.js 처리 단계
    print("Node.js 처리 단계: 추출된 XML 데이터 처리 중...")
    
    # 현재 스크립트의 경로를 기준으로 Node.js 스크립트 경로 계산
    current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    node_script_path = os.path.join(current_dir, "node", "dist", "app.js")
    
    # Node.js 스크립트 실행
    try:
        node_process = subprocess.Popen(
            ["node", node_script_path, "--data", meta_json_path, "--output", output_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # 실시간으로 출력 표시
        for line in node_process.stdout:
            print(line.strip())
        
        # 프로세스 완료 대기
        node_process.wait()
        
        # 오류 확인
        if node_process.returncode != 0:
            print("Node.js 처리 중 오류 발생:")
            for line in node_process.stderr:
                print(line.strip())
            return
        
        print("Node.js 처리 완료")
    except Exception as e:
        print(f"Node.js 스크립트 실행 중 오류 발생: {e}")
        return
    
    print(f"모든 처리가 완료되었습니다. 결과는 {output_path}에 저장되었습니다.")

if __name__ == "__main__":
    main()
import os
import re
import sys
from pathlib import Path

from python.services.xml_processor import XMLParser

def process():
    """XML 파일 처리 메인 함수"""
    # 환경 변수에서 입력/출력 경로 가져오기
    input_path = os.getenv('INPUT_PATH')
    output_path = os.getenv('OUTPUT_PATH')
    
    if not input_path or not output_path:
        print("오류: 환경 변수 INPUT_PATH 또는 OUTPUT_PATH가 설정되지 않았습니다.")
        return {"success": False, "error": "환경 변수 설정 오류"}

    # 출력 디렉토리 생성
    os.makedirs(output_path, exist_ok=True)
    
    # XML 파일 목록 생성
    xml_files = []
    if os.path.isdir(input_path):
        xml_files = list(Path(input_path).glob("**/*.xml"))
    elif os.path.isfile(input_path) and input_path.endswith(".xml"):
        xml_files = [Path(input_path)]
    
    if not xml_files:
        error_msg = f"오류: 입력 경로 '{input_path}'에서 XML 파일을 찾을 수 없습니다."
        print(error_msg)
        return {"success": False, "error": error_msg}
    
    print(f"{len(xml_files)}개의 XML 파일을 처리합니다...")
    
    # 결과 저장용 딕셔너리
    results = {
        "success": True,
        "processed_files": [],
        "errors": []
    }
    
    # 각 XML 파일 처리
    for xml_file in xml_files:
        file_name = xml_file.name
        page_idx = extract_idx(xml_file.stem)
        
        try:
            # XML 파일 처리
            parser = XMLParser(str(xml_file))
            
            # XML 문자열 생성 (파일에 저장하지 않고 메모리에 보관)
            positive_xml = parser.generate_xml_string(is_positive=True)
            negative_xml = parser.generate_xml_string(is_positive=False)
            
            print(f"파일 '{file_name}' 처리 완료")
            
            # 결과 저장 - XML 문자열 포함
            results["processed_files"].append({
                "success": True, 
                "file": file_name, 
                "page_idx": page_idx,
                "positive_xml": positive_xml,
                "negative_xml": negative_xml
            })
            
        except Exception as e:
            print(f"파일 '{file_name}' 처리 중 오류: {e}")
            results["errors"].append({
                "success": False, 
                "file": file_name, 
                "error": str(e)
            })
    
    return results

def extract_idx(filename):
    """파일명에서 숫자 추출 (예: '12344_text' -> '12344')"""
    match = re.match(r'^(\d+)', filename)
    return match.group(1) if match else filename

if __name__ == "__main__":
    process()
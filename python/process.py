import os
import re
import sys
import json
import math
from pathlib import Path

from python.services.xml_processor import XMLParser

def process():
    """XML 파일 처리 메인 함수"""
    # 환경 변수에서 입력/출력 경로 가져오기
    input_path = os.getenv('INPUT_PATH')
    output_path = os.getenv('OUTPUT_PATH')
    
    # 배치 사이즈 환경 변수에서 가져오기 (기본값: 100)
    batch_size = int(os.getenv('BATCH_SIZE', '100'))
    
    if not input_path or not output_path:
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
    
    # 배치 처리를 위한 파일 분할
    total_batches = math.ceil(len(xml_files) / batch_size)
    print(f"총 {total_batches}개의 배치로 나누어 처리합니다. (배치당 최대 {batch_size}개 파일)")
    
    # 모든 배치 결과를 저장할 딕셔너리
    result = {
        "success": True,
        "total_files": len(xml_files),
        "total_batches": total_batches,
        "batches": []
    }
    
    # 배치별 처리
    for batch_idx in range(total_batches):
        start_idx = batch_idx * batch_size
        end_idx = min(start_idx + batch_size, len(xml_files))
        batch_files = xml_files[start_idx:end_idx]
        
        print(f"배치 {batch_idx + 1}/{total_batches} 처리 중... ({len(batch_files)}개 파일)")
        
        # 배치 결과 저장용 딕셔너리
        batch_results = {
            "batch_idx": batch_idx,
            "success": True,
            "processed_files": [],
            "errors": []
        }
        
        # 각 XML 파일 처리
        for xml_file in batch_files:
            file_name = xml_file.name
            page_idx = extract_idx(xml_file.stem)
            
            try:
                # XML 파일 처리
                parser = XMLParser(str(xml_file))
                
                # XML 문자열 생성 (API 한 번만 호출)
                positive_xml, negative_xml = parser.generate_xml_string()
                
                print(f"파일 '{file_name}' 처리 완료")
                
                # 결과 저장 - XML 문자열 포함
                batch_results["processed_files"].append({
                    "success": True, 
                    "file": file_name, 
                    "page_idx": page_idx,
                    "positive_xml": positive_xml,
                    "negative_xml": negative_xml
                })
                
            except Exception as e:
                print(f"파일 '{file_name}' 처리 중 오류: {e}")
                batch_results["errors"].append({
                    "success": False, 
                    "file": file_name, 
                    "error": str(e)
                })
        
        # 배치 결과를 JSON 파일로 저장
        batch_json_path = os.path.join(output_path, f"batch_{batch_idx}.json")
        with open(batch_json_path, 'w', encoding='utf-8') as f:
            json.dump(batch_results, f, ensure_ascii=False, indent=2)
        
        print(f"배치 {batch_idx + 1} 결과가 {batch_json_path}에 저장되었습니다.")
        
        # 전체 결과에 배치 정보 추가
        result["batches"].append({
            "batch_idx": batch_idx,
            "file_count": len(batch_files),
            "json_path": batch_json_path
        })
    
    # 전체 배치 정보를 담은 메타데이터 JSON 파일 저장
    meta_json_path = os.path.join(output_path, "batches_meta.json")
    with open(meta_json_path, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    print(f"모든 배치 처리가 완료되었습니다. 메타데이터는 {meta_json_path}에 저장되었습니다.")
    
    return result

def extract_idx(filename):
    """파일명에서 숫자 추출 (예: '12344_text' -> '12344')"""
    match = re.match(r'^(\d+)', filename)
    return match.group(1) if match else filename

if __name__ == "__main__":
    process()
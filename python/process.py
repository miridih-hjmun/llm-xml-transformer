import os
import re
from pathlib import Path
from python.services.xml_processor import XMLParser

def process():
    # 입력 경로 설정 (파일 또는 디렉토리)
    input_path = os.getenv('INPUT_PATH')
    output_path = os.getenv('OUTPUT_PATH')
    
    if not input_path or not output_path:
        print("오류: 환경 변수 INPUT_PATH 또는 OUTPUT_PATH가 설정되지 않았습니다.")
        return

    # 출력 디렉토리가 없으면 생성
    if not os.path.exists(output_path):
        os.makedirs(output_path)

    # 입력 경로가 디렉토리인지 파일인지 확인
    if os.path.isdir(input_path):
        # 디렉토리인 경우 모든 XML 파일 처리
        process_directory(input_path, output_path)
    elif os.path.isfile(input_path) and input_path.endswith(".xml"):
        # 단일 XML 파일인 경우 처리
        process_file(input_path, output_path)
    else:
        print(f"오류: 입력 경로 '{input_path}'는 유효한 XML 파일 또는 디렉토리가 아닙니다.")

def process_directory(input_directory, output_directory):
    """디렉토리 내의 모든 XML 파일 처리"""
    xml_files = [f for f in os.listdir(input_directory) if f.endswith(".xml")]
    
    if not xml_files:
        print(f"경고: '{input_directory}' 디렉토리에 XML 파일이 없습니다.")
        return
    
    print(f"총 {len(xml_files)}개의 XML 파일을 처리합니다.")
    
    for i, xml_file in enumerate(xml_files):
        input_file_path = os.path.join(input_directory, xml_file)
        
        # 파일명에서 숫자 부분 추출
        file_number = extract_number_from_filename(Path(xml_file).stem)
        
        print(f"\n[{i+1}/{len(xml_files)}] 처리 중: {xml_file}")
        print(f"입력 파일: {input_file_path}")
        print(f"파일 번호: {file_number}")
        
        try:
            # XML 처리
            parser = XMLParser(input_file_path)
            
            # 출력 파일 경로 생성
            output_path_positive = os.path.join(output_directory, f"{file_number}_positive.xml")
            output_path_negative = os.path.join(output_directory, f"{file_number}_negative.xml")
            
            print(f"Positive 출력 파일: {output_path_positive}")
            print(f"Negative 출력 파일: {output_path_negative}")
            
            parser.generate_xml(output_path_positive, output_path_negative)
            print(f"파일 '{xml_file}' 처리 완료!")
        except Exception as e:
            print(f"파일 '{xml_file}' 처리 중 오류 발생: {e}")

def process_file(input_file, output_directory):
    """단일 XML 파일 처리"""
    file_name = os.path.basename(input_file)
    
    # 파일명에서 숫자 부분 추출
    file_number = extract_number_from_filename(Path(file_name).stem)
    
    print(f"입력 파일: {input_file}")
    print(f"파일 번호: {file_number}")
    
    try:
        # XML 처리
        parser = XMLParser(input_file)
        
        # 출력 파일 경로 생성
        output_path_positive = os.path.join(output_directory, f"{file_number}_positive.xml")
        output_path_negative = os.path.join(output_directory, f"{file_number}_negative.xml")
        
        print(f"Positive 출력 파일: {output_path_positive}")
        print(f"Negative 출력 파일: {output_path_negative}")
        
        parser.generate_xml(output_path_positive, output_path_negative)
        print(f"파일 '{file_name}' 처리 완료!")
    except Exception as e:
        print(f"파일 '{file_name}' 처리 중 오류 발생: {e}")
        
def extract_number_from_filename(filename):
    """
    파일명에서 숫자 부분만 추출합니다.
    예: '12344_asfaef_sdf.xml' -> '12344'
    
    Args:
        filename: 파일명
        
    Returns:
        str: 추출된 숫자 부분
    """
    # 파일명에서 첫 번째 숫자 그룹 추출
    match = re.match(r'^(\d+)', filename)
    if match:
        return match.group(1)
    return filename  # 숫자가 없으면 원본 파일명 반환

if __name__ == "__main__":
    process()
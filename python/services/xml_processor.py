import xml.etree.ElementTree as ET
import json
import os
import re
from prompt.Design_PosNeg_Prompts.src.workflow import process_text

class XMLParser:
    def __init__(self, file_path):
        self.file_path = file_path
        self.tree = ET.parse(file_path)
        self.root = self.tree.getroot()

    def generate_xml(self, output_path_positive, output_path_negative):
        """
        XML 파일을 처리하고 결과를 저장합니다.
        
        Args:
            output_path_positive: positive 텍스트가 적용된 XML 파일 경로
            output_path_negative: negative 텍스트가 적용된 XML 파일 경로
        """
        # 출력 디렉토리가 없으면 생성
        os.makedirs(os.path.dirname(output_path_positive), exist_ok=True)
        os.makedirs(os.path.dirname(output_path_negative), exist_ok=True)
        
        # 원본 XML 파일에서 텍스트 추출
        text_info_list = self.extract_text()
        text_list = [text for text, _ in text_info_list]
        tbpe_id_list = [tbpe_id for _, tbpe_id in text_info_list]
        
        if not text_list:
            print("추출된 텍스트가 없습니다.")
            return
        
        # 텍스트 리스트를 \\+\\ 구분자로 연결
        combined_text = "\\+\\".join(text_list)
        
        # workflow.py의 process_text 함수에 결합된 텍스트 전달
        try:
            processed_result = process_text(combined_text)
            print(f"프롬프트 처리 결과: {processed_result}")
        except Exception as e:
            print(f"텍스트 처리 중 오류 발생: {e}")
            return
        
        # positive 텍스트 처리 및 저장
        positive_text_info_list = self.extract_processed_texts(processed_result, text_list, tbpe_id_list, "positive")
        self.update_xml(positive_text_info_list)
        self.save_xml(output_path_positive)
        print(f"Positive XML 파일 저장 완료: {output_path_positive}")
        
        # 원본 XML 파일을 다시 로드 (positive 처리로 변경된 내용을 초기화)
        self.tree = ET.parse(self.file_path)
        self.root = self.tree.getroot()
        
        # negative 텍스트 처리 및 저장
        negative_text_info_list = self.extract_processed_texts(processed_result, text_list, tbpe_id_list, "negative")
        self.update_xml(negative_text_info_list)
        self.save_xml(output_path_negative)
        print(f"Negative XML 파일 저장 완료: {output_path_negative}")
    
    def extract_processed_texts(self, processed_result, text_list, tbpe_id_list, doc_type="positive"):
        """
        process_text 함수의 결과에서 텍스트를 추출하고 TbpeId와 매핑합니다.
        
        Args:
            processed_result: process_text 함수의 결과 (딕셔너리 형태)
            text_list: 원본 텍스트 리스트
            tbpe_id_list: TbpeId 리스트h
            doc_type: 문서 유형 ("positive" 또는 "negative")
            
        Returns:
            list: (텍스트, TbpeId) 튜플의 리스트
        """
        prompted_text_info_list = []
        
        try:
            # 딕셔너리 형태로 결과가 반환된 경우
            if isinstance(processed_result, dict):
                # positive 또는 negative 텍스트 선택
                if doc_type == "negative":
                    processed_text = processed_result.get("hard_negative_document", "")
                else:  # positive
                    processed_text = processed_result.get("positive_document", "")
                
                print(f"{doc_type} 텍스트: {processed_text}")
                print(f"{doc_type} 텍스트 (repr): {repr(processed_text)}")
                
                # 처리된 텍스트를 개행 문자(\n)로 분리
                processed_text_list = processed_text.split("\n")
                processed_text_list = [text.strip() for text in processed_text_list if text.strip()]
                
                print(f"분리된 텍스트 수: {len(processed_text_list)}, 원본 텍스트 수: {len(text_list)}")
                
                # 분리된 텍스트 수가 원본 텍스트 수와 다를 경우
                if len(processed_text_list) != len(text_list):
                    print(f"개행 문자로 분리된 텍스트 수({len(processed_text_list)})가 원본 텍스트 수({len(text_list)})와 다릅니다.")
                    
                    # 텍스트 수가 더 많은 경우, 원본 텍스트 수에 맞게 조정
                    if len(processed_text_list) > len(text_list):
                        print(f"처리된 텍스트가 더 많습니다. 원본 텍스트 수에 맞게 조정합니다.")
                        processed_text_list = processed_text_list[:len(text_list)]
                    
                    # 텍스트 수가 더 적은 경우, 부족한 부분은 원본 텍스트로 채움
                    elif len(processed_text_list) < len(text_list):
                        print(f"처리된 텍스트가 더 적습니다. 부족한 부분은 원본 텍스트로 채웁니다.")
                        for i in range(len(processed_text_list), len(text_list)):
                            processed_text_list.append(text_list[i])
                
                # 텍스트와 TbpeId 매핑
                for i, (processed_text, tbpe_id) in enumerate(zip(processed_text_list, tbpe_id_list)):
                    prompted_text_info_list.append((processed_text, tbpe_id))
                    print(f"처리된 텍스트 ({i+1}/{len(processed_text_list)}): {processed_text}, TbpeId={tbpe_id}")
            
            # 딕셔너리가 아닌 경우 (문자열인 경우)
            else:
                print(f"처리된 결과가 딕셔너리가 아닙니다. 원본 텍스트를 유지합니다.")
                # 원본 텍스트 유지
                for i, (text, tbpe_id) in enumerate(zip(text_list, tbpe_id_list)):
                    prompted_text_info_list.append((text, tbpe_id))
                    print(f"원본 텍스트 유지 ({i+1}/{len(text_list)}): {text}, TbpeId={tbpe_id}")
        
        except Exception as e:
            print(f"텍스트 추출 중 오류 발생: {e}")
            # 오류 발생 시 원본 텍스트 유지
            for i, (text, tbpe_id) in enumerate(zip(text_list, tbpe_id_list)):
                prompted_text_info_list.append((text, tbpe_id))
                print(f"오류로 인한 원본 텍스트 유지 ({i+1}/{len(text_list)}): TbpeId={tbpe_id}")
        
        return prompted_text_info_list
    
    def extract_text(self):
        """XML에서 <SIMPLE_TEXT> 또는 <TEXT> 태그의 텍스트와 TbpeId를 추출하고 형식을 변환합니다."""
        text_tag_info = []

        # SIMPLE_TEXT 태그에서 텍스트와 TbpeId 추출
        for simple_text_tag in self.root.findall(".//SIMPLE_TEXT"):
            text_body = simple_text_tag.find(".//TextBody")
            if text_body is not None and text_body.text:
                try:
                    json_data = json.loads(text_body.text)
                    texts = self.extract_texts_from_json_structure(json_data)
                    tbpe_id = simple_text_tag.get('TbpeId')
                    
                    # 추출된 각 텍스트에 대해 형식 변환
                    for text in texts:
                        if text is not None:  # text가 None이 아닌 경우에만 처리
                            # 개행 문자만 \\\ 로 대체
                            formatted_text = text.replace("\n", "\\\\\\")
                            text_tag_info.append((formatted_text, tbpe_id))
                except json.JSONDecodeError:
                    continue

        # TEXT 태그에서 텍스트와 TbpeId 추출
        for text_tag in self.root.findall(".//TEXT"):
            # TEXT 태그 내부의 Text 하위 태그 찾기
            text_subtag = text_tag.find("Text")
            if text_subtag is not None and text_subtag.text is not None:
                text = text_subtag.text
            else:
                # 하위 태그가 없거나 텍스트가 없으면 TEXT 태그 자체의 텍스트 사용
                text = text_tag.text
            
            tbpe_id = text_tag.get('TbpeId')
            if text is not None:
                # 개행 문자만 \\\ 로 대체
                formatted_text = text.replace("\n", "\\\\\\")
                text_tag_info.append((formatted_text, tbpe_id))

        return text_tag_info

    def extract_texts_from_json_structure(self, json_data):
        """
        재귀적으로 JSON 구조를 탐색하여 텍스트 추출
        SIMPLE_TEXT 태그의 TextBody에 있는 JSON 구조에서 실제 텍스트만 추출

        """
        # 결과 텍스트를 저장할 리스트
        result = []
        
        # 리스트인 경우 각 항목에 대해 재귀 호출
        if isinstance(json_data, list):
            for item in json_data:
                result.extend(self.extract_texts_from_json_structure(item))
        
        # 딕셔너리인 경우
        elif isinstance(json_data, dict):
            # 텍스트 노드 처리 ("t"가 "r"이고 "c"에 문자열 리스트가 있는 경우)
            if json_data.get("t") == "r" and "c" in json_data and isinstance(json_data["c"], list):
                # "c" 리스트의 각 항목이 문자열인 경우 텍스트로 추가
                for item in json_data["c"]:
                    if isinstance(item, str):
                        result.append(item)
                    else:
                        # 문자열이 아닌 경우 재귀 처리
                        result.extend(self.extract_texts_from_json_structure(item))
            
            # 다른 노드는 "c" 필드만 재귀적으로 처리
            elif "c" in json_data:
                result.extend(self.extract_texts_from_json_structure(json_data["c"]))
        
        return result
        
    def update_xml(self, response_list):
        """시뮬레이션된 응답을 XML에 적용"""
        # 파일 버전 확인 (TEXT 태그가 있는지 SIMPLE_TEXT 태그가 있는지)
        has_text_tag = len(self.root.findall(".//TEXT")) > 0
        has_simple_text_tag = len(self.root.findall(".//SIMPLE_TEXT")) > 0
        
        for prompted_text, tbpe_id in response_list:
            if has_text_tag:
                # TEXT 태그 버전 처리
                self.update_text_tag(prompted_text, tbpe_id)
            elif has_simple_text_tag:
                # SIMPLE_TEXT 태그 버전 처리
                self.update_simple_text_tag(prompted_text, tbpe_id)
            else:
                print(f"지원되지 않는 XML 형식입니다. TbpeId: {tbpe_id}")

    def update_text_tag(self, prompted_text, tbpe_id):
        """TEXT 태그 내부의 Text 태그 내용을 업데이트하고 TextData 태그 삭제"""
        for text_tag in self.root.findall(".//TEXT"):
            if text_tag.get('TbpeId') == tbpe_id:
                # Text 태그 찾기
                text_inner_tag = text_tag.find("Text")
                if text_inner_tag is not None:
                    # Text 태그 내용 업데이트
                    text_inner_tag.text = prompted_text
                    print(f"TEXT 내부의 Text 태그 업데이트 완료: {tbpe_id}")
                else:
                    # Text 태그가 없으면 TEXT 태그 내용 직접 업데이트
                    text_tag.text = prompted_text
                    print(f"Text 태그가 없어 TEXT 태그 직접 업데이트 완료: {tbpe_id}")
                
                # TextData 태그 삭제
                self.remove_renderPos_tag(text_tag, "TextData")
                self.remove_renderPos_tag(text_tag, "RenderPos")
                print(f"TextData 태그 삭제 완료: {tbpe_id}")

    def update_simple_text_tag(self, prompted_text, tbpe_id):
        """SIMPLE_TEXT 태그 업데이트 및 RenderPos 태그 삭제"""
        for simple_text_tag in self.root.findall(".//SIMPLE_TEXT"):
            if simple_text_tag.get('TbpeId') == tbpe_id:
                text_body = simple_text_tag.find("TextBody")
                if text_body is not None:
                    try:
                        # 기존 JSON 구조를 파싱
                        json_data = json.loads(text_body.text)
                        # JSON 구조 내의 특정 텍스트를 업데이트
                        self.update_text_json_structure(json_data, prompted_text)
                        # 업데이트된 JSON 구조를 다시 문자열로 변환하여 저장
                        text_body.text = json.dumps(json_data, ensure_ascii=False)
                        
                        # RenderPos 태그 삭제
                        self.remove_renderPos_tag(simple_text_tag, "RenderPos")
                        print(f"SIMPLE_TEXT 태그 업데이트 완료: {tbpe_id}")
                    except json.JSONDecodeError as e:
                        print(f"JSON 파싱 오류: {e}")
                        continue

    def update_text_json_structure(self, json_data, new_text):
        """JSON 구조 내의 텍스트를 업데이트"""
        if isinstance(json_data, dict):
            # "c" 키가 있고 그 값이 리스트인 경우
            if "c" in json_data and isinstance(json_data["c"], list):
                # "c" 리스트의 각 항목에 대해
                for i, item in enumerate(json_data["c"]):
                    # 항목이 문자열인 경우 업데이트
                    if isinstance(item, str):
                        json_data["c"][i] = new_text
                    # 항목이 딕셔너리나 리스트인 경우 재귀적으로 처리
                    else:
                        self.update_text_json_structure(item, new_text)
            # "t" 키가 "r"이고 "c" 키가 있는 경우 (텍스트 배열을 포함하는 특별한 경우)
            elif "t" in json_data and json_data["t"] == "r" and "c" in json_data and isinstance(json_data["c"], list):
                # 텍스트 배열을 새 텍스트로 업데이트
                json_data["c"] = [new_text]
        # json_data가 리스트인 경우
        elif isinstance(json_data, list):
            # 리스트의 각 항목에 대해 재귀적으로 처리
            for item in json_data:
                if isinstance(item, (dict, list)):
                    self.update_text_json_structure(item, new_text)

    def remove_renderPos_tag(self, parent_tag, renderPos_tag):
        """랜더링 태그 삭제"""
        child_tag = parent_tag.find(renderPos_tag)
        if child_tag is not None:
            parent_tag.remove(child_tag)
            print(f"{renderPos_tag} 태그 삭제 완료")

    def save_xml(self, output_path):
        """수정된 XML 저장"""
        self.tree.write(output_path, encoding="utf-8", xml_declaration=True)

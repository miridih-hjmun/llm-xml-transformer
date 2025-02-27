import xml.etree.ElementTree as ET
import json
from services.llm_processor import LLMProcessor

class XMLParser:
    def __init__(self, file_path):
        self.file_path = file_path
        self.tree = ET.parse(file_path)
        self.root = self.tree.getroot()
        self.llm_processor = LLMProcessor()

    def process(self, output_path):
        """XML 처리 및 업데이트"""
        prompted_text_info_list = self.request_prompt()
        self.update_xml(prompted_text_info_list)
        self.save_xml(output_path)
    
    def extract_text(self):
        """XML에서 <SIMPLE_TEXT> 또는 <TEXT> 태그의 텍스트와 TbpeId를 추출"""
        text_tag_info = []

        # SIMPLE_TEXT 태그에서 텍스트와 TbpeId 추출
        for simple_text_tag in self.root.findall(".//SIMPLE_TEXT"):
            text_body = simple_text_tag.find(".//TextBody")
            if text_body is not None and text_body.text:
                try:
                    json_data = json.loads(text_body.text)
                    texts = self.extract_texts_from_json_structure(json_data)
                    tbpe_id = simple_text_tag.get('TbpeId')
                    text_tag_info.extend((text, tbpe_id) for text in texts)
                except json.JSONDecodeError:
                    continue

        # TEXT 태그에서 텍스트와 TbpeId 추출
        for text_tag in self.root.findall(".//TEXT"):
            text = text_tag.text
            tbpe_id = text_tag.get('TbpeId')
            if text is not None:
                text_tag_info.append((text, tbpe_id))

        return text_tag_info

    def extract_texts_from_json_structure(self, json_data):
        """재귀적으로 JSON 구조를 탐색하여 모든 텍스트(t 필드) 추출"""
        text = []
        if isinstance(json_data, list):
            for item in json_data:
                text.extend(self.extract_texts_from_json_structure(item))
        elif isinstance(json_data, dict):
            if "t" in json_data and isinstance(json_data["t"], str):
                text.append(json_data["t"])
            if "c" in json_data:
                text.extend(self.extract_texts_from_json_structure(json_data["c"]))
        return text

    def request_prompt(self):
        """텍스트를 추출하고 시뮬레이션된 응답을 생성"""
        text_info_list = self.extract_text()
        prompted_text_info_list = []

        for text, tbpe_id in text_info_list:
            prompted_text = self.llm_processor.prompt_text(text)
            prompted_text_info_list.append((prompted_text, tbpe_id))

        return prompted_text_info_list

    def update_xml(self, response_list):
        """시뮬레이션된 응답을 XML에 적용"""
        for prompted_text, tbpe_id in response_list:
            for text_tag in self.root.findall(".//TEXT") + self.root.findall(".//SIMPLE_TEXT"):
                if text_tag.get('TbpeId') == tbpe_id:
                    text_tag.text = prompted_text

    def save_xml(self, output_path):
        """수정된 XML 저장"""
        self.tree.write(output_path, encoding="utf-8", xml_declaration=True)

if __name__ == "__main__":
    parser = XMLParser("input.xml")
    texts = parser.extract_text()
    print(texts)
    parser.save_xml("output.xml")

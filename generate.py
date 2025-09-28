import fitz  # PyMuPDF
import csv
import re
import json
import csv
import os
from dataclasses import dataclass
from typing import List, Dict, Optional, Tuple
from copy import deepcopy

@dataclass
class TextElement:
    text: str
    size: float
    bbox: Tuple[float, float, float, float]

class FrenchVerbExtractor:
    def __init__(self, pdf_path: str):
        self.doc = fitz.open(pdf_path)

        # 定义CSV表头
        self.csv_headers = [
            'verbe', 'indice', 'caracterisation',
            # INDICATIF
            'indicatif_present_1s', 'indicatif_present_2s', 'indicatif_present_3s',
            'indicatif_present_1p', 'indicatif_present_2p', 'indicatif_present_3p',
            'indicatif_passe_compose_1s', 'indicatif_passe_compose_2s', 'indicatif_passe_compose_3s',
            'indicatif_passe_compose_1p', 'indicatif_passe_compose_2p', 'indicatif_passe_compose_3p',
            'indicatif_imparfait_1s', 'indicatif_imparfait_2s', 'indicatif_imparfait_3s',
            'indicatif_imparfait_1p', 'indicatif_imparfait_2p', 'indicatif_imparfait_3p',
            'indicatif_plus_que_parfait_1s', 'indicatif_plus_que_parfait_2s', 'indicatif_plus_que_parfait_3s',
            'indicatif_plus_que_parfait_1p', 'indicatif_plus_que_parfait_2p', 'indicatif_plus_que_parfait_3p',
            'indicatif_passe_simple_1s', 'indicatif_passe_simple_2s', 'indicatif_passe_simple_3s',
            'indicatif_passe_simple_1p', 'indicatif_passe_simple_2p', 'indicatif_passe_simple_3p',
            'indicatif_passe_anterieur_1s', 'indicatif_passe_anterieur_2s', 'indicatif_passe_anterieur_3s',
            'indicatif_passe_anterieur_1p', 'indicatif_passe_anterieur_2p', 'indicatif_passe_anterieur_3p',
            'indicatif_futur_simple_1s', 'indicatif_futur_simple_2s', 'indicatif_futur_simple_3s',
            'indicatif_futur_simple_1p', 'indicatif_futur_simple_2p', 'indicatif_futur_simple_3p',
            'indicatif_futur_anterieur_1s', 'indicatif_futur_anterieur_2s', 'indicatif_futur_anterieur_3s',
            'indicatif_futur_anterieur_1p', 'indicatif_futur_anterieur_2p', 'indicatif_futur_anterieur_3p',
            # CONDITIONNEL
            'conditionnel_present_1s', 'conditionnel_present_2s', 'conditionnel_present_3s',
            'conditionnel_present_1p', 'conditionnel_present_2p', 'conditionnel_present_3p',
            'conditionnel_passe_1s', 'conditionnel_passe_2s', 'conditionnel_passe_3s',
            'conditionnel_passe_1p', 'conditionnel_passe_2p', 'conditionnel_passe_3p',
            # SUBJONCTIF
            'subjonctif_present_1s', 'subjonctif_present_2s', 'subjonctif_present_3s',
            'subjonctif_present_1p', 'subjonctif_present_2p', 'subjonctif_present_3p',
            'subjonctif_passe_1s', 'subjonctif_passe_2s', 'subjonctif_passe_3s',
            'subjonctif_passe_1p', 'subjonctif_passe_2p', 'subjonctif_passe_3p',
            'subjonctif_imparfait_1s', 'subjonctif_imparfait_2s', 'subjonctif_imparfait_3s',
            'subjonctif_imparfait_1p', 'subjonctif_imparfait_2p', 'subjonctif_imparfait_3p',
            'subjonctif_plus_que_parfait_1s', 'subjonctif_plus_que_parfait_2s', 'subjonctif_plus_que_parfait_3s',
            'subjonctif_plus_que_parfait_1p', 'subjonctif_plus_que_parfait_2p', 'subjonctif_plus_que_parfait_3p',
            # IMPERATIF
            'imperatif_present_2s', 'imperatif_present_1p', 'imperatif_present_2p',
            'imperatif_passe_2s', 'imperatif_passe_1p', 'imperatif_passe_2p',
            # INFINITIF
            'infinitif_present', 'infinitif_passe',
            # PARTICIPE
            'participe_present', 'participe_passe', 'participe_passe_compose',
            # OTHERS
            'notes', 'labels',
        ]

        self.pdf_position = {
            "indicatif_present": (40, 145, 180, 285),
            "indicatif_passe_compose": (190, 145, 340, 285),
            "indicatif_imparfait": (40, 300, 180, 440),
            "indicatif_plus_que_parfait": (190, 300, 340, 440),
            "indicatif_passe_simple": (40, 460, 180, 600),
            "indicatif_passe_anterieur": (190, 460, 340, 600),
            "indicatif_futur_simple": (40, 615, 180, 760),
            "indicatif_futur_anterieur": (190, 615, 340, 760),
            "conditionnel_present": (40, 770, 180, 920),
            "conditionnel_passe": (190, 770, 340, 920),
            "subjonctif_present": (350, 145, 500, 285),
            "subjonctif_passe": (500, 145, 700, 285),
            "subjonctif_imparfait": (350, 305, 500, 440),
            "subjonctif_plus_que_parfait": (500, 305, 700, 440),
            "imperatif_present_2s": (350, 505, 500, 520),
            "imperatif_present_1p": (350, 524, 500, 539),
            "imperatif_present_2p": (350, 542, 500, 560),
            "imperatif_passe_2s": (500, 505, 700, 520),
            "imperatif_passe_1p": (500, 524, 700, 539),
            "imperatif_passe_2p": (500, 542, 700, 560),
            "infinitif_present": (350, 623, 500, 640),
            "infinitif_passe": (500, 623, 700, 640),
            "participe_present": (350, 705, 500, 722),
            "participe_passe": (500, 705, 700, 722),
            "participe_passe_compose": (500, 725, 700, 740),
        }

    def combine_line(self, current_line, elements):
        # 每一行元素先按左端横坐标排序
        current_line.sort(key = lambda x: (x.bbox[0]))

        temp_elem = TextElement(
            text = "",
            size = 0.0,
            bbox = (0.0, 0.0, 0.0, 0.0)
        )

        for text_span in current_line:
            # 计算：当前横坐标左端 - 上一个元素块横坐标右端
            position_diff = text_span.bbox[0] - temp_elem.bbox[2]
            if position_diff > -1 and position_diff < 5:
                # 满足连缀条件，进行连缀合并
                if position_diff < 0.5:
                    temp_elem.text = f"{temp_elem.text}{text_span.text}" # 两个文字块是连着的，直接拼接
                else:
                    temp_elem.text = f"{temp_elem.text} {text_span.text}" # 两个文字块之间有一定间距，并利用这个间距作为空格
                temp_elem.size = max(temp_elem.size, text_span.size)
                temp_elem.bbox = (
                    temp_elem.bbox[0],
                    min(temp_elem.bbox[1], text_span.bbox[1]), # 上边沿纵坐标取两者中较小
                    text_span.bbox[2],
                    max(temp_elem.bbox[3], text_span.bbox[3]) # 下边沿纵坐标取两者中较大
                )
            else:
                # 不满足连缀条件，把 temp_elem 存入 elements
                if temp_elem.text != "":
                    elements.append(deepcopy(temp_elem))
                temp_elem.text = text_span.text
                temp_elem.size = text_span.size
                temp_elem.bbox = text_span.bbox

        if temp_elem.text != "":
            elements.append(deepcopy(temp_elem))

    def extract_text_elements(self, page) -> List[TextElement]:
        """提取页面所有文字元素"""
        elements = []
        blocks = page.get_text("dict")
        current_line = []
        current_y_position = 0.0
        for block in blocks["blocks"]:
            if "lines" in block:
                for line in block["lines"]:
                    for span in line["spans"]:
                        text = span["text"]
                        if text:
                            if abs(current_y_position - span["bbox"][1]) > 5:
                                self.combine_line(current_line, elements)
                                current_line = []
                            current_line.append(TextElement(
                                text = text,
                                size = span["size"],
                                bbox = span["bbox"]
                            ))
                            current_y_position = span["bbox"][1]
        if len(current_line) > 0:
            self.combine_line(current_line, elements)

        # print(elements)
        return elements

    def extract_verb_info(self, page_num: int) -> Optional[Dict]:
        """从单页提取动词信息"""
        page = self.doc[page_num]
        elements = self.extract_text_elements(page)

        if not elements:
            return None

        # 提取基本信息
        verb_info = {}

        # 1. 提取indice (绿色圆圈中的数字)
        verb_info['indice'] = self.extract_indice(elements)

        # 2. 提取动词名称
        verb_info['verbe'] = self.extract_verb_name(elements)

        # 3. 提取特征描述
        verb_info['caracterisation'] = self.extract_caracterisation(elements)

        # 4. 提取变位表格
        conjugations = self.extract_conjugations(elements)
        verb_info.update(conjugations)
        if conjugations['infinitif_present'] != verb_info['verbe']:
            print(f"infinitif_present: {conjugations['infinitif_present']}, and verbe: {verb_info['verbe']}.")
            if verb_info['verbe'] == "":
                verb_info['verbe'] = conjugations['infinitif_present']

        # 5. 笔记和标签创建
        verb_info['notes'] = ""
        verb_info['labels'] = ""

        return verb_info

    def extract_indice(self, elements: List[TextElement]) -> str:
        """提取左上角绿色圆圈中的数字"""
        for element in elements:
            if (element.text.isdigit() and
                len(element.text) <= 3 and
                element.size > 20):
                return element.text
        return ""

    def extract_verb_name(self, elements: List[TextElement]) -> str:
        """提取动词名称"""
        for element in elements:
            if (element.size >= 30 and
                len(element.text) > 3 and
                element.bbox[1] > 25 and
                element.bbox[3] < 75):
                return element.text
        return ""

    def extract_caracterisation(self, elements: List[TextElement]) -> str:
        """提取动词特征描述"""
        blocks = []
        for element in elements:
            if (element.size > 14 and element.size < 17 and
                element.bbox[1] > 75 and element.bbox[3] < 120 and
                element.bbox[2] < 450):
                if element.text.strip() == "":
                    blocks.append("|")
                else:
                    blocks.append(element.text.strip())
        return " ".join(blocks)

    def decide_tense_by_position(self, element) -> str:
        for tense, position in self.pdf_position.items():
            if (element.bbox[0] > position[0] and
                element.bbox[1] > position[1] and
                element.bbox[2] < position[2] and
                element.bbox[3] < position[3]):
                return tense
        return ""

    def extract_conjugations(self, elements: List[TextElement]) -> Dict:
        """提取所有变位"""
        conjugations = {}
        for header in self.csv_headers[3: -2]:
            conjugations[header] = ""
            conjugations[f"{header}_audio"] = ""

        for element in elements:
            tense = self.decide_tense_by_position(element)
            if tense == "":
                continue

            non_person_tenses = [
                "imperatif_present_2s", "imperatif_present_1p", "imperatif_present_2p",
                "imperatif_passe_2s",   "imperatif_passe_1p",   "imperatif_passe_2p",
                "infinitif_present",    "infinitif_passe",      "participe_present",
                "participe_passe",      "participe_passe_compose",
            ]
            if tense in non_person_tenses:
                conjugations[tense] = element.text
                continue

            person_patterns = [
                ("je",        "1s"), ("j’",   "1s"), ("tu",   "2s"),
                ("il/elle",   "3s"), ("nous", "1p"), ("vous", "2p"),
                ("ils/elles", "3p"),
            ]
            for pattern, person in person_patterns:
                if pattern in element.text:
                    conjugations[f'{tense}_{person}'] = element.text
                    break
                else:
                    continue

        return conjugations

    def extract_all_verbs(self, start_page: int = 0, end_page: int = 1000) -> List[Dict]:
        """提取所有动词"""
        all_verbs = []

        for page_num in range(start_page, end_page + 1):
            if page_num in [41, 42]:  # PDF页码从0开始，所以52、53页对应51、52
                continue

            print(f"正在处理第 {page_num} 页...")

            try:
                verb_info = self.extract_verb_info(page_num)
                if verb_info and verb_info.get('verbe'):
                    all_verbs.append(verb_info)
                    print(f"  提取动词: {verb_info['verbe']}")
            except Exception as e:
                print(f"  处理第 {page_num + 1} 页时出错: {e}")

        return all_verbs

class CSVAttributeManager:
    def __init__(self, csv_file):
        self.csv_file = csv_file
        self.data = {}
        self.elements = []
        self.attributes = []
        self._load_data()

    def _load_data(self):
        """从CSV文件加载数据到内存"""
        if not os.path.exists(self.csv_file):
            # 如果文件不存在，创建空的数据结构
            self.data = {}
            self.elements = []
            self.attributes = []
            return

        with open(self.csv_file, 'r', newline='', encoding='utf-8') as file:
            reader = csv.reader(file)
            rows = list(reader)

            if not rows:
                self.data = {}
                self.elements = []
                self.attributes = []
                return

            # 第一行是属性名（第一列为空）
            self.attributes = rows[0][1:]

            # 读取数据
            self.elements = []
            self.data = {}

            for row in rows[1:]:
                if row:  # 跳过空行
                    element = row[0]
                    self.elements.append(element)
                    self.data[element] = {}

                    for i, attr_value in enumerate(row[1:]):
                        if i < len(self.attributes):
                            attr_name = self.attributes[i]
                            self.data[element][attr_name] = attr_value

    def _save_data(self):
        """将数据保存回CSV文件"""
        with open(self.csv_file, 'w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)

            # 写入属性行
            writer.writerow([''] + self.attributes)

            # 写入数据行
            for element in self.elements:
                row = [element]
                for attr in self.attributes:
                    row.append(self.data.get(element, {}).get(attr, ''))
                writer.writerow(row)

    def read_attribute(self, element, attribute):
        """读取指定元素的指定属性值"""
        if element not in self.data:
            raise ValueError(f"元素 '{element}' 不存在")

        if attribute not in self.attributes:
            raise ValueError(f"属性 '{attribute}' 不存在")

        return self.data[element].get(attribute, '')

    def write_attribute(self, element, attribute, value):
        """写入指定元素的指定属性值"""
        # 如果元素不存在，创建新元素
        if element not in self.data:
            self.elements.append(element)
            self.data[element] = {}

        # 如果属性不存在，添加到属性列表
        if attribute not in self.attributes:
            self.attributes.append(attribute)
            # 为所有现有元素添加这个新属性
            for existing_element in self.elements:
                if existing_element != element:
                    self.data[existing_element][attribute] = ''

        # 设置属性值
        self.data[element][attribute] = str(value)
        self._save_data()

    def add_element(self, element):
        """添加新元素"""
        if element in self.data:
            raise ValueError(f"元素 '{element}' 已存在")

        self.elements.append(element)
        self.data[element] = {attr: '' for attr in self.attributes}
        self._save_data()

    def add_attribute(self, attribute):
        """添加新属性"""
        if attribute in self.attributes:
            raise ValueError(f"属性 '{attribute}' 已存在")

        self.attributes.append(attribute)
        for element in self.elements:
            self.data[element][attribute] = ''
        self._save_data()

    def get_all_elements(self):
        """获取所有元素列表"""
        return self.elements.copy()

    def get_all_attributes(self):
        """获取所有属性列表"""
        return self.attributes.copy()

    def get_element_data(self, element):
        """获取元素的所有属性数据"""
        if element not in self.data:
            raise ValueError(f"元素 '{element}' 不存在")
        return self.data[element].copy()

    def delete_element(self, element):
        """删除元素"""
        if element not in self.data:
            raise ValueError(f"元素 '{element}' 不存在")

        self.elements.remove(element)
        del self.data[element]
        self._save_data()

    def delete_attribute(self, attribute):
        """删除属性"""
        if attribute not in self.attributes:
            raise ValueError(f"属性 '{attribute}' 不存在")

        self.attributes.remove(attribute)
        for element in self.elements:
            if attribute in self.data[element]:
                del self.data[element][attribute]
        self._save_data()

def main():
    # 使用示例
    pdf_path = "bescherelle.pdf"
    output_csv = "french_verbs_conjugations.csv"

    extractor = FrenchVerbExtractor(pdf_path)
    manager = CSVAttributeManager(output_csv)

    print("开始提取法语动词变位...")

    try:
        # 提取所有动词
        verbs = extractor.extract_all_verbs(start_page=10, end_page=116)
        print(f"\n总共提取了 {len(verbs)} 个动词")

        # 保存到CSV
        for verb in verbs:
            element = verb['verbe']
            for attr_name, attr_value in verb.items():
                if attr_name == 'verbe':
                    continue
                manager.write_attribute(element, attr_name, attr_value)
        # manager.read_attribute(element, attribute)
        print(f"结果已保存到 {output_csv}")

        # 提取目录页


        # 保存目录页结果到 CSV


        ##########################################################################
        # 上面完成了 PDF 相关的工作，接下来针对 CSV 进行补充调整
        ##########################################################################

        # 到网上查询其他单词


        # 获取发音并填充

    except Exception as e:
        print(f"处理过程中出错: {e}")

if __name__ == "__main__":
    main()

import os
import csv
import requests
import json
from urllib.parse import urlparse
from time import sleep
from bs4 import BeautifulSoup
from bs4 import Comment

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

verbe_attribute = [
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
]

def deal_with_conjugation(conjugation_data, item_title, section_soup):
    content_verb = section_soup.find_all("div", class_="content-verbe")[0]
    conjuctions = content_verb.find_all("div", class_="d-flex p-2")  # 不同的人称

    if item_title == "participe_present":
        conjuction = conjuctions[0]
        verbs = conjuction.p.find_all("verb")
        conjugation_data['participe_present'] = verbs[0].string.strip()
        return
    if item_title == "participe_passe":
        conjuction = conjuctions[0]
        verbs = conjuction.p.find_all("verb")
        conjugation_data['participe_passe'] = verbs[0].string.strip()
        conjugation_data['participe_passe_compose'] = verbs[1].string.strip()
        return
    if item_title == "infinitif_present":
        conjuction = conjuctions[0]
        verbs = conjuction.p.find_all("verb")
        conjugation_data['infinitif_present'] = verbs[0].string.strip()
        return
    if item_title == "infinitif_passe":
        conjuction = conjuctions[0]
        verbs = conjuction.p.find_all("verb")
        conjugation_data['infinitif_passe'] = verbs[0].string.strip()
        return

    conj_list = []
    for conjuction in conjuctions:
        paras = conjuction.p.stripped_strings
        conj_per_person = ""
        for word in paras:
            conj_per_person = f"{conj_per_person} {word}"
        conj_list.append(conj_per_person.strip().replace("’ ", "’"))

    if item_title == "imperatif_present":
        if len(conj_list) != 3:
            print("imperatif_present 不是 3 个，请检查")
            return
        conjugation_data['imperatif_present_2s'] = conj_list[0]
        conjugation_data['imperatif_present_1p'] = conj_list[1]
        conjugation_data['imperatif_present_2p'] = conj_list[2]
        return
    if item_title == "imperatif_passe":
        if len(conj_list) != 3:
            print("imperatif_passe 不是 3 个，请检查")
            return
        conjugation_data['imperatif_passe_2s'] = conj_list[0]
        conjugation_data['imperatif_passe_1p'] = conj_list[1]
        conjugation_data['imperatif_passe_2p'] = conj_list[2]
        return

    person_patterns = [
        ("je",        "1s"), ("j’",   "1s"), ("tu",   "2s"),
        ("il/elle",   "3s"), ("nous", "1p"), ("vous", "2p"),
        ("ils/elles", "3p"), ("n.",   "1p"), ("v.",   "2p"),
        ("que je",       "1s"), ("que j’",   "1s"), ("que tu",   "2s"),
        ("qu’il/elle",   "3s"), ("que nous", "1p"), ("que vous", "2p"),
        ("qu’ils/elles", "3p"), ("que n.",   "1p"), ("que v.",   "2p"),
        ("ils (elles)",  "3p"), ("il (elle)", "3s"), ("qu’ils (elles)", "3p"),
        ("qu’il (elle)", "3s"),
        ("ils", "3p"), ("il", "3s"), ("qu’ils", "3p"), ("qu’il", "3s"),
    ]
    for conj in conj_list:
        # print(conj)
        for pattern, person in person_patterns:
            if conj.startswith(pattern):
                conjugation_data[f'{item_title}_{person}'] = conj
                break
            else:
                continue


def extract_verb_conjugation(html_content):
    """
    从HTML内容中提取动词变位信息
    """
    sections_dict = {}
    soup = BeautifulSoup(html_content, 'html.parser')
    for comment in soup.find_all(string = lambda text: isinstance(text, Comment)):
        comment.extract()

    # print(soup.prettify())
    main_sections = soup.find_all("section", class_="section")
    if len(main_sections) == 1:
        main_section = main_sections[0]
    else:
        print("main sections 不止一个，请检查。")
        return {}

    article = main_section.article
    all_conj = article.find_all("div", class_="tab-content", id="nav-tabContent-active-passive")[0]
    active_conj = all_conj.find_all("div", class_="active")[0]
    tab_content = active_conj.find_all("div", class_="tab-content")[0]

    temp_simple = tab_content.find_all("div", class_="tab-pane")[0].find_all("div", class_="container-tabs")[0]

    left_simple = temp_simple.find_all("div", class_="first-temps-simple")[0]
    indicatif_list = left_simple.find_all("div", class_="indicatif-present")
    if len(indicatif_list) > 0:
        indicatif_list = indicatif_list[0].find_all("div", class_="col-xs-12")
        for small_section in indicatif_list:
            h5_text = small_section.h5.string.strip()
            if h5_text == "Présent":
                sections_dict["indicatif_present"] = small_section
            elif h5_text == "Imparfait":
                sections_dict["indicatif_imparfait"] = small_section
            elif h5_text == "Passé simple":
                sections_dict["indicatif_passe_simple"] = small_section
            elif h5_text == "Futur simple":
                sections_dict["indicatif_futur_simple"] = small_section
    conditionnel_list = left_simple.find_all("div", class_="conditionnel-present")
    if len(conditionnel_list) > 0:
        conditionnel_list = conditionnel_list[0].find_all("div", class_="col-xs-12")
        for small_section in conditionnel_list:
            h5_text = small_section.h5.string.strip()
            if h5_text == "Présent":
                sections_dict["conditionnel_present"] = small_section

    right_simple = temp_simple.find_all("div", class_="second-temps-simple")[0]
    subjonctif_list = right_simple.find_all("div", class_="subjonctif-present")
    if len(subjonctif_list) > 0:
        subjonctif_list = subjonctif_list[0].find_all("div", class_="col-xs-12")
        for small_section in subjonctif_list:
            h5_text = small_section.h5.string.strip()
            if h5_text == "Présent":
                sections_dict["subjonctif_present"] = small_section
            elif h5_text == "Imparfait":
                sections_dict["subjonctif_imparfait"] = small_section
    imperatif_list = right_simple.find_all("div", class_="imperatif-present")
    if len(imperatif_list) > 0:
        imperatif_list = imperatif_list[0].find_all("div", class_="col-xs-12")
        for small_section in imperatif_list:
            h5_text = small_section.h5.string.strip()
            if h5_text == "Présent":
                sections_dict["imperatif_present"] = small_section
    infinitif_list = right_simple.find_all("div", class_="infinitif-present")
    if len(infinitif_list) > 0:
        infinitif_list = infinitif_list[0].find_all("div", class_="col-xs-12")
        for small_section in infinitif_list:
            h5_text = small_section.h5.string.strip()
            if h5_text == "Présent":
                sections_dict["infinitif_present"] = small_section
    participe_list = right_simple.find_all("div", class_="participe-present")
    if len(participe_list) > 0:
        participe_list = participe_list[0].find_all("div", class_="col-xs-12")
        for small_section in participe_list:
            h5_text = small_section.h5.string.strip()
            if h5_text == "Présent":
                sections_dict["participe_present"] = small_section

    temp_compose = tab_content.find_all("div", class_="tab-pane")[1]

    left_compose = temp_compose.find_all("div", class_="first-temps-simple")[0]
    indicatif_list = left_compose.find_all("div", class_="indicatif-passe")
    if len(indicatif_list) > 0:
        indicatif_list = indicatif_list[0].find_all("div", class_="col-xs-12")
        for small_section in indicatif_list:
            h5_text = small_section.h5.string.strip()
            if h5_text == "Passé composé":
                sections_dict["indicatif_passe_compose"] = small_section
            elif h5_text == "Plus-que-parfait":
                sections_dict["indicatif_plus_que_parfait"] = small_section
            elif h5_text == "Passé antérieur":
                sections_dict["indicatif_passe_anterieur"] = small_section
            elif h5_text == "Futur antérieur":
                sections_dict["indicatif_futur_anterieur"] = small_section
    conditionnel_list = left_compose.find_all("div", class_="conditionnel-passe")
    if len(conditionnel_list) > 0:
        conditionnel_list = conditionnel_list[0].find_all("div", class_="col-xs-12")
        for small_section in conditionnel_list:
            h5_text = small_section.h5.string.strip()
            if h5_text == "Passé":
                sections_dict["conditionnel_passe"] = small_section

    right_compose = temp_compose.find_all("div", class_="second-temps-simple")[0]
    subjonctif_list = right_compose.find_all("div", class_="subjonctif-passe")
    if len(subjonctif_list) > 0:
        subjonctif_list = subjonctif_list[0].find_all("div", class_="col-xs-12")
        for small_section in subjonctif_list:
            h5_text = small_section.h5.string.strip()
            if h5_text == "Passé":
                sections_dict["subjonctif_passe"] = small_section
            elif h5_text == "Plus-que-parfait":
                sections_dict["subjonctif_plus_que_parfait"] = small_section
    imperatif_list = right_compose.find_all("div", class_="imperatif-passe")
    if len(imperatif_list) > 0:
        imperatif_list = imperatif_list[0].find_all("div", class_="col-xs-12")
        for small_section in imperatif_list:
            h5_text = small_section.h5.string.strip()
            if h5_text == "Passé":
                sections_dict["imperatif_passe"] = small_section
    infinitif_list = right_compose.find_all("div", class_="infinitif-passe")
    if len(infinitif_list) > 0:
        infinitif_list = infinitif_list[0].find_all("div", class_="col-xs-12")
        for small_section in infinitif_list:
            h5_text = small_section.h5.string.strip()
            if h5_text == "Passé":
                sections_dict["infinitif_passe"] = small_section
    participe_list = right_compose.find_all("div", class_="participe-passe")
    if len(participe_list) > 0:
        participe_list = participe_list[0].find_all("div", class_="col-xs-12")
        for small_section in participe_list:
            h5_text = small_section.h5.string.strip()
            if h5_text == "Passé":
                sections_dict["participe_passe"] = small_section

    conjugation_data = {}
    for attr in verbe_attribute:
        conjugation_data[attr] = ""

    for item_title, section_soup in sections_dict.items():
        deal_with_conjugation(conjugation_data, item_title, section_soup)

    return conjugation_data

def look_in_web(url):
    try:
        r = requests.get(url)
        conjugation_data = extract_verb_conjugation(r.text)
        # for key, value in conjugation_data.items():
        #     print(f"{key}: {value}")
        return conjugation_data
    except requests.exceptions.RequestException as e:
        print(f"网络请求错误: {e}")


def main(look_in_list):
    conjugation_csv = "conjugations_to_anki.csv"
    repertoire_csv = "french_verbs_conjugations.csv"
    conjugation_manager = CSVAttributeManager(conjugation_csv)
    repertoire_manager = CSVAttributeManager(repertoire_csv)

    for verb, url in look_in_list.items():
        if not verb:
            continue
        if verb[0] == "h":
            try:
                caracterisation = repertoire_manager.read_attribute(verb, "caracterisation")
                print(f"能在目录库中读到，是哑音 h 无需特殊处理")
            except ValueError:
                verb = f"* {verb}"
                try:
                    caracterisation = repertoire_manager.read_attribute(verb, "caracterisation")
                    print(f"嘘音 h 可以在目录库中读到，按 verb = {verb} 处理")
                except ValueError:
                    print(f"哑音、嘘音 h 也读不到，请检查，verb = {verb}")
                    continue
        if url == "":
            url = f"https://conjugaison.bescherelle.com/verbes/{verb}"\
                .replace("â", "a").replace("ä", "a").replace("à", "a")\
                .replace("é", "e").replace("è", "e").replace("ê", "e").replace("ë", "e")\
                .replace("î", "i").replace("ï", "i").replace("ô", "i").replace("ö", "i")\
                .replace("û", "u").replace("ç", "c").replace("*", "").strip()
        try:
            caracterisation = conjugation_manager.read_attribute(verb, "caracterisation")
            print(f"=========={verb} 可以在 conjugations_to_anki.csv 中读到，说明已经在 anki 列表中了，跳过")
            continue
        except ValueError:
            # 这里才是预期
            try:
                caracterisation = repertoire_manager.read_attribute(verb, "caracterisation")
                notes = repertoire_manager.read_attribute(verb, "notes")
                labels = repertoire_manager.read_attribute(verb, "labels")
                print(f"=========={verb} 读到：caracterisation = {caracterisation}, notes = {notes}, labels = {labels}, url = {url}")
                conjugations = look_in_web(url)
                if conjugations:
                    conjugation_manager.write_attribute(verb, "caracterisation", caracterisation)
                    conjugation_manager.write_attribute(verb, "notes", notes)
                    conjugation_manager.write_attribute(verb, "labels", labels)
                    for attr, value in conjugations.items():
                        # print(f"{key}: {value}")
                        conjugation_manager.write_attribute(verb, attr, value)
                    print(f"写入成功：{verb}")
            except ValueError:
                print(f"=========={verb} 在 french_verbs_conjugations.csv 中读不到")
                # conjugations = look_in_web(url)

def small_fix():
    conjugation_csv = "conjugations_to_anki.csv"
    repertoire_csv = "french_verbs_conjugations.csv"
    conjugation_manager = CSVAttributeManager(conjugation_csv)
    repertoire_manager = CSVAttributeManager(repertoire_csv)

    for verb in conjugation_manager.elements:
        indice = conjugation_manager.read_attribute(verb, "indice")
        for attr in conjugation_manager.attributes:
            value = conjugation_manager.read_attribute(verb, attr)
            if value:
                continue
            else:
                if attr == "notes" or attr == "caracterisation" or attr == "labels" or attr.endswith("_audio"):
                    continue
                print(f"empty: verb = {verb}, indice = {indice}, attr = {attr}")

    print("=======================")

    for verb in repertoire_manager.elements:
        label = repertoire_manager.read_attribute(verb, "labels")
        if label:
            continue
        else:
            print(verb)


if __name__ == "__main__":
    look_in_list = {
        "rentrer": "",
        "": "",
        "": "",
        "": "",
        "": "",
        "": "",
        "": "",
        "": "",
        "": "",
        "": "",
        "": "",
        "": "",
        "": "",
        "": "",
        "": "",
        # "répartir": "https://conjugaison.bescherelle.com/verbes/repartir-0",
        # "se manger": "https://conjugaison.bescherelle.com/verbes/se-manger",
    }
    main(look_in_list)
    # small_fix()

import os
import csv
import requests
import json
from urllib.parse import urlparse
from time import sleep

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

def download_file(url, save_path):
    try:
        # Send GET request to the URL
        response = requests.get(url)

        # Check if the request was successful (status code 200)
        if response.status_code == 200:
            # Write the content of the response to a local file
            with open(save_path, 'wb') as file:
                file.write(response.content)
            print(f"File downloaded successfully: {save_path}")
            return 0
        else:
            print(f"Failed to download file. Status code: {response.status_code}")
            return 1
    except Exception as e:
        print(f"Error: {e}")
        return 1

def tts(text):
    url = "https://api.soundoftext.com/sounds"
    payload = {
        "engine": "Google",
        "data": {
            "text": text,
            "voice": "fr-FR"
        }
    }
    headers = {
        "Content-Type": "application/json"
    }
    try:
        fulfill_post = requests.post(url, json=payload, headers=headers)
        if fulfill_post.json()["success"]:
            sound_id = fulfill_post.json()["id"]
            sleep(2)
            download_request = requests.get(f"{url}/{sound_id}")
            if download_request.json()["status"] == "Done":
                file_url = download_request.json()["location"]
                url_tuple = urlparse(file_url)
                save_path = f"sound_download/fr-conj-{url_tuple.path[1:]}"
                ret = download_file(file_url, save_path)
                return ret, url_tuple.path
            elif download_request.json()["status"] == "Pending":
                print(f"声音文件暂未生成，稍后再试。sound_id：{sound_id}")
                return 1, None
            elif download_request.json()["status"] == "Error":
                print(f"声音下载失败，返回消息为：{download_request.json()["message"]}")
                return 1, None
        else:
            print(f"post 失败，返回消息为：{fulfill_post.json()["message"]}")
            return 1, None
    except requests.exceptions.RequestException as e:
        print(f"网络请求错误: {e}")
        print("等待两分钟……")
        sleep(120)
        return 1, None
    except ValueError as e:
        print(f"JSON解析错误: {e}")
        return 1, None

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

def split_3_person_to_two(str, split_sign):
    if split_sign == "ils/elles" or split_sign == "ils (elles)":
        person_list = ["ils", "elles"]
    elif split_sign == "il/elle" or split_sign == "il (elle)":
        person_list = ["il", "elle"]

    prefix = str.split(split_sign)[0]
    word_root = str.split(split_sign)[1]
    if "(e)" in word_root:
        word_root_list = [word_root.replace("(e)", ""), word_root.replace("(e)", "e")]
    else:
        word_root_list = [word_root, word_root]

    return f"{prefix}{person_list[0]}{word_root_list[0]} / {prefix}{person_list[1]}{word_root_list[1]}"


def split_3sp(combine_str):
    combine_str = combine_str.replace("n.", "nous").replace("v.", "vous")\
        .replace("(e)(s)", "(e, s, es)").replace(" (u, ue, us, ues)", "(e, s, es)")\
        .replace(" (é, ée, és, ées)", "(e, s, es)")
    if "ils/elles" in combine_str:
        return split_3_person_to_two(combine_str, "ils/elles")
    elif "il/elle" in combine_str:
        return split_3_person_to_two(combine_str, "il/elle")
    elif "ils (elles)" in combine_str:
        return split_3_person_to_two(combine_str, "ils (elles)")
    elif "il (elle)" in combine_str:
        return split_3_person_to_two(combine_str, "il (elle)")
    else:
        if "(e)" in combine_str:
            prefix = combine_str.split("(e)")[0]
            word_root = combine_str.split("(e)")[1]
            return f"{prefix}{word_root} / {prefix}e{word_root}"
        elif "(e, s, es)" in combine_str:
            prefix = combine_str.split("(e, s, es)")[0]
            word_root = combine_str.split("(e, s, es)")[1]
            return f"{prefix}{word_root} / {prefix}e{word_root} / {prefix}s{word_root} / {prefix}es{word_root}"
        elif "(e, es)" in combine_str:
            prefix = combine_str.split("(e, es)")[0]
            word_root = combine_str.split("(e, es)")[1]
            return f"{prefix}{word_root} / {prefix}e{word_root} / {prefix}es{word_root}"
        else:
            return combine_str

def main():
    conjugation_csv = "conjugations_to_anki.csv"
    manager = CSVAttributeManager(conjugation_csv)

    for verb in manager.elements:
        for attribute in verbe_attribute:
            text = manager.read_attribute(verb, attribute)
            sound = manager.read_attribute(verb, f"{attribute}_audio")
            if text and not sound:
                ret, path = tts(split_3sp(text))
                if ret == 0 and path:
                    path = path.replace("/", "")
                    manager.write_attribute(verb, f"{attribute}_audio", f"[sound:fr-conj-{path}]")
            # if text == ".":
            #     manager.write_attribute(verb, f"{attribute}", "")
            #     manager.write_attribute(verb, f"{attribute}_audio", "")
            #     print(f"delete . of verb: {verb}, attr: {attribute}, text: {text}, sound: {sound}")

def small_fix():
    conjugation_csv = "conjugations_to_anki.csv"
    manager = CSVAttributeManager(conjugation_csv)

    for verb in manager.elements:
        for attribute in verbe_attribute:
            text = manager.read_attribute(verb, attribute)
            if "(e," in text:
                manager.write_attribute(verb, f"{attribute}_audio", "")


if __name__ == "__main__":
    main()
    # small_fix()
    examples = [
        "j’avais joué",
        "il/elle avait navigué",
        "il/elle avait été aimé(e)",
        "tu avais été aimé(e)",
        "nous étions allé(e)s",
        "qu’ils/elles eussent été aimé(e)s",
        "étant allé(e, s, es)",
        "clos(e, es)",
        "il (elle) est venu(e)",
        "ils (elles) ont écouté",
        "ils (elles) s’en sont allé(e)s",
        "nous étions venu(e)s",
        "s’en étant allé(e)(s)",
        "venu (u, ue, us, ues)",
        "",
        ""
    ]
    for example in examples:
        # print(split_3sp(example))
        pass

"""
每个单词有 95 个变位，每个变位 2 秒钟，一共 190 秒，大约三四分钟能下载完一个单词的所有变位。
一共 105 个单词，400 分钟能下载完所有，大约是七个小时？也时间有点太长了吧。不过值得。冲吧。
"""

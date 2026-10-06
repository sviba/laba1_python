import json
import xml.etree.ElementTree as ET
from abc import ABC, abstractmethod # Abstract Base Classes
from pathlib import Path

class SportSectionError(Exception):
    """Базовое собственное исключение для спортивного комплекса."""

class EmptyNameError(SportSectionError):
    """Название секции не может быть пустым."""

class InvalidPriceError(SportSectionError):
    """Стоимость абонемента вне допустимого диапазона."""

class InvalidAgeLimitError(SportSectionError):
    """Некорректное возрастное ограничение."""

class DataFormatError(SportSectionError):
    """Ошибка формата данных при чтении/записи файла."""

class InvalidskillimitError(SportSectionError):
    """Неподходящий уровень поступающего"""

class SportSection(ABC):    
    def __init__(self, name: str, coach: str, price: int) -> None:
        if not name or not name.strip(): # .strip() - убирает пробелы в начале и конце строки
            raise EmptyNameError("Название секции не может быть пустым") # raise == throw в С++
        if price < 0 or price > 100000:
            raise InvalidPriceError(
                f"Стоимость {price} руб. невозможна"
            )
        self.name = name.strip()
        self.coach = coach.strip()
        self.price = price

    @abstractmethod # следующий метод - виртуальный
    def get_info(self) -> str:
        """Абстрактный метод: краткая информация о секции."""

    def __str__(self) -> str:
        return self.get_info()

# skill: low, middle, hard, champion
class Fight_Section(SportSection):
    def __init__(self,name: str,coach: str,price: int,skill: str,age: int) -> None:
        super().__init__(name,coach,price)
        if skill == "low":
            raise InvalidskillimitError("Слишком низкий уровень подготовки")
        elif skill == "champion":
            raise InvalidskillimitError("Слишком высокий уровень подготовки")
        if age < 14 or age > 25:
            raise InvalidAgeLimitError("Неподходящий возраст")
        self.skill = skill.strip()
        self.age = age
    def get_info(self) -> str:
        return f"Секция: {self.name}\n Ответственный тренер: {self.coach}\n Цена за месяц занятий: {self.price}\n Допустимый уровень подготовки {self.skill}\n Допустимый возраст занятий спортом: {self.age}\n"

    def to_DB(self) -> dict: # dict == map в С++
        return {"name": self.name, "coach": self.coach, "price": self.price, "skill": self.skill, "age": self.age}
    @classmethod
    def from_DB(cls,data: dict) -> "Fight_Section": # cls - class(первой идет ссылка на заполняемый класс)
        try:
            return cls(
                name=data["name"],
                coach=data["coach"],
                price=int(data["price"]),
                skill=data["skill"],
                age=int(data["age"])
            )
        except (KeyError, TypeError, ValueError) as exc: # ловится ошибка и дальше именуется как exc
            # KeyError - обращение к несуществующему ключу, 
            # TypeError - какой то тип в файле нарушен
            # ValueError - ошибка преобразования типов
            raise DataFormatError(f"Некорректные данные секции: {exc}") from exc # цепочка исключений
            # выбрасывается DataFormatError, но первоисточником указывается exc(одна из выше перечисленных ошибок)

class Team_Section(SportSection):
    def __init__(self,name:str,coach: str,price: int,team_size: int,inventory: str) -> None:
        super().__init__(name,coach,price)
        if team_size <= 0: 
            raise ValueError("Количество игроков в команде меньше 1")
        self.team_size = team_size
        self.inventory = inventory
    
    def get_info(self) -> str:
        return f"Секция: {self.name}\n Ответственный тренер: {self.coach}\n Цена за месяц занятий: {self.price}\n Количество позиций в команде {self.team_size}\n Необходимый инвентарь: {self.inventory}\n"

    def to_xml(self) -> ET.Element:
        elem = ET.Element("Team_Section")
        ET.SubElement(elem,"name").text = self.name
        ET.SubElement(elem,"coach").text = self.coach
        ET.SubElement(elem,"price").text = str(self.price)
        ET.SubElement(elem,"team_size").text = str(self.team_size)
        ET.SubElement(elem,"inventory").text = self.inventory
        return elem

    @classmethod
    def from_xml(cls,element:ET.Element) -> "Team_Section":
        try:
            return cls(
                name = element.findtext("name",""),
                coach = element.findtext("coach",""),
                price = int(element.findtext("price","0")),
                team_size = int(element.findtext("team_size","0")),
                inventory = element.findtext("inventory","")
            )
        except (TypeError,ValueError) as exc:
            raise DataFormatError(f"Некорректные данные командной секции: {exc}") from exc
        
class Administration:
    def __init__(self) -> None:
        self.fight_sections: list[Fight_Section] = [] # создание пустого динамического 
        # списка с элементами типа Fight_Section
        self.team_sections: list[Team_Section] = []

    def add_fight_section(self,section: Fight_Section) -> None:
        self.fight_sections.append(section) # section - временная переменная класса 
    
    def add_team_section(self,section: Team_Section) -> None:
        self.team_sections.append(section)

    def save_fight_sections_json(self,path: str) -> None:
        data = [section.to_DB() for section in self.fight_sections]
        try:
            with open(path,"w",encoding = "utf-8") as f:
                json.dump(data,f,ensure_ascii = False,indent = 4) #ensure_ascii = False не дает переводить char символы при записи в аски код
        except (OSError,json.JSONDecodeError) as exc:
            raise DataFormatError(f"Не удалось записать файл {path}: {exc}") from exc
        
    def load_fight_sections_json(self,path: str) -> None:
        try:
            with open(path,"r",encoding = "utf-8") as f:
                data = json.load(f)
        except (OSError,json.JSONDecodeError) as exc:
            raise DataFormatError(f"Не удалось прочитать файл {path}: {exc}") from exc
        self.fight_sections = [Fight_Section.from_DB(item) for item in data]

    def save_team_sections_xml(self,path: str) -> None:
        root = ET.Element("team_sections")
        for section in self.team_sections:
            root.append(section.to_xml())
        tree  = ET.ElementTree(root)
        try:
            tree.write(path,encoding = "utf-8",xml_declaration = True)
        except OSError as exc:
            raise DataFormatError(f"Не удалось сделать запись XML файла {path}: {exc}") from exc

    def load_team_section_xml(self,path: str) -> None:
        try:
            tree = ET.parse(path)
        except (OSError, ET.ParseError) as exc:
            raise DataFormatError(f"Не удалось прочитать XML файл {path}: {exc}") from exc
        root = tree.getroot() # возвращает корень дерева
        if root.tag != "team_sections":
            raise DataFormatError(f"Некорректный корневой элемент в XML: ожидали <team_sections>, нашли <{root.tag}>")
        self.team_sections = [Team_Section.from_xml(elem) for elem in root.findall("Team_Section")]
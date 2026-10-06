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

class TeamSection(SportSection):
    def __init__(self,name:str,coach: str,price: int,team_size: int,inventory: str) -> None:
        super().__init__(name,coach,price)
        if team_size <= 0: 
            raise ValueError("Количество игроков в команде меньше 1")
        self.team_size = team_size
        self.inventory = inventory
    
    def get_info(self) -> str:
        return f"Секция: {self.name}\n Ответственный тренер: {self.coach}\n Цена за месяц занятий: {self.price}\n Количество позиций в команде {self.team_size}\n Необходимый инвентарь: {self.inventory}\n"

    def to_xml(self) -> ET.Element:
        elem = ET.Element("TeamSection")
        ET.SubElement(elem,"name").text = self.name
        ET.SubElement(elem,"coach").text = self.coach
        ET.SubElement(elem,"price").text = str(self.price)
        ET.SubElement(elem,"team_size").text = str(self.team_size)
        ET.SubElement(elem,"inventory").text = self.inventory

    @classmethod
    def from_xml(cls,element,ET.Element) -> "TeamSection":
        try:
            return cls(
                name = element.findtext("name",""),
                coach = element.findtext("coach",""),
                name = element.findtext("name",""),
                name = element.findtext("name",""),
                name = element.findtext("name",""),
            )
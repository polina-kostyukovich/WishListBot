class Bean:
    def __init__(self, id = None):
        self.id = id

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    def isCorrect(self) -> bool:
        return self.id is not None

    def toString(self, phrases) -> str:
        pass


class ContentBean(Bean):
    def __init__(self, id = None, number = None, name = None, description = None, link = None, gifter_id = None):
        Bean.__init__(self, id)
        self.number = number
        self.name = name
        self.description = description
        self.link = link
        self.gifter_id = gifter_id

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    def __hash__(self):
        return hash(self.id) + hash(self.name)

    def isCorrect(self) -> bool:
        return Bean.isCorrect(self) and self.name is not None

    def hasNumber(self) -> bool:
        return self.number is not None

    def toString(self, phrases) -> str:
        string = phrases.name + ": " + self.name
        if self.description is not None:
            string += "\n" + phrases.description + ": " + self.description
        if self.link is not None:
            string += "\n" + phrases.link + ": " + self.link
        return string

    def toStringWithNumber(self) -> str:
        string = str(self.number) + ". " + self.name
        if self.description is not None:
            string += "\n<i>" + self.description + "</i>"
        if self.link is not None:
            string += "\n" + self.link
        return string


class WishlistBean(Bean):
    def __init__(self, id = None, owner_id = None, name = None, description = None, number = None):
        Bean.__init__(self, id)
        self.owner_id = owner_id
        self.name = name
        self.description = description
        self.number = number

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    def isCorrect(self) -> bool:
        return Bean.isCorrect(self) and self.owner_id is not None and self.name is not None

    def hasNumber(self) -> bool:
        return self.number is not None

    def toString(self, phrases) -> str:
        string = phrases.name + ": " + self.name
        if self.description is not None:
            string += "\n" + phrases.description + ": " + self.description
        return string

    def toStringWithNumber(self) -> str:
        string = str(self.number) + ". " + self.name
        if self.description is not None:
            string += "\n<i>" + self.description + "</i>"
        return string


class UserBean(Bean):
    def __init__(self, id = None, username = None, number = None):
        Bean.__init__(self, id)
        self.username = username
        self.number = number

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    def isCorrect(self) -> bool:
        return Bean.isCorrect(self) and self.username is not None

    def hasNumber(self) -> bool:
        return self.number is not None

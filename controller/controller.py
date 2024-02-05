import json
import sys
from telebot import types
from munch import DefaultMunch

from create_wishlist_controller import CreateWishlistController
from list_wishlists_controller import ListWishlistsController
from add_wish_controller import AddWishController
from find_wish_controller import FindWishController
from manage_access_controller import ManageAccessController
from edit_wishlist_controller import EditWishlistController
from see_friend_wishlist_controller import SeeFriendWishlistController
from feedback_controller import FeedbackController
sys.path.insert(1, '/home/polyushka/WishListBot')
import beans
import service
from service import UserService
from exceptions import ControllerException
from abstract_bot import Bot


class MessageToSend:
    def __init__(self, text, markup = None, reply_params = None):
        self.text = text
        self.markup = markup
        self.reply_params = reply_params


class Controller:
    def __init__(self, setup_file_name: str, phrases_file_name: str, bot: Bot):
        with open(setup_file_name) as setup_file:
            data = json.load(setup_file)
        service.Transaction.setDatabaseInfo(data['database_info'])
        self.__admin_id = data['admin_id']

        with open(phrases_file_name) as phrases_file:
            phrases = json.load(phrases_file)
            self.__phrases = DefaultMunch.fromDict(phrases)

        self.__bot = bot
        self.__active_scenario_controllers = {}
        self.__last_active_messages = {}


    def getCommandsDescriptions(self):
        return self.__phrases.commands_descriptions


    def registerUser(self, user: beans.UserBean):
        if user is None:
            raise ControllerException("user is None")
        if not user.isCorrect():
            raise ControllerException("user is not correct")

        user_service = UserService()
        try:
            user_service.createUserSafe(user)
            self.sendMessage(user.id, self.__phrases.common.hello)
        except:
            self.sendMessage(user.id, self.__phrases.common.error)
            self.sendMessage(self.__admin_id, self.__phrases.common.error_for_admin)


    def processTextMessage(self, message):
        self.__active_scenario_controllers[message.from_user.id].processTextMessage(message)


    def sendMessage(self, user_id: int, text: str,
                    reply_markup = types.ReplyKeyboardRemove(selective=False),
                    reply_params = None):
        self.__last_active_messages[user_id] = MessageToSend(text, reply_markup, reply_params)
        return self.__bot.sendMessage(user_id, text, reply_markup, reply_params)


    def sendMessageWishoutSaving(self, user_id: int, text: str,
                    reply_markup = types.ReplyKeyboardRemove(selective=False),
                    reply_params = None):
        return self.__bot.sendMessage(user_id, text, reply_markup, reply_params)


    def forwardMessage(self, message, to_chat_id):
        self.__bot.forwardMessage(to_chat_id, message.chat.id, message.message_id)


    def sendLastMessage(self, user_id: int):
        last_message = self.__last_active_messages[user_id]
        return self.__bot.sendMessage(user_id, last_message.text, last_message.markup, last_message.reply_params)


    def sendYesNoButtons(self, user_id: int, text: str):
        markup = types.ReplyKeyboardMarkup()
        yes_button = types.KeyboardButton(self.__phrases.common.yes)
        no_button = types.KeyboardButton(self.__phrases.common.no)
        markup.row(yes_button, no_button)
        self.sendMessage(user_id, text, reply_markup = markup)


    def cancel(self, message):
        if message.from_user.id in self.__active_scenario_controllers.keys():
            self.__active_scenario_controllers[message.from_user.id].cancel(message)


    def finishActiveScenario(self, user_id: int):
        del self.__active_scenario_controllers[user_id]
        del self.__last_active_messages[user_id]


    def askToFinishScenario(self, message):
        self.sendMessageWishoutSaving(message.from_user.id, self.__phrases.common.finish_scenario_request)
        self.sendLastMessage(message.from_user.id)


    def startActiveScenario(self, message):
        self.__active_scenario_controllers[message.from_user.id].start(message)


    def setCreateWishlistCase(self, message):
        if message.from_user.id in self.__active_scenario_controllers.keys():
            self.askToFinishScenario(message)
        else:
            self.__active_scenario_controllers[message.from_user.id] = \
                    CreateWishlistController(self,
                                             self.__phrases.common,
                                             self.__phrases.create_wishlist,
                                             self.__admin_id)
            self.startActiveScenario(message)


    def setListWishlistsCase(self, message):
        if message.from_user.id in self.__active_scenario_controllers.keys():
            self.askToFinishScenario(message)
        else:
            self.__active_scenario_controllers[message.from_user.id] = \
                    ListWishlistsController(self,
                                            self.__phrases.common,
                                            self.__phrases.list_wishlists,
                                            self.__admin_id)
            self.startActiveScenario(message)


    def setAddWishCase(self, message):
        if message.from_user.id in self.__active_scenario_controllers.keys():
            self.askToFinishScenario(message)
        else:
            self.__active_scenario_controllers[message.from_user.id] = \
                    AddWishController(self,
                                      self.__phrases.common,
                                      self.__phrases.add_wish,
                                      self.__admin_id)
            self.startActiveScenario(message)


    def setManageAccessCase(self, message):
        if message.from_user.id in self.__active_scenario_controllers.keys():
            self.askToFinishScenario(message)
        else:
            self.__active_scenario_controllers[message.from_user.id] = \
                    ManageAccessController(self,
                                      self.__phrases.common,
                                      self.__phrases.manage_access,
                                      self.__admin_id)
            self.startActiveScenario(message)


    def setFindWishCase(self, message):
        if message.from_user.id in self.__active_scenario_controllers.keys():
            self.askToFinishScenario(message)
        else:
            self.__active_scenario_controllers[message.from_user.id] = \
                    FindWishController(self,
                                      self.__phrases.common,
                                      self.__phrases.find_wish,
                                      self.__admin_id)
            self.startActiveScenario(message)


    def setEditWishlistCase(self, message):
        if message.from_user.id in self.__active_scenario_controllers.keys():
            self.askToFinishScenario(message)
        else:
            self.__active_scenario_controllers[message.from_user.id] = \
                    EditWishlistController(self,
                                          self.__phrases.common,
                                          self.__phrases.edit_wishlist,
                                          self.__admin_id)
            self.startActiveScenario(message)


    def setSeeFriendWishlistCase(self, message):
        if message.from_user.id in self.__active_scenario_controllers.keys():
            self.askToFinishScenario(message)
        else:
            self.__active_scenario_controllers[message.from_user.id] = \
                    SeeFriendWishlistController(self,
                                                self.__phrases.common,
                                                self.__phrases.see_friend_wishlist,
                                                self.__admin_id)
            self.startActiveScenario(message)


    def setGiveFeedbackCase(self, message):
        if message.from_user.id in self.__active_scenario_controllers.keys():
            self.askToFinishScenario(message)
        else:
            self.__active_scenario_controllers[message.from_user.id] = \
                    FeedbackController(self,
                                       self.__phrases.common,
                                       self.__phrases.feedback,
                                       self.__admin_id)
            self.startActiveScenario(message)

import sys
from telebot.types import ReplyParameters
from telebot.types import ReplyKeyboardMarkup
from telebot import types

from case_controller import CaseController
from scenarios import ManageAccessCase

sys.path.insert(1, '/home/polyushka/WishListBot')
import service
from exceptions import ControllerException


class ManageAccessController(CaseController):
    def start(self, message):
        self.__readers = []
        self.__wishlists = self.getWishlists(message.from_user.id)
        text = self.wishlistsToStr(self.__wishlists)

        if not self.__wishlists:
            self.controller.sendMessage(message.from_user.id, self.common_phrases.no_wishlists)
            self.finish(message)
        else:
            self.__list_message = self.controller.sendMessage(message.from_user.id, text)
            reply_params = ReplyParameters(message_id = self.__list_message.message_id)
            self.controller.sendMessage(message.from_user.id,
                                        self.special_phrases.what_wishlist,
                                        reply_params = reply_params)
            self.__step = ManageAccessCase.choose_wishlist


    def processTextMessage(self, message):
        match self.__step:
            case ManageAccessCase.choose_wishlist:
                self.__showFriends(message)

            case ManageAccessCase.choose_option:
                self.__chooseOption(message)

            case ManageAccessCase.username_enter:
                self.__processUsernameEnter(message)


    def hasFinished(self):
        return self.__step == ManageAccessCase.has_finished


    def finish(self, message):
        del self.__wishlists
        del self.__readers
        self.__step = ManageAccessCase.has_finished
        self.controller.finishActiveScenario(message.from_user.id)


    def __showFriends(self, message):
        wishlist_number = self.extractNumber(message, message.text, len(self.__wishlists))
        if wishlist_number is None:
            return

        self.__wishlist_number = wishlist_number

        user_service = service.UserService()
        self.__readers = user_service.getWishlistReaders(self.__wishlists[self.__wishlist_number].id)
        if not self.__readers:
            self.controller.sendMessage(message.from_user.id, self.special_phrases.no_friends)
        else:
            text = self.special_phrases.friends_here % ('<b>' + self.__wishlists[self.__wishlist_number].name + '</b>:')
            for i in range(len(self.__readers)):
                text += '\n' + str(i + 1) + '. @' + self.__readers[i].username
            self.controller.sendMessage(message.from_user.id, text)

        self.__whatNext(message)


    def __whatNext(self, message):
        markup = ReplyKeyboardMarkup()
        allow_button = types.KeyboardButton(self.special_phrases.add_reader)
        forbid_button = types.KeyboardButton(self.special_phrases.delete_reader)
        nothing_button = types.KeyboardButton(self.common_phrases.nothing)
        markup.row(allow_button)
        markup.row(forbid_button)
        markup.row(nothing_button)
        self.controller.sendMessage(message.from_user.id, self.common_phrases.what_next, reply_markup = markup)
        self.__step = ManageAccessCase.choose_option


    def __chooseOption(self, message):
        if message.text == self.special_phrases.add_reader or message.text == self.special_phrases.delete_reader:
            self.controller.sendMessage(message.from_user.id, self.special_phrases.enter_username)
            self.__answer = message.text
            self.__step = ManageAccessCase.username_enter
        elif message.text == self.common_phrases.nothing:
            self.controller.sendMessage(message.from_user.id, self.common_phrases.well)
            self.finish(message)
        else:
            self.controller.sendMessageWishoutSaving(message.from_user.id, self.common_phrases.choose_from_variants)
            self.controller.sendLastMessage(message.from_user.id)


    def __processUsernameEnter(self, message):
        if self.__answer == self.special_phrases.add_reader:
            self.__addFriend(message)
        elif self.__answer == self.special_phrases.delete_reader:
            self.__deleteFriend(message)
        else:
            raise ControllerException("unknown answer")

        self.__whatNext(message)


    def __addFriend(self, message):
        username = message.text
        if username[0] == '@':
            username = username[1:]
        usernames = [reader.username for reader in self.__readers]
        if username not in usernames:
            try:
                wishlist_id = self.__wishlists[self.__wishlist_number].id
                user_service = service.UserService()
                user = user_service.findUserByUsername(username)
                if user is None:
                    self.controller.sendMessage(message.from_user.id, self.special_phrases.friend_does_not_exist % username)
                    return
                user_service.addReaderToWishlist(reader_id = user.id, wishlist_id = wishlist_id)
                self.__readers.append(user)
            except:
                self.handleError(message)
                self.finish(message)
                return

        self.controller.sendMessage(message.from_user.id, self.common_phrases.done)


    def __deleteFriend(self, message):
        username = message.text
        usernames = [reader.username for reader in self.__readers]
        if username in usernames:
            try:
                wishlist_id = self.__wishlists[self.__wishlist_number].id
                user_service = service.UserService()
                user_index = usernames.index(username)
                user_id = self.__readers[user_index].id
                user_service.deleteReaderFromWishlist(reader_id = user_id, wishlist_id = wishlist_id)
                del self.__readers[user_index]
            except:
                self.handleError(message)
                self.finish(message)
                return

        self.controller.sendMessage(message.from_user.id, self.common_phrases.done)

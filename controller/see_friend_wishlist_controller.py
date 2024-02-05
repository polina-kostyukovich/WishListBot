import sys
from telebot.types import ReplyParameters
from telebot.types import ReplyKeyboardMarkup
from telebot import types

from case_controller import CaseController
from scenarios import SeeFriendWishlistCase

sys.path.insert(1, '/home/polyushka/WishListBot')
import service
import beans


class SeeFriendWishlistController(CaseController):
    def start(self, message):
        self.controller.sendMessage(message.from_user.id, self.special_phrases.enter_friend_username)
        self.__step = SeeFriendWishlistCase.username_enter


    def processTextMessage(self, message):
        match self.__step:
            case SeeFriendWishlistCase.username_enter:
                self.__enterUsername(message)

            case SeeFriendWishlistCase.choose_option:
                self.__chooseOption(message)

            case SeeFriendWishlistCase.number_enter_to_reserve:
                self.__reserveContent(message)

            case SeeFriendWishlistCase.number_enter_to_unreserve:
                self.__unreserveContent(message)


    def hasFinished(self):
        return self.__step == SeeFriendWishlistCase.has_finished


    def finish(self, message):
        self.__step = SeeFriendWishlistCase.has_finished
        self.controller.finishActiveScenario(message.from_user.id)


    def __enterUsername(self, message):
        username = message.text
        if username[0] == '@':
            username = username[1:]
        try:
            user_service = service.UserService()
            self.__owner = user_service.findUserByUsername(username)
            if self.__owner is None:
                self.controller.sendMessage(message.from_user.id, self.special_phrases.friend_does_not_exist % username)
                return
            self.__contents = self.__findAccessibleContents(message, owner_id = self.__owner.id, reader_id = message.from_user.id)
        except:
            self.handleError(message)
            self.finish(message)
            return

        if not self.__contents:
            self.controller.sendMessage(message.from_user.id, self.special_phrases.no_wishlists % ('@' + username))
            self.finish(message)
            return

        CaseController.enumerateBeans(self.__contents)
        text = self.__contentsToStr(message)
        self.__list_message = self.controller.sendMessage(message.from_user.id, text)
        self.__whatNext(message)


    def __contentsToStr(self, message):
        text = self.special_phrases.wishlist_here % ('<b>@' + self.__owner.username + '</b>') + ':'
        for content in self.__contents:
            if content.gifter_id is None:
                content_str = content.toStringWithNumber()
            elif content.gifter_id == message.from_user.id:
                content_str = '<b>' + content.toStringWithNumber() + '</b>'
            else:
                content_str = '<s>' + content.toStringWithNumber() + '</s>'
            text += '\n' + content_str
        return text


    def __findAccessibleContents(self, message, owner_id: int, reader_id: int) -> list[beans.ContentBean]:
        owner_wishlists = self.getWishlists(owner_id)
        user_service = service.UserService()
        accessible_wishlists = []
        for wishlist in owner_wishlists:
            try:
                readers = user_service.getWishlistReaders(wishlist.id)
            except:
                self.handleError(message)
                self.finish(message)
                return
            if reader_id in [reader.id for reader in readers]:
                accessible_wishlists.append(wishlist)

        contents = []
        content_service = service.ContentService()
        for wishlist in accessible_wishlists:
            try:
                contents.extend(content_service.getWishlistContents(wishlist.id))
            except:
                self.handleError(message)
                self.finish(message)
                return

        unique_contents = list(set(contents))
        return unique_contents


    def __whatNext(self, message):
        markup = ReplyKeyboardMarkup()
        reserve_button = types.KeyboardButton(self.special_phrases.reserve)
        markup.row(reserve_button)

        if message.from_user.id in [content.gifter_id for content in self.__contents]:
            unreserve_button = types.KeyboardButton(self.special_phrases.unreserve)
            markup.row(unreserve_button)

        nothing_button = types.KeyboardButton(self.common_phrases.nothing)
        markup.row(nothing_button)

        self.controller.sendMessage(message.from_user.id, self.common_phrases.what_next, reply_markup = markup)
        self.__step = SeeFriendWishlistCase.choose_option


    def __chooseOption(self, message):
        if message.text == self.special_phrases.reserve:
            reply_params = ReplyParameters(message_id = self.__list_message.message_id)
            self.controller.sendMessage(message.from_user.id,
                                        self.special_phrases.enter_number_to_reserve,
                                        reply_params = reply_params)
            self.__step = SeeFriendWishlistCase.number_enter_to_reserve
        elif message.text == self.special_phrases.unreserve:
            reply_params = ReplyParameters(message_id = self.__list_message.message_id)
            self.controller.sendMessage(message.from_user.id,
                                        self.special_phrases.enter_number_to_unreserve,
                                        reply_params = reply_params)
            self.__step = SeeFriendWishlistCase.number_enter_to_unreserve
        elif message.text == self.common_phrases.nothing:
            self.controller.sendMessage(message.from_user.id, self.common_phrases.well)
            self.finish(message)
        else:
            self.controller.sendMessageWishoutSaving(message.from_user.id, self.common_phrases.choose_from_variants)
            self.controller.sendLastMessage(message.from_user.id)


    def __reserveContent(self, message):
        content_number = self.extractNumber(message, message.text, len(self.__contents))
        if content_number is None:
            return

        self.__content_number = content_number
        content = self.__contents[content_number]
        if content.gifter_id is None:
            try:
                content_service = service.ContentService()
                content_service.reserveContent(content.id, message.from_user.id)
                content.gifter_id = message.from_user.id
            except:
                self.handleError(message)
                self.finish(message)
                return
        elif content.gifter_id != message.from_user.id:
            self.controller.sendMessage(message.from_user.id, self.special_phrases.already_reserved)
            reply_params = ReplyParameters(message_id = self.__list_message.message_id)
            self.controller.sendMessage(message.from_user.id,
                                        self.special_phrases.enter_number_to_reserve,
                                        reply_params = reply_params)
            return
        self.controller.sendMessage(message.from_user.id, self.common_phrases.done)
        text = self.__contentsToStr(message)
        self.__list_message = self.controller.sendMessage(message.from_user.id, text)
        self.__whatNext(message)


    def __unreserveContent(self, message):
        content_number = self.extractNumber(message, message.text, len(self.__contents))
        if content_number is None:
            return

        self.__content_number = content_number
        content = self.__contents[content_number]
        if content.gifter_id == message.from_user.id:
            try:
                content_service = service.ContentService()
                content_service.unreserveContent(content.id)
                content.gifter_id = None
            except:
                self.handleError(message)
                self.finish(message)
                return
        else:
            reply_params = ReplyParameters(message_id = self.__list_message.message_id)
            self.controller.sendMessage(message.from_user.id,
                                        self.special_phrases.not_reserved,
                                        reply_params = reply_params)
            return
        self.controller.sendMessage(message.from_user.id, self.common_phrases.done)
        text = self.__contentsToStr(message)
        self.__list_message = self.controller.sendMessage(message.from_user.id, text)
        self.__whatNext(message)

import sys
from telebot.types import ReplyParameters
from telebot.types import ReplyKeyboardMarkup
from telebot import types

from case_controller import CaseController
from scenarios import EditWishlistCase

sys.path.insert(1, '/home/polyushka/WishListBot')
import service


class EditWishlistController(CaseController):
    def start(self, message):
        self.__wishlists = self.getWishlists(message.from_user.id)
        text = self.wishlistsToStr(self.__wishlists)

        if not self.__wishlists:
            self.controller.sendMessage(message.from_user.id, self.common_phrases.no_wishlists)
            self.finish(message)
        else:
            self.__list_message = self.controller.sendMessage(message.from_user.id, text)
            reply_params = ReplyParameters(message_id = self.__list_message.message_id)
            self.controller.sendMessage(message.from_user.id,
                                        self.special_phrases.enter_number_to_edit,
                                        reply_params = reply_params)
            self.__step = EditWishlistCase.number_enter


    def processTextMessage(self, message):
        match self.__step:
            case EditWishlistCase.number_enter:
                self.__enterNumber(message)

            case EditWishlistCase.choose_option:
                self.__chooseOption(message)

            case EditWishlistCase.change_name:
                self.__changeName(message)

            case EditWishlistCase.change_description:
                self.__changeDescription(message)

            case EditWishlistCase.delete_description:
                self.__deleteDescription(message)


    def hasFinished(self):
        return self.__step == EditWishlistCase.has_finished


    def finish(self, message):
        del self.__wishlists
        self.__step = EditWishlistCase.has_finished
        self.controller.finishActiveScenario(message.from_user.id)


    def __enterNumber(self, message):
        wishlist_number = self.extractNumber(message, message.text, len(self.__wishlists))
        if wishlist_number is None:
            return
        self.__wishlist_number = wishlist_number
        self.__whatNext(message)


    def __whatNext(self, message):
        wishlist = self.__wishlists[self.__wishlist_number]
        text = self.special_phrases.wishlist_info_here + ':\n' + wishlist.toString(self.common_phrases) +\
                    '\n' + self.common_phrases.what_next

        markup = ReplyKeyboardMarkup()
        change_name_button = types.KeyboardButton(self.special_phrases.change_name)
        markup.row(change_name_button)

        if wishlist.description is None:
            add_description_button = types.KeyboardButton(self.special_phrases.add_description)
            markup.row(add_description_button)
        else:
            change_description_button = types.KeyboardButton(self.special_phrases.change_description)
            markup.row(change_description_button)
            delete_description_button = types.KeyboardButton(self.special_phrases.delete_description)
            markup.row(delete_description_button)

        delete_button = types.KeyboardButton(self.special_phrases.delete_wishlist)
        markup.row(delete_button)

        nothing_button = types.KeyboardButton(self.common_phrases.nothing)
        markup.row(nothing_button)

        self.controller.sendMessage(message.from_user.id, text, reply_markup = markup)
        self.__step = EditWishlistCase.choose_option


    def __chooseOption(self, message):
        if message.text == self.special_phrases.change_name:
            text = self.special_phrases.enter_new_name
            self.__step = EditWishlistCase.change_name
        elif message.text == self.special_phrases.add_description:
            text = self.special_phrases.enter_description
            self.__step = EditWishlistCase.change_description
        elif message.text == self.special_phrases.change_description:
            text = self.special_phrases.enter_new_description
            self.__step = EditWishlistCase.change_description
        elif message.text == self.special_phrases.delete_description:
            self.__deleteDescription(message)
            return
        elif message.text == self.special_phrases.delete_wishlist:
            self.__deleteWishlist(message)
            return
        elif message.text == self.common_phrases.nothing:
            self.controller.sendMessage(message.from_user.id, self.common_phrases.well)
            self.finish(message)
            return
        else:
            self.controller.sendMessageWishoutSaving(message.from_user.id, self.common_phrases.choose_from_variants)
            self.controller.sendLastMessage(message.from_user.id)
            return

        self.controller.sendMessage(message.from_user.id, text)


    def __changeName(self, message):
        wishlist = self.__wishlists[self.__wishlist_number]
        wishlist_service = service.WishlistService()
        try:
            wishlist_service.updateWishlistName(wishlist.id, message.text)
            wishlist.name = message.text
            self.controller.sendMessage(message.from_user.id, self.common_phrases.done)
        except:
            self.handleError(message)
            self.finish(message)
            return
        self.__whatNext(message)


    def __changeDescription(self, message):
        wishlist = self.__wishlists[self.__wishlist_number]
        wishlist_service = service.WishlistService()
        try:
            wishlist_service.updateWishlistDescription(wishlist.id, message.text)
            wishlist.description = message.text
            self.controller.sendMessage(message.from_user.id, self.common_phrases.done)
        except:
            self.handleError(message)
            self.finish(message)
            return
        self.__whatNext(message)


    def __deleteDescription(self, message):
        wishlist = self.__wishlists[self.__wishlist_number]
        wishlist_service = service.WishlistService()
        try:
            wishlist_service.deleteWishlistDescription(wishlist.id)
            wishlist.description = None
            self.controller.sendMessage(message.from_user.id, self.common_phrases.done)
        except:
            self.handleError(message)
            self.finish(message)
            return
        self.__whatNext(message)


    def __deleteWishlist(self, message):
        wishlist = self.__wishlists[self.__wishlist_number]
        wishlist_service = service.WishlistService()
        try:
            unique_contents = wishlist_service.deleteWishlist(wishlist.id)
            self.controller.sendMessage(message.from_user.id, self.common_phrases.done)

            user_service = service.UserService()
            owner = user_service.findUserById(message.from_user.id)
            for content in unique_contents:
                if content.gifter_id is not None:
                    text = self.special_phrases.wish_was_edited % ('<b>@' + owner.username + '</b>') + ':\n' +\
                                content.toString(self.common_phrases)
                    self.controller.sendMessage(content.gifter_id, text)
        except:
            self.handleError(message)
        self.finish(message)

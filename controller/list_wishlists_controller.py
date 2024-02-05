import sys
from telebot.types import ReplyParameters

from case_controller import CaseController
from scenarios import ListWishlistsCase

sys.path.insert(1, '/home/polyushka/WishListBot')
import service


class ListWishlistsController(CaseController):
    def start(self, message):
        self.__wishlists = self.getWishlists(message.from_user.id)
        text = self.wishlistsToStr(self.__wishlists)

        if not self.__wishlists:
            self.controller.sendMessage(message.from_user.id, self.common_phrases.no_wishlists)
            self.finish(message)
        else:
            self.__list_message = self.controller.sendMessage(message.from_user.id, text)
            self.controller.sendYesNoButtons(message.from_user.id, self.special_phrases.see_wishlist_ask)
            self.__step = ListWishlistsCase.see_wishlist_ask


    def processTextMessage(self, message):
        match self.__step:
            case ListWishlistsCase.see_wishlist_ask:
                self.__whatWishlist(message)

            case ListWishlistsCase.choose_wishlist:
                self.__showWishlist(message)


    def hasFinished(self):
        return self.__step == ListWishlistsCase.has_finished


    def finish(self, message):
        del self.__wishlists
        self.__step = ListWishlistsCase.has_finished
        self.controller.finishActiveScenario(message.from_user.id)


    def __whatWishlist(self, message):
        if message.text == self.common_phrases.yes:
            reply_params = ReplyParameters(message_id = self.__list_message.message_id)
            self.controller.sendMessage(message.from_user.id,
                                        self.special_phrases.what_wishlist,
                                        reply_params = reply_params)
            self.__step = ListWishlistsCase.choose_wishlist
        elif message.text == self.common_phrases.no:
            self.controller.sendMessage(message.from_user.id, self.common_phrases.well)
            self.finish(message)
        else:
            self.controller.sendMessageWishoutSaving(message.from_user.id, self.common_phrases.choose_from_variants)
            self.controller.sendLastMessage(message.from_user.id)


    def __showWishlist(self, message):
        wishlist_number = self.extractNumber(message, message.text, len(self.__wishlists))
        if wishlist_number is None:
            return

        content_service = service.ContentService()
        contents = content_service.getWishlistContents(self.__wishlists[wishlist_number].id)
        CaseController.enumerateBeans(contents)
        text = self.__wishlists[wishlist_number].toString(self.common_phrases)
        for content in contents:
            text += '\n' + content.toStringWithNumber()

        if not contents:
            text += '\n' + self.common_phrases.nothing_yet

        self.controller.sendMessage(message.from_user.id, text)
        self.controller.sendYesNoButtons(message.from_user.id, self.special_phrases.see_another_wishlist_ask)
        self.__step = ListWishlistsCase.see_wishlist_ask

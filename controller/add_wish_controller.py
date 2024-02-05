import sys
from telebot.types import ReplyParameters

from case_controller import CaseController
from scenarios import AddWishCase

sys.path.insert(1, '/home/polyushka/WishListBot')
import beans
import service


class AddWishController(CaseController):
    def start(self, message):
        self.__content = beans.ContentBean()
        self.__wishlists_with_content = []
        self.__wishlists = self.getWishlists(message.from_user.id)
        text = self.wishlistsToStr(self.__wishlists)

        if not self.__wishlists:
            self.controller.sendMessage(message.from_user.id, self.common_phrases.no_wishlists)
            self.finish(message)
        else:
            self.__list_message = self.controller.sendMessage(message.from_user.id, text)
            reply_params = ReplyParameters(message_id = self.__list_message.message_id)
            self.controller.sendMessage(message.from_user.id,
                                        self.special_phrases.enter_wishlist_number,
                                        reply_params = reply_params)
            self.__step = AddWishCase.choose_wishlist


    def processTextMessage(self, message):
        match self.__step:
            case AddWishCase.choose_wishlist:
                self.__chooseWishlist(message)

            case AddWishCase.name_enter:
                self.__enterName(message)

            case AddWishCase.description_enter_ask:
                self.__enterDescriptionAsk(message)

            case AddWishCase.description_enter:
                self.__enterDescription(message)

            case AddWishCase.link_enter_ask:
                self.__enterLinkAsk(message)

            case AddWishCase.link_enter:
                self.__enterLink(message)

            case AddWishCase.correct_ask:
                self.__correct(message)

            case AddWishCase.add_to_another_wishlist_ask:
                self.__addToAnotherWishlistAsk(message)

            case AddWishCase.add_to_another_wishlist:
                self.__addToAnotherWishlist(message)

            case AddWishCase.add_another_wish:
                self.__addOneMoreWish(message)


    def hasFinished(self):
        return self.__step == AddWishCase.has_finished


    def finish(self, message):
        del self.__wishlists
        del self.__content
        del self.__wishlists_with_content
        self.__step = AddWishCase.has_finished
        self.controller.finishActiveScenario(message.from_user.id)


    def __chooseWishlist(self, message):
        wishlist_number = self.extractNumber(message, message.text, len(self.__wishlists))
        if wishlist_number is None:
            return

        self.__wishlist_number = wishlist_number
        self.controller.sendMessage(message.from_user.id,
                                    self.special_phrases.enter_name)
        self.__step = AddWishCase.name_enter


    def __enterName(self, message):
        self.__content.name = message.text
        self.controller.sendYesNoButtons(message.from_user.id, text = self.special_phrases.add_description_ask)
        self.__step = AddWishCase.description_enter_ask


    def __enterDescriptionAsk(self, message):
        if message.text == self.common_phrases.yes:
            self.controller.sendMessage(message.from_user.id, self.special_phrases.enter_description)
            self.__step = AddWishCase.description_enter
        elif message.text == self.common_phrases.no:
            self.controller.sendYesNoButtons(message.from_user.id, text = self.special_phrases.add_link_ask)
            self.__step = AddWishCase.link_enter_ask
        else:
            self.controller.sendMessageWishoutSaving(message.from_user.id, self.common_phrases.choose_from_variants)
            self.controller.sendLastMessage(message.from_user.id)


    def __enterDescription(self, message):
        self.__content.description = message.text
        self.controller.sendYesNoButtons(message.from_user.id, text = self.special_phrases.add_link_ask)
        self.__step = AddWishCase.link_enter_ask


    def __enterLinkAsk(self, message):
        if message.text == self.common_phrases.yes:
            self.controller.sendMessage(message.from_user.id, self.special_phrases.enter_link)
            self.__step = AddWishCase.link_enter
        elif message.text == self.common_phrases.no:
            self.__check(message)
        else:
            self.controller.sendMessageWishoutSaving(message.from_user.id, self.common_phrases.choose_from_variants)
            self.controller.sendLastMessage(message.from_user.id)


    def __enterLink(self, message):
        self.__content.link = message.text
        self.__check(message)


    def __check(self, message):
        wishlist_name = self.__wishlists[self.__wishlist_number].name
        text = self.special_phrases.params % ('<b>' + wishlist_name + '</b>') + ": \n" + \
                    self.__content.toString(self.common_phrases) +\
                    "\n" + self.common_phrases.all_correct_question
        self.controller.sendYesNoButtons(message.from_user.id, text = text)
        self.__step = AddWishCase.correct_ask


    def __correct(self, message):
        wishlist_id = self.__wishlists[self.__wishlist_number].id
        if message.text == self.common_phrases.yes:
            try:
                content_service = service.ContentService()
                content_service.addContentToWishlist(self.__content, wishlist_id)
                self.__wishlists_with_content = [wishlist_id]
                self.controller.sendMessage(message.from_user.id, self.special_phrases.created)
            except:
                self.handleError(message)
                self.finish(message)
                return

            self.controller.sendYesNoButtons(message.from_user.id, self.special_phrases.add_to_another_wishlist_ask)
            self.__step = AddWishCase.add_to_another_wishlist_ask
        elif message.text == self.common_phrases.no:
            self.controller.sendMessage(message.from_user.id, self.special_phrases.cancel)
            wishlist = self.__wishlists[self.__wishlist_number]
            self.controller.sendYesNoButtons(message.from_user.id,
                                             self.special_phrases.add_another_wish % ('<b>' + wishlist.name + '</b>'))
            self.__step = AddWishCase.add_another_wish
        else:
            self.controller.sendMessageWishoutSaving(message.from_user.id, self.common_phrases.choose_from_variants)
            self.controller.sendLastMessage(message.from_user.id)


    def __addToAnotherWishlistAsk(self, message):
        if message.text == self.common_phrases.yes:
            reply_params = ReplyParameters(message_id = self.__list_message.message_id)
            self.controller.sendMessage(message.from_user.id,
                                        self.special_phrases.enter_wishlist_number2,
                                        reply_params = reply_params)
            self.__step = AddWishCase.add_to_another_wishlist
        elif message.text == self.common_phrases.no:
            wishlist = self.__wishlists[self.__wishlist_number]
            self.controller.sendYesNoButtons(message.from_user.id,
                                             self.special_phrases.add_another_wish % ('<b>' + wishlist.name + '</b>'))
            self.__step = AddWishCase.add_another_wish
        else:
            self.controller.sendMessageWishoutSaving(message.from_user.id, self.common_phrases.choose_from_variants)
            self.controller.sendLastMessage(message.from_user.id)


    def __addToAnotherWishlist(self, message):
        wishlist_number = self.extractNumber(message, message.text, len(self.__wishlists))
        if wishlist_number is None:
            return

        wishlist_id = self.__wishlists[wishlist_number].id
        if wishlist_id not in self.__wishlists_with_content:
            try:
                content_service = service.ContentService()
                content_service.addExistingContentToWishlist(wishlist_id = wishlist_id, content_id = self.__content.id)
                self.__wishlists_with_content.append(wishlist_id)
                self.controller.sendMessage(message.from_user.id, self.special_phrases.created)
            except:
                self.handleError(message)
                self.finish(message)
                return
        else:
            self.controller.sendMessage(message.from_user.id, self.special_phrases.created)

        self.controller.sendYesNoButtons(message.from_user.id, self.special_phrases.add_to_another_wishlist_ask)
        self.__step = AddWishCase.add_to_another_wishlist_ask


    def __addOneMoreWish(self, message):
        if message.text == self.common_phrases.yes:
            self.controller.sendMessage(message.from_user.id,
                                    self.special_phrases.enter_name)
            self.__content = beans.ContentBean()
            self.__step = AddWishCase.name_enter
        elif message.text == self.common_phrases.no:
            self.controller.sendMessage(message.from_user.id, self.common_phrases.well)
            self.finish(message)
        else:
            self.controller.sendMessageWishoutSaving(message.from_user.id, self.common_phrases.choose_from_variants)
            self.controller.sendLastMessage(message.from_user.id)

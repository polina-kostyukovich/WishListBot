import sys

from case_controller import CaseController
from scenarios import CreateWishlistCase

sys.path.insert(1, '/home/polyushka/WishListBot')
import beans
import service


class CreateWishlistController(CaseController):
    def start(self, message):
        self.controller.sendMessage(message.from_user.id, self.special_phrases.enter_name)
        self.__step = CreateWishlistCase.name_enter
        self.__wishlist = beans.WishlistBean(id = 0, owner_id = message.from_user.id)


    def processTextMessage(self, message):
        match self.__step:
            case CreateWishlistCase.name_enter:
                self.__enterName(message)

            case CreateWishlistCase.description_enter_ask:
                self.__enterDescriptionAsk(message)

            case CreateWishlistCase.description_enter:
                self.__enterDescription(message)

            case CreateWishlistCase.correct_ask:
                self.__correct(message)


    def hasFinished(self):
        return self.__step == CreateWishlistCase.has_finished


    def finish(self, message):
        del self.__wishlist
        self.__step = CreateWishlistCase.has_finished
        self.controller.finishActiveScenario(message.from_user.id)


    def __enterName(self, message):
        wishlist_service = service.WishlistService()
        user_wishlists = wishlist_service.getUserWishlists(message.from_user.id)
        wishlists_names = [wishlist.name for wishlist in user_wishlists]
        if message.text in wishlists_names:
            self.controller.sendMessage(message.from_user.id, self.special_phrases.name_exists +\
                    '. ' + self.special_phrases.enter_another_name)
        else:
            self.__wishlist.name = message.text
            self.controller.sendYesNoButtons(message.from_user.id, text = self.special_phrases.add_description_ask)
            self.__step = CreateWishlistCase.description_enter_ask


    def __enterDescriptionAsk(self, message):
        if message.text == self.common_phrases.yes:
            self.controller.sendMessage(message.from_user.id, self.special_phrases.enter_description)
            self.__step = CreateWishlistCase.description_enter
        elif message.text == self.common_phrases.no:
            self.__check(message)
        else:
            self.controller.sendMessageWishoutSaving(message.from_user.id, self.common_phrases.choose_from_variants)
            self.controller.sendLastMessage(message.from_user.id)


    def __enterDescription(self, message):
        self.__wishlist.description = message.text
        self.__check(message)


    def __check(self, message):
        text = self.special_phrases.params + ": \n" + self.__wishlist.toString(self.common_phrases) +\
                    "\n" + self.common_phrases.all_correct_question
        self.controller.sendYesNoButtons(message.from_user.id, text = text)
        self.__step = CreateWishlistCase.correct_ask


    def __correct(self, message):
        if message.text == self.common_phrases.yes:
            try:
                wishlist_service = service.WishlistService()
                wishlist_service.createWishlist(self.__wishlist)
                self.controller.sendMessage(message.from_user.id, self.special_phrases.created)
            except:
                self.handleError(message)

            self.finish(message)
        elif message.text == self.common_phrases.no:
            self.cancel(message)
        else:
            self.controller.sendMessageWishoutSaving(message.from_user.id, self.common_phrases.choose_from_variants)
            self.controller.sendLastMessage(message.from_user.id)

import sys
import traceback
from typing import Optional

sys.path.insert(1, '/home/polyushka/WishListBot')
import beans
import service


class CaseController:
    def __init__(self, controller, common_phrases, special_phrases, admin_id: int):
        self.controller = controller
        self.common_phrases = common_phrases
        self.special_phrases = special_phrases
        self.admin_id = admin_id

    def start(self, message):
        pass

    def processTextMessage(self, message):
        pass

    def hasFinished(self):
        pass

    def finish(self, message):
        pass

    def cancel(self, message):
        self.controller.sendMessage(message.from_user.id, self.special_phrases.cancel)
        self.finish(message)

    def handleError(self, message):
        traceback.print_exc()
        self.controller.sendMessage(message.from_user.id, self.common_phrases.error)
        self.controller.sendMessage(self.admin_id, self.common_phrases.error_for_admin)

    @staticmethod
    def enumerateBeans(beans_list: list[beans.Bean]):
        for i in range(len(beans_list)):
            beans_list[i].number = i + 1

    def wishlistsToStr(self, wishlists: list[beans.WishlistBean]) -> str:
        text = self.common_phrases.wishlists_here + ':'
        for wishlist in wishlists:
            text += '\n' + wishlist.toStringWithNumber()
        return text

    def getWishlists(self, user_id: int) -> list[beans.WishlistBean]:
        try:
            wishlist_service = service.WishlistService()
            wishlists = wishlist_service.getUserWishlists(user_id)
            CaseController.enumerateBeans(wishlists)
            return wishlists
        except:
            traceback.print_exc()
            self.controller.sendMessage(user_id, self.common_phrases.error)
            self.controller.sendMessage(self.admin_id, self.common_phrases.error_for_admin)

    def extractNumber(self, message, text, max_number: int) -> Optional[int]:
        try:
            number = int(text) - 1
        except:
            self.controller.sendMessage(message.from_user.id,
                                        self.common_phrases.not_number + '. ' + self.common_phrases.try_again)
            return None

        if number < 0 or number >= max_number:
            self.controller.sendMessage(message.from_user.id,
                                        self.common_phrases.number_out_of_bounds + '. ' + self.common_phrases.try_again)
            return None
        return number

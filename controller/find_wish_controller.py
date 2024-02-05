import sys
import traceback
from telebot.types import ReplyParameters
from telebot.types import ReplyKeyboardMarkup
from telebot import types

from case_controller import CaseController
from scenarios import FindWishCase

sys.path.insert(1, '/home/polyushka/WishListBot')
import service
import beans


class FindWishController(CaseController):
    def start(self, message):
        self.controller.sendMessage(message.from_user.id, self.special_phrases.enter_pattern)
        self.__step = FindWishCase.pattern_enter
        self.__matched_contents = []
        self.__wishlists_with_match = {}
        self.__wishlists = []


    def processTextMessage(self, message):
        match self.__step:
            case FindWishCase.pattern_enter:
                self.__enterPattern(message)

            case FindWishCase.choose_option:
                self.__chooseOption(message)

            case FindWishCase.number_enter:
                self.__enterNumber(message)

            case FindWishCase.choose_option_to_edit:
                self.__editChosen(message)

            case FindWishCase.change_name:
                self.__changeName(message)

            case FindWishCase.change_description:
                self.__changeDescription(message)

            case FindWishCase.change_link:
                self.__changeLink(message)

            case FindWishCase.delete_description:
                self.__deleteDescription(message)

            case FindWishCase.delete_link:
                self.__deleteLink(message)

            case FindWishCase.add_to_wishlists:
                self.__addToWishlists(message)

            case FindWishCase.delete_from_wishlists:
                self.__deleteFromWishlists(message)


    def hasFinished(self):
        return self.__step == FindWishCase.has_finished


    def finish(self, message):
        del self.__matched_contents
        del self.__wishlists_with_match
        del self.__wishlists
        self.__step = FindWishCase.has_finished
        self.controller.finishActiveScenario(message.from_user.id)


    def __enterPattern(self, message):
        pattern = message.text
        content_service = service.ContentService()
        all_contents = content_service.getAllUserContents(message.from_user.id)
        for content in all_contents:
            if pattern.lower() in content.name.lower():
                self.__matched_contents.append(content)
                wishlists = content_service.getWishlistsOfContent(content.id)
                CaseController.enumerateBeans(wishlists)
                self.__wishlists_with_match[content.id] = wishlists

        if not self.__matched_contents:
            self.controller.sendMessage(message.from_user.id, self.special_phrases.not_found)
            self.finish(message)
            return

        CaseController.enumerateBeans(self.__matched_contents)
        text = self.special_phrases.matches_here + ':'
        for content in self.__matched_contents:
            text += '\n' + content.toStringWithNumber() + '\n' + self.special_phrases.found_in_wishlists + ':'
            for wishlist in self.__wishlists_with_match[content.id]:
                text += '\n - ' + wishlist.name

        self.__contents_message = self.controller.sendMessage(message.from_user.id, text)
        reply_params = ReplyParameters(message_id = self.__contents_message.message_id)
        self.controller.sendMessage(message.from_user.id, self.special_phrases.what_wish, reply_params = reply_params)
        self.__step = FindWishCase.number_enter


    def __whatNext(self, message):
        markup = ReplyKeyboardMarkup()
        edit_button = types.KeyboardButton(self.special_phrases.edit_wish)
        delete_button = types.KeyboardButton(self.special_phrases.delete_wish)
        nothing_button = types.KeyboardButton(self.common_phrases.nothing)
        add_to_wishlist_button = types.KeyboardButton(self.special_phrases.add_to_wishlist)
        markup.row(edit_button)
        markup.row(add_to_wishlist_button)
        markup.row(delete_button)
        markup.row(nothing_button)
        self.controller.sendMessage(message.from_user.id, self.common_phrases.what_next, reply_markup = markup)
        self.__step = FindWishCase.choose_option


    def __chooseOption(self, message):
        if message.text == self.special_phrases.edit_wish:
            self.__sendEditChoice(message)

        elif message.text == self.special_phrases.add_to_wishlist:
            self.__wishlists = self.getWishlists(message.from_user.id)
            text = self.wishlistsToStr(self.__wishlists)
            self.__wishlists_message = self.controller.sendMessage(message.from_user.id, text)
            reply_params = ReplyParameters(message_id = self.__wishlists_message.message_id)
            self.controller.sendMessage(message.from_user.id,
                                        self.special_phrases.enter_numbers_to_add,
                                        reply_params = reply_params)
            self.__step = FindWishCase.add_to_wishlists

        elif message.text == self.special_phrases.delete_wish:
            content = self.__matched_contents[self.__content_number]
            self.__wishlists = self.__wishlists_with_match[content.id]
            CaseController.enumerateBeans(self.__wishlists)
            text = self.wishlistsToStr(self.__wishlists)
            self.__wishlists_message = self.controller.sendMessage(message.from_user.id, text)
            reply_params = ReplyParameters(message_id = self.__wishlists_message.message_id)
            self.controller.sendMessage(message.from_user.id,
                                        self.special_phrases.enter_numbers_to_delete,
                                        reply_params = reply_params)
            self.__step = FindWishCase.delete_from_wishlists

        elif message.text == self.common_phrases.nothing:
            self.controller.sendMessage(message.from_user.id, self.common_phrases.well)
            self.finish(message)

        else:
            self.controller.sendMessageWishoutSaving(message.from_user.id, self.common_phrases.choose_from_variants)
            self.controller.sendLastMessage(message.from_user.id)


    def __enterNumber(self, message):
        content_number = self.extractNumber(message, message.text, len(self.__matched_contents))
        if content_number is None:
            return
        self.__content_number = content_number
        self.__whatNext(message)


    def __sendEditChoice(self, message):
        content = self.__matched_contents[self.__content_number]

        markup = ReplyKeyboardMarkup()
        change_name_button = types.KeyboardButton(self.special_phrases.change_name)
        markup.row(change_name_button)

        if content.description is None:
            add_description_button = types.KeyboardButton(self.special_phrases.add_description)
            markup.row(add_description_button)
        else:
            change_description_button = types.KeyboardButton(self.special_phrases.change_description)
            markup.row(change_description_button)
            delete_description_button = types.KeyboardButton(self.special_phrases.delete_description)
            markup.row(delete_description_button)

        if content.link is None:
            add_link_button = types.KeyboardButton(self.special_phrases.add_link)
            markup.row(add_link_button)
        else:
            change_link_button = types.KeyboardButton(self.special_phrases.change_link)
            markup.row(change_link_button)
            delete_link_button = types.KeyboardButton(self.special_phrases.delete_link)
            markup.row(delete_link_button)

        nothing_button = types.KeyboardButton(self.common_phrases.nothing)
        markup.row(nothing_button)

        text = self.special_phrases.wish_here + ':\n' + content.toString(self.common_phrases) +\
                        '\n' + self.special_phrases.what_edit
        self.controller.sendMessage(message.from_user.id, text = text, reply_markup = markup)
        self.__step = FindWishCase.choose_option_to_edit


    def __editChosen(self, message):
        if message.text == self.special_phrases.change_name:
            text = self.special_phrases.enter_new_name
            self.__step = FindWishCase.change_name
        elif message.text == self.special_phrases.add_description:
            text = self.special_phrases.enter_description
            self.__step = FindWishCase.change_description
        elif message.text == self.special_phrases.change_description:
            text = self.special_phrases.enter_new_description
            self.__step = FindWishCase.change_description
        elif message.text == self.special_phrases.delete_description:
            self.__deleteDescription(message)
            return
        elif message.text == self.special_phrases.add_link:
            text = self.special_phrases.enter_link
            self.__step = FindWishCase.change_link
        elif message.text == self.special_phrases.change_link:
            text = self.special_phrases.enter_new_link
            self.__step = FindWishCase.change_link
        elif message.text == self.special_phrases.delete_link:
            self.__deleteLink(message)
            return
        elif message.text == self.common_phrases.nothing:
            self.__whatNext(message)
            return
        else:
            self.controller.sendMessageWishoutSaving(message.from_user.id, self.common_phrases.choose_from_variants)
            self.controller.sendLastMessage(message.from_user.id)
            return

        self.controller.sendMessage(message.from_user.id, text)


    def __changeName(self, message):
        content = self.__matched_contents[self.__content_number]
        content_service = service.ContentService()
        try:
            content_service.updateContentName(content.id, message.text)
            content.name = message.text
            self.controller.sendMessage(message.from_user.id, self.common_phrases.done)

            if content.gifter_id is not None:
                user_service = service.UserService()
                owner = user_service.findUserById(message.from_user.id)
                text = self.special_phrases.wish_was_edited % ('<b>@' + owner.username + '</b>') + ':\n' +\
                            content.toString(self.common_phrases)
                self.controller.sendMessage(content.gifter_id, text)
        except:
            self.handleError(message)
            self.finish(message)
            return
        self.__sendEditChoice(message)


    def __changeDescription(self, message):
        content = self.__matched_contents[self.__content_number]
        content_service = service.ContentService()
        try:
            content_service.updateContentDescription(content.id, message.text)
            content.description = message.text
            self.controller.sendMessage(message.from_user.id, self.common_phrases.done)

            if content.gifter_id is not None:
                user_service = service.UserService()
                owner = user_service.findUserById(message.from_user.id)
                text = self.special_phrases.wish_was_edited % ('<b>@' + owner.username + '</b>') + ':\n' +\
                            content.toString(self.common_phrases)
                self.controller.sendMessage(content.gifter_id, text)
        except:
            self.handleError(message)
            self.finish(message)
            return
        self.__sendEditChoice(message)


    def __changeLink(self, message):
        content = self.__matched_contents[self.__content_number]
        content_service = service.ContentService()
        try:
            content_service.updateContentLink(content.id, message.text)
            content.link = message.text
            self.controller.sendMessage(message.from_user.id, self.common_phrases.done)

            if content.gifter_id is not None:
                user_service = service.UserService()
                owner = user_service.findUserById(message.from_user.id)
                text = self.special_phrases.wish_was_edited % ('<b>@' + owner.username + '</b>') + ':\n' +\
                            content.toString(self.common_phrases)
                self.controller.sendMessage(content.gifter_id, text)
        except:
            self.handleError(message)
            self.finish(message)
            return
        self.__sendEditChoice(message)


    def __deleteDescription(self, message):
        content = self.__matched_contents[self.__content_number]
        content_service = service.ContentService()
        try:
            content_service.deleteContentDescription(content.id)
            content.description = None
            self.controller.sendMessage(message.from_user.id, self.common_phrases.done)

            if content.gifter_id is not None:
                user_service = service.UserService()
                owner = user_service.findUserById(message.from_user.id)
                text = self.special_phrases.wish_was_edited % ('<b>@' + owner.username + '</b>') + ':\n' +\
                            content.toString(self.common_phrases)
                self.controller.sendMessage(content.gifter_id, text)
        except:
            self.handleError(message)
            self.finish(message)
            return
        self.__sendEditChoice(message)


    def __deleteLink(self, message):
        content = self.__matched_contents[self.__content_number]
        content_service = service.ContentService()
        try:
            content_service.deleteContentLink(content.id)
            content.link = None
            self.controller.sendMessage(message.from_user.id, self.common_phrases.done)

            if content.gifter_id is not None:
                user_service = service.UserService()
                owner = user_service.findUserById(message.from_user.id)
                text = self.special_phrases.wish_was_edited % ('<b>@' + owner.username + '</b>') + ':\n' +\
                            content.toString(self.common_phrases)
                self.controller.sendMessage(content.gifter_id, text)
        except:
            self.handleError(message)
            self.finish(message)
            return
        self.__sendEditChoice(message)


    def __addToWishlists(self, message):
        numbers_str = message.text.split(' ')
        wishlists_numbers = []
        for number in numbers_str:
            wishlist_number = self.extractNumber(message, number, len(self.__wishlists))
            if wishlist_number is None:
                return
            wishlists_numbers.append(wishlist_number)
        wishlists_numbers = list(set(wishlists_numbers))

        content = self.__matched_contents[self.__content_number]
        content_service = service.ContentService()
        content_service.beginTransaction()
        for wishlist_number in wishlists_numbers:
            wishlist = self.__wishlists[wishlist_number]
            if wishlist.id not in [item.id for item in self.__wishlists_with_match[content.id]]:
                try:
                    content_service.addExistingContentToWishlist(wishlist_id = wishlist.id, content_id = content.id)
                    self.__wishlists_with_match[content.id].append(wishlist)
                except:
                    self.handleError(message)
                    self.finish(message)
                    return
        try:
            content_service.commit()
        except:
            self.handleError(message)
            self.finish(message)
            return
        self.controller.sendMessage(message.from_user.id, self.common_phrases.done)
        self.__whatNext(message)


    def __deleteFromWishlists(self, message):
        numbers_str = message.text.split(' ')
        wishlists_numbers = []
        for number in numbers_str:
            wishlist_number = self.extractNumber(message, number, len(self.__wishlists))
            if wishlist_number is None:
                return
            wishlists_numbers.append(wishlist_number)
        wishlists_numbers = list(set(wishlists_numbers))

        content = self.__matched_contents[self.__content_number]
        content_copy = beans.ContentBean(id = content.id,
                                         name = content.name,
                                         description = content.description,
                                         link = content.link,
                                         gifter_id = content.gifter_id)
        content_service = service.ContentService()
        content_service.beginTransaction()
        for wishlist_number in wishlists_numbers:
            wishlist = self.__wishlists[wishlist_number]
            try:
                content_service.deleteContentFromWishlist(wishlist_id = wishlist.id, content_id = content.id)
                index = self.__wishlists_with_match[content.id].index(wishlist)
                self.__wishlists_with_match[content.id][index] = None
            except:
                self.handleError(message)
                self.finish(message)
                return
        try:
            content_service.commit()
        except:
            self.handleError(message)
            self.finish(message)
            return
        self.__wishlists_with_match[content.id] = [item for item in self.__wishlists_with_match[content.id] if item is not None]

        if not self.__wishlists_with_match[content.id]:
            try:
                content_service.deleteContent(content.id)

                if content_copy.gifter_id is not None:
                    user_service = service.UserService()
                    owner = user_service.findUserById(message.from_user.id)
                    text = self.special_phrases.wish_was_deleted % (content_copy.toString(self.common_phrases), '<b>@' + owner.username + '</b>') +\
                                ':\n' + content.toString(self.common_phrases)
                    self.controller.sendMessage(content_copy.gifter_id, text)
            except:
                traceback.print_exc()
                self.controller.sendMessage(self.admin_id, self.common_phrases.error_for_admin)
            self.controller.sendMessage(message.from_user.id, self.common_phrases.done)
            self.finish(message)
        else:
            self.controller.sendMessage(message.from_user.id, self.common_phrases.done)
            self.__whatNext(message)

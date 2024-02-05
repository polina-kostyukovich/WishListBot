import telebot
import sys

import beans
from abstract_bot import Bot
sys.path.insert(1, '/home/polyushka/WishListBot/controller')
from controller import Controller


class WishlistBot(Bot):
    bot = telebot.TeleBot("<token>", parse_mode = 'HTML')
    controller = None

    @staticmethod
    def run():
        WishlistBot.bot.infinity_polling(timeout=10, long_polling_timeout = 5)

    @staticmethod
    @bot.message_handler(commands=['start'])
    def start(message):
        user = beans.UserBean(id = message.from_user.id, username = message.from_user.username)
        WishlistBot.controller.registerUser(user)

    @staticmethod
    @bot.message_handler(commands=['create_wishlist'])
    def createWishlist(message):
        WishlistBot.controller.setCreateWishlistCase(message)

    @staticmethod
    @bot.message_handler(commands=['list_my_wishlists'])
    def listWishlists(message):
        WishlistBot.controller.setListWishlistsCase(message)

    @staticmethod
    @bot.message_handler(commands=['edit_wishlist'])
    def editWishlist(message):
        WishlistBot.controller.setEditWishlistCase(message)

    @staticmethod
    @bot.message_handler(commands=['add_wish'])
    def addWish(message):
        WishlistBot.controller.setAddWishCase(message)

    @staticmethod
    @bot.message_handler(commands=['find_and_edit_wish'])
    def findWish(message):
        WishlistBot.controller.setFindWishCase(message)

    @staticmethod
    @bot.message_handler(commands=['manage_access'])
    def manageAccess(message):
        WishlistBot.controller.setManageAccessCase(message)

    @staticmethod
    @bot.message_handler(commands=['see_friend_wishlist'])
    def seeFriendWishlist(message):
        WishlistBot.controller.setSeeFriendWishlistCase(message)

    @staticmethod
    @bot.message_handler(commands=['cancel'])
    def cancelWishlist(message):
        WishlistBot.controller.cancel(message)

    @staticmethod
    @bot.message_handler(content_types=['text'])
    def getTextMessage(message):
        WishlistBot.controller.processTextMessage(message)

    def sendMessage(self, user_id: int, message: str, reply_markup, reply_parameters):
        return WishlistBot.bot.send_message(user_id, message, reply_markup=reply_markup, reply_parameters=reply_parameters)


if __name__ == '__main__':
    if len(sys.argv) < 2:
        raise Exception('no setup filename was found')

    wishlist_bot = WishlistBot()
    phrases_file_name = 'settings/phrases_ru.json'
    controller = Controller(sys.argv[1], phrases_file_name, wishlist_bot)
    WishlistBot.controller = controller

    commands_descriptions = controller.getCommandsDescriptions()
    WishlistBot.bot.set_my_commands([
        telebot.types.BotCommand("/create_wishlist", commands_descriptions.create_wishlist),
        telebot.types.BotCommand("/list_my_wishlists", commands_descriptions.list_wishlists),
        telebot.types.BotCommand("/edit_wishlist", commands_descriptions.edit_wishlist),
        telebot.types.BotCommand("/add_wish", commands_descriptions.add_wish),
        telebot.types.BotCommand("/find_and_edit_wish", commands_descriptions.find_and_edit_wish),
        telebot.types.BotCommand("/manage_access", commands_descriptions.manage_access),
        telebot.types.BotCommand("/see_friend_wishlist", commands_descriptions.see_friend_wishlist),
        telebot.types.BotCommand("/cancel", commands_descriptions.cancel)
    ])

    WishlistBot.run()

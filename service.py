import mysql.connector
from typing import Optional

import dao
import beans
from exceptions import ServiceException


class Transaction:
    __database_info = {}

    @staticmethod
    def setDatabaseInfo(info: dict):
        Transaction.__database_info['host'] = info['host']
        Transaction.__database_info['user'] = info['user']
        Transaction.__database_info['password'] = info['password']
        Transaction.__database_info['database'] = info['database']

    def __init__(self):
        self.__connection = mysql.connector.connect(
                host=Transaction.__database_info['host'],
                user=Transaction.__database_info['user'],
                password=Transaction.__database_info['password'],
                database=Transaction.__database_info['database']
            )

    def __del__(self):
        self.__connection.close()

    def commit(self):
        self.__connection.commit()

    def getConnection(self):
        return self.__connection


class Service:
    def __init__(self):
        self.transaction = None

    def beginTransaction(self):
        self.transaction = Transaction()

    def commit(self):
        self.transaction.commit()
        del self.transaction
        self.transaction = None


class UserService(Service):
    def createUserSafe(self, user: beans.UserBean):
        if user is None:
            raise ServiceException("user is None")
        if not user.isCorrect():
            raise ServiceException("user is incorrect")

        transaction = Transaction() if self.transaction is None else self.transaction
        users_dao = dao.UsersDao(transaction.getConnection())
        if users_dao.findById(id = user.id) is None:
            users_dao.create(user)
            if self.transaction is None:
                transaction.commit()


    def findUserById(self, user_id: int) -> Optional[beans.UserBean]:
        if user_id is None:
            raise ServiceException("user_id is None")

        transaction = Transaction() if self.transaction is None else self.transaction
        users_dao = dao.UsersDao(transaction.getConnection())
        return users_dao.findById(user_id)


    def findUserByUsername(self, username: str) -> Optional[beans.UserBean]:
        if username is None:
            raise ServiceException("username is None")

        transaction = Transaction() if self.transaction is None else self.transaction
        users_dao = dao.UsersDao(transaction.getConnection())
        return users_dao.findByUsername(username)


    def getWishlistReaders(self, wishlist_id: int) -> list[beans.UserBean]:
        if wishlist_id is None:
            raise ServiceException("wishlist_id is None")

        transaction = Transaction() if self.transaction is None else self.transaction
        readers_dao = dao.ReadersDao(transaction.getConnection())
        return readers_dao.getReaders(wishlist_id = wishlist_id)


    def addReaderToWishlist(self, reader_id: int, wishlist_id: int):
        if wishlist_id is None:
            raise ServiceException("wishlist_id is None")
        if reader_id is None:
            raise ServiceException("reader_id is None")

        transaction = Transaction() if self.transaction is None else self.transaction
        readers_dao = dao.ReadersDao(transaction.getConnection())
        readers_dao.addReaderToWishlist(reader_id = reader_id, wishlist_id = wishlist_id)
        if self.transaction is None:
            transaction.commit()


    def deleteReaderFromWishlist(self, reader_id: int, wishlist_id: int):
        if wishlist_id is None:
            raise ServiceException("wishlist_id is None")
        if reader_id is None:
            raise ServiceException("reader_id is None")

        transaction = Transaction() if self.transaction is None else self.transaction
        readers_dao = dao.ReadersDao(transaction.getConnection())
        readers_dao.deleteReaderFromWishlist(reader_id = reader_id, wishlist_id = wishlist_id)
        if self.transaction is None:
            transaction.commit()


class WishlistService(Service):
    def createWishlist(self, wishlist: beans.WishlistBean):
        if wishlist is None:
            raise ServiceException("wishlist is None")
        wishlist.id = 0
        if not wishlist.isCorrect():
            raise ServiceException("wishlist is incorrect")

        transaction = Transaction() if self.transaction is None else self.transaction
        wishlist_dao = dao.WishlistDao(transaction.getConnection())
        wishlist_dao.create(wishlist)
        if self.transaction is None:
            transaction.commit()


    def findWishlistById(self, wishlist_id: int) -> Optional[beans.WishlistBean]:
        if wishlist_id is None:
            raise ServiceException("wishlist_id is None")

        transaction = Transaction() if self.transaction is None else self.transaction
        wishlist_dao = dao.WishlistDao(transaction.getConnection())
        return wishlist_dao.findById(wishlist_id)


    def getUserWishlists(self, user_id: int):
        if user_id is None:
            raise ServiceException("user_id is None")

        transaction = Transaction() if self.transaction is None else self.transaction
        wishlist_dao = dao.WishlistDao(transaction.getConnection())
        wishlists = wishlist_dao.findByOwnerId(user_id)
        return wishlists


    def updateWishlistName(self, wishlist_id: int, new_name: str):
        if wishlist_id is None:
            raise ServiceException("wishlist_id is None")
        if new_name is None:
            raise ServiceException("new_name is None")

        transaction = Transaction() if self.transaction is None else self.transaction
        wishlist_dao = dao.WishlistDao(transaction.getConnection())
        wishlist_dao.updateName(id = wishlist_id, new_name = new_name)
        if self.transaction is None:
            transaction.commit()


    def updateWishlistDescription(self, wishlist_id: int, new_description: str):
        if wishlist_id is None:
            raise ServiceException("wishlist_id is None")
        if new_description is None:
            raise ServiceException("new_description is None")

        transaction = Transaction() if self.transaction is None else self.transaction
        wishlist_dao = dao.WishlistDao(transaction.getConnection())
        wishlist_dao.updateDescription(id = wishlist_id, new_description = new_description)
        if self.transaction is None:
            transaction.commit()


    def deleteWishlistDescription(self, wishlist_id: int):
        if wishlist_id is None:
            raise ServiceException("wishlist_id is None")

        transaction = Transaction() if self.transaction is None else self.transaction
        wishlist_dao = dao.WishlistDao(transaction.getConnection())
        wishlist_dao.deleteDescription(id = wishlist_id)
        if self.transaction is None:
            transaction.commit()


    def deleteWishlist(self, wishlist_id: int) -> list[beans.ContentBean]:
        if wishlist_id is None:
            raise ServiceException("wishlist_id is None")

        transaction = Transaction() if self.transaction is None else self.transaction
        wc_dao = dao.WishlistContentsDao(transaction.getConnection())
        unique_contents = wc_dao.deleteAndGetUniqueContentsOfWishlist(wishlist_id = wishlist_id)

        wishlist_dao = dao.WishlistDao(transaction.getConnection())
        wishlist_dao.delete(id = wishlist_id)
        if self.transaction is None:
            transaction.commit()
        return unique_contents


class ContentService(Service):
    def getWishlistContents(self, wishlist_id: int) -> list[beans.ContentBean]:
        if wishlist_id is None:
            raise ServiceException("wishlist_id is None")

        transaction = Transaction() if self.transaction is None else self.transaction
        wc_dao = dao.WishlistContentsDao(transaction.getConnection())
        contents = wc_dao.getContentsOfWishlist(wishlist_id)
        return contents


    def addContentToWishlist(self, content: beans.ContentBean, wishlist_id: int):
        if wishlist_id is None:
            raise ServiceException("wishlist_id is None")
        if content is None:
            raise ServiceException("content is None")
        content.id = 0
        if not content.isCorrect():
            raise ServiceException("content is incorrect")

        transaction = Transaction() if self.transaction is None else self.transaction
        content_dao = dao.ContentDao(transaction.getConnection())
        wc_dao = dao.WishlistContentsDao(transaction.getConnection())
        content_id = content_dao.create(content)
        content.id = content_id
        wc_dao.addContentToWishlist(wishlist_id = wishlist_id, content_id = content_id)
        if self.transaction is None:
            transaction.commit()


    def addExistingContentToWishlist(self, wishlist_id: int, content_id: int):
        if wishlist_id is None:
            raise ServiceException("wishlist_id is None")
        if content_id is None:
            raise ServiceException("content_id is None")

        transaction = Transaction() if self.transaction is None else self.transaction
        wc_dao = dao.WishlistContentsDao(transaction.getConnection())
        wc_dao.addContentToWishlist(wishlist_id = wishlist_id, content_id = content_id)
        if self.transaction is None:
            transaction.commit()


    def deleteContentFromWishlist(self, wishlist_id: int, content_id: int):
        if wishlist_id is None:
            raise ServiceException("wishlist_id is None")
        if content_id is None:
            raise ServiceException("content_id is None")

        transaction = Transaction() if self.transaction is None else self.transaction
        wc_dao = dao.WishlistContentsDao(transaction.getConnection())
        wc_dao.deleteContentFromWishlist(wishlist_id = wishlist_id, content_id = content_id)
        if self.transaction is None:
            transaction.commit()


    def getAllUserContents(self, user_id: int) -> list[beans.ContentBean]:
        if user_id is None:
            raise ServiceException("user_id is None")

        transaction = Transaction() if self.transaction is None else self.transaction
        wishlist_dao = dao.WishlistDao(transaction.getConnection())
        wc_dao = dao.WishlistContentsDao(transaction.getConnection())
        wishlists = wishlist_dao.findByOwnerId(user_id)
        contents = []
        for wishlist in wishlists:
            contents.extend(wc_dao.getContentsOfWishlist(wishlist.id))

        unique_contents = list(set(contents))
        return unique_contents


    def getWishlistsOfContent(self, content_id: int) -> list[beans.WishlistBean]:
        if content_id is None:
            raise ServiceException("content_id is None")

        transaction = Transaction() if self.transaction is None else self.transaction
        wc_dao = dao.WishlistContentsDao(transaction.getConnection())
        return wc_dao.getWishlistsOfContent(content_id)


    def deleteContent(self, content_id: int):
        if content_id is None:
            raise ServiceException("content_id is None")

        transaction = Transaction() if self.transaction is None else self.transaction
        content_dao = dao.ContentDao(transaction.getConnection())
        content_dao.delete(content_id)
        if self.transaction is None:
            transaction.commit()


    def updateContentName(self, content_id: int, new_name: str):
        if content_id is None:
            raise ServiceException("content_id is None")
        if new_name is None:
            raise ServiceException("new_name is None")

        transaction = Transaction() if self.transaction is None else self.transaction
        content_dao = dao.ContentDao(transaction.getConnection())
        content_dao.updateName(content_id, new_name)
        if self.transaction is None:
            transaction.commit()


    def updateContentDescription(self, content_id: int, new_description: str):
        if content_id is None:
            raise ServiceException("content_id is None")
        if new_description is None:
            raise ServiceException("new_description is None")

        transaction = Transaction() if self.transaction is None else self.transaction
        content_dao = dao.ContentDao(transaction.getConnection())
        content_dao.updateDescription(content_id, new_description)
        if self.transaction is None:
            transaction.commit()


    def updateContentLink(self, content_id: int, new_link: str):
        if content_id is None:
            raise ServiceException("content_id is None")
        if new_link is None:
            raise ServiceException("new_link is None")

        transaction = Transaction() if self.transaction is None else self.transaction
        content_dao = dao.ContentDao(transaction.getConnection())
        content_dao.updateLink(content_id, new_link)
        if self.transaction is None:
            transaction.commit()


    def deleteContentDescription(self, content_id: int):
        if content_id is None:
            raise ServiceException("content_id is None")

        transaction = Transaction() if self.transaction is None else self.transaction
        content_dao = dao.ContentDao(transaction.getConnection())
        content_dao.deleteDescription(content_id)
        if self.transaction is None:
            transaction.commit()


    def deleteContentLink(self, content_id: int):
        if content_id is None:
            raise ServiceException("content_id is None")

        transaction = Transaction() if self.transaction is None else self.transaction
        content_dao = dao.ContentDao(transaction.getConnection())
        content_dao.deleteLink(content_id)
        if self.transaction is None:
            transaction.commit()


    def reserveContent(self, content_id: int, gifter_id: int):
        if content_id is None:
            raise ServiceException("content_id is None")
        if gifter_id is None:
            raise ServiceException("gifter_id is None")

        transaction = Transaction() if self.transaction is None else self.transaction
        content_dao = dao.ContentDao(transaction.getConnection())
        content_dao.updateGifter(content_id, gifter_id)
        if self.transaction is None:
            transaction.commit()


    def unreserveContent(self, content_id: int):
        if content_id is None:
            raise ServiceException("content_id is None")

        transaction = Transaction() if self.transaction is None else self.transaction
        content_dao = dao.ContentDao(transaction.getConnection())
        content_dao.deleteGifter(content_id)
        if self.transaction is None:
            transaction.commit()

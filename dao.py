import beans
from typing import Optional
from exceptions import DaoException


class Dao:
    def __init__(self, connection):
        self.connection = connection


class UsersDao(Dao):
    SQL_CREATE_USER = "INSERT INTO users VALUES (%s, %s);"
    SQL_FIND_BY_ID = "SELECT * FROM users WHERE id = %s;"
    SQL_FIND_BY_USERNAME = "SELECT * FROM users WHERE username = %s;"


    def create(self, user: beans.UserBean):
        if user is None:
            raise DaoException("user is None")
        if not user.isCorrect():
            raise DaoException("user is incorrect")

        user_info = (user.id, user.username)
        with self.connection.cursor() as cursor:
            cursor.execute(self.SQL_CREATE_USER, user_info)


    def findById(self, id: int) -> Optional[beans.UserBean]:
        if id is None:
            raise DaoException("user id is None")

        with self.connection.cursor() as cursor:
            cursor.execute(self.SQL_FIND_BY_ID, [id])
            result = cursor.fetchall()
            if not result:
                return None
            else:
                user = beans.UserBean(id = result[0][0],
                                      username = result[0][1])
                return user


    def findByUsername(self, username: str) -> Optional[beans.UserBean]:
        if username is None:
            raise DaoException("username is None")

        with self.connection.cursor() as cursor:
            cursor.execute(self.SQL_FIND_BY_USERNAME, [username])
            result = cursor.fetchall()
            if not result:
                return None
            else:
                user = beans.UserBean(id = result[0][0],
                                      username = result[0][1])
                return user


class WishlistDao(Dao):
    SQL_CREATE_WISHLIST = "INSERT INTO wishlists (owner_id, name, description) VALUES (%s, %s, %s);"
    SQL_UPDATE_NAME = "UPDATE wishlists SET name = %s WHERE id = %s;"
    SQL_UPDATE_DESCRIPTION = "UPDATE wishlists SET description = %s WHERE id = %s;"
    SQL_DELETE_WISHLIST = "DELETE FROM wishlists WHERE id = %s;"
    SQL_FIND_BY_ID = "SELECT id, owner_id, name, description FROM wishlists WHERE id = %s;"
    SQL_FIND_BY_OWNER_ID = "SELECT id, owner_id, name, description FROM wishlists WHERE owner_id = %s;"


    def create(self, wishlist: beans.WishlistBean):
        if wishlist is None:
            raise DaoException("wishlist is None")
        if not wishlist.isCorrect():
            raise DaoException("wishlist is incorrect")

        wishlist_info = [wishlist.owner_id, wishlist.name, wishlist.description]
        with self.connection.cursor() as cursor:
            cursor.execute(self.SQL_CREATE_WISHLIST, wishlist_info)


    def updateName(self, id: int, new_name: str):
        if id is None:
            raise DaoException("id is None")
        if new_name is None:
            raise DaoException("new_name is None")

        with self.connection.cursor() as cursor:
            cursor.execute(self.SQL_UPDATE_NAME, [new_name, id])


    def updateDescription(self, id: int, new_description: str):
        if id is None:
            raise DaoException("id is None")
        if new_description is None:
            raise DaoException("new_description is None")

        with self.connection.cursor() as cursor:
            cursor.execute(self.SQL_UPDATE_DESCRIPTION, [new_description, id])


    def deleteDescription(self, id: int):
        if id is None:
            raise DaoException("id is None")

        with self.connection.cursor() as cursor:
            cursor.execute(self.SQL_UPDATE_DESCRIPTION, [None, id])


    def delete(self, id: int):
        if id is None:
            raise DaoException("id is None")

        with self.connection.cursor() as cursor:
            cursor.execute(self.SQL_DELETE_WISHLIST, [id])


    def findById(self, id: int) -> Optional[beans.WishlistBean]:
        if id is None:
            raise DaoException("id is None")

        with self.connection.cursor() as cursor:
            cursor.execute(self.SQL_FIND_BY_ID, [id])
            result = cursor.fetchall()
            if not result:
                return None
            else:
                wishlist = beans.WishlistBean(id = result[0][0],
                                              owner_id = result[0][1],
                                              name = result[0][2],
                                              description = result[0][3])
                return wishlist


    def findByOwnerId(self, owner_id: int) -> list[beans.WishlistBean]:
        if owner_id is None:
            raise DaoException("owner_id is None")

        with self.connection.cursor() as cursor:
            cursor.execute(self.SQL_FIND_BY_OWNER_ID, [owner_id])
            result = cursor.fetchall()
            wishlists = []
            for wishlist in result:
                wishlists.append(beans.WishlistBean(id = wishlist[0],
                                                    owner_id = wishlist[1],
                                                    name = wishlist[2],
                                                    description = wishlist[3]))
            return wishlists


class ContentDao(Dao):
    SQL_CREATE_CONTENT = "INSERT INTO contents (name, description, link, gifter_id) VALUES (%s, %s, %s, %s);"
    SQL_UPDATE_NAME = "UPDATE contents SET name = %s WHERE id = %s;"
    SQL_UPDATE_DESCRIPTION = "UPDATE contents SET description = %s WHERE id = %s;"
    SQL_UPDATE_LINK = "UPDATE contents SET link = %s WHERE id = %s;"
    SQL_UPDATE_GIFTER = "UPDATE contents SET gifter_id = %s WHERE id = %s;"
    SQL_DELETE_CONTENT = "DELETE FROM contents WHERE id = %s;"
    SQL_FIND_BY_ID = "SELECT * FROM contents WHERE id = %s;"

    def create(self, content: beans.ContentBean):
        if content is None:
            raise DaoException("content is None")
        if not content.isCorrect():
            raise DaoException("content is incorrect")

        content_info = [content.name, content.description, content.link, content.gifter_id]
        with self.connection.cursor() as cursor:
            cursor.execute(self.SQL_CREATE_CONTENT, content_info)
            return cursor.lastrowid


    def updateName(self, id: int, new_name: str):
        if id is None:
            raise DaoException("id is None")
        if new_name is None:
            raise DaoException("new_name is None")

        with self.connection.cursor() as cursor:
            cursor.execute(self.SQL_UPDATE_NAME, [new_name, id])


    def updateDescription(self, id: int, new_description: str):
        if id is None:
            raise DaoException("id is None")
        if new_description is None:
            raise DaoException("new_description is None")

        with self.connection.cursor() as cursor:
            cursor.execute(self.SQL_UPDATE_DESCRIPTION, [new_description, id])


    def updateLink(self, id: int, new_link: str):
        if id is None:
            raise DaoException("id is None")
        if new_link is None:
            raise DaoException("new_link is None")

        with self.connection.cursor() as cursor:
            cursor.execute(self.SQL_UPDATE_LINK, [new_link, id])


    def updateGifter(self, id: int, new_gifter_id: int):
        if id is None:
            raise DaoException("id is None")
        if new_gifter_id is None:
            raise DaoException("new_gifter_id is None")

        with self.connection.cursor() as cursor:
            cursor.execute(self.SQL_UPDATE_GIFTER, [new_gifter_id, id])


    def deleteGifter(self, id: int):
        if id is None:
            raise DaoException("id is None")

        with self.connection.cursor() as cursor:
            cursor.execute(self.SQL_UPDATE_GIFTER, [None, id])


    def deleteDescription(self, id: int):
        if id is None:
            raise DaoException("id is None")

        with self.connection.cursor() as cursor:
            cursor.execute(self.SQL_UPDATE_DESCRIPTION, [None, id])


    def deleteLink(self, id: int):
        if id is None:
            raise DaoException("id is None")

        with self.connection.cursor() as cursor:
            cursor.execute(self.SQL_UPDATE_LINK, [None, id])


    def delete(self, id: int):
        if id is None:
            raise DaoException("id is None")

        with self.connection.cursor() as cursor:
            cursor.execute(self.SQL_DELETE_CONTENT, [id])


    def findById(self, id: int) -> Optional[beans.ContentBean]:
        if id is None:
            raise DaoException("id is None")

        with self.connection.cursor() as cursor:
            cursor.execute(self.SQL_FIND_BY_ID, [id])
            result = cursor.fetchall()
            if not result:
                return None
            else:
                content = beans.ContentBean(id = result[0][0],
                                            name = result[0][1],
                                            description = result[0][2],
                                            link = result[0][3],
                                            gifter_id = result[0][4])
                return content


class WishlistContentsDao(Dao):
    SQL_CREATE_WISHLIST_CONTENT = "INSERT INTO wishlists_contents (wishlist_id, content_id) VALUES (%s, %s);"
    SQL_DELETE_WISHLIST_CONTENT = "DELETE FROM wishlists_contents WHERE wishlist_id = %s AND content_id = %s;"
    SQL_GET_CONTENTS_OF_WISHLIST = """
        SELECT id, name, description, link, gifter_id FROM
        contents JOIN (
            SELECT * FROM wishlists_contents WHERE wishlist_id = %s
        ) AS conts
        ON contents.id = conts.content_id;"""
    SQL_GET_WISHLISTS_OF_CONTENT = """
        SELECT id, owner_id, name, description FROM
        wishlists JOIN (
            SELECT * FROM wishlists_contents WHERE content_id = %s
        ) AS wishls
        ON wishlists.id = wishls.wishlist_id;"""
    SQL_GET_UNIQUE_CONTENTS_OF_WISHLIST = """
        SELECT * FROM contents WHERE id IN (
	        SELECT id FROM (
		        SELECT content_id AS id FROM wishlists_contents
		        WHERE wishlist_id = %s
	        ) AS needed_ids
	        JOIN (
		        SELECT content_id FROM (
		        	SELECT content_id, COUNT(*) AS wishlists_count FROM wishlists_contents
		        	GROUP BY content_id
	        	) AS grouped_contents
	        	WHERE wishlists_count = 1
        	) AS unique_ids
        	ON needed_ids.id = unique_ids.content_id
        );"""
    SQL_GET_UNIQUE_CONTENTS_OF_WISHLIST = "DELETE FROM contents WHERE id IN %s;"

    def addContentToWishlist(self, wishlist_id: int, content_id: int):
        if wishlist_id is None:
            raise DaoException("wishlist_id is None")
        if content_id is None:
            raise DaoException("content_id is None")

        with self.connection.cursor() as cursor:
            cursor.execute(self.SQL_CREATE_WISHLIST_CONTENT, [wishlist_id, content_id])


    def deleteContentFromWishlist(self, wishlist_id: int, content_id: int):
        if wishlist_id is None:
            raise DaoException("wishlist_id is None")
        if content_id is None:
            raise DaoException("content_id is None")

        with self.connection.cursor() as cursor:
            cursor.execute(self.SQL_DELETE_WISHLIST_CONTENT, [wishlist_id, content_id])


    def getContentsOfWishlist(self, wishlist_id: int) -> list[beans.ContentBean]:
        if wishlist_id is None:
            raise DaoException("wishlist_id is None")

        with self.connection.cursor() as cursor:
            cursor.execute(self.SQL_GET_CONTENTS_OF_WISHLIST, [wishlist_id])
            result = cursor.fetchall()
            contents = [beans.ContentBean(content[0], None, content[1], content[2], content[3], content[4]) for content in result]
            return contents


    def getWishlistsOfContent(self, content_id: int) -> list[beans.WishlistBean]:
        if content_id is None:
            raise DaoException("content_id is None")

        with self.connection.cursor() as cursor:
            cursor.execute(self.SQL_GET_WISHLISTS_OF_CONTENT, [content_id])
            result = cursor.fetchall()
            wishlists = [beans.WishlistBean(wishlist[0], wishlist[1], wishlist[2], wishlist[3]) for wishlist in result]
            return wishlists


    def deleteAndGetUniqueContentsOfWishlist(self, wishlist_id: int) -> list[beans.ContentBean]:
        if wishlist_id is None:
            raise DaoException("id is None")

        with self.connection.cursor() as cursor:
            cursor.execute(self.SQL_GET_UNIQUE_CONTENTS_OF_WISHLIST, [wishlist_id])
            result = cursor.fetchall()
            contents = []
            for content in result:
                contents.append(beans.ContentBean(id = content[0],
                                                  name = content[1],
                                                  description = content[2],
                                                  link = content[3],
                                                  gifter_id = content[4]))

            ids = [content.id for content in result]
            cursor.execute(self.SQL_DElETE_UNIQUE_CONTENTS_OF_WISHLIST, str(tuple(ids)))

        return contents


class ReadersDao(Dao):
    SQL_GET_READERS = """
        SELECT id, username FROM
        users JOIN (
            SELECT * FROM wishlists_readers WHERE wishlist_id = %s
        ) AS readers
        ON users.id = readers.reader_id;"""
    SQL_INSERT_WISHLIST_READER = "INSERT INTO wishlists_readers (wishlist_id, reader_id) VALUES (%s, %s);"
    SQL_DELETE_WISHLIST_READER = "DELETE FROM wishlists_readers WHERE wishlist_id = %s AND reader_id = %s;"


    def getReaders(self, wishlist_id: int) -> list[beans.UserBean]:
        if wishlist_id is None:
            raise DaoException("wishlist_id is None")

        with self.connection.cursor() as cursor:
            cursor.execute(self.SQL_GET_READERS, [wishlist_id])
            result = cursor.fetchall()
            readers = [beans.UserBean(id = user[0], username = user[1]) for user in result]
            return readers


    def addReaderToWishlist(self, reader_id: int, wishlist_id: int):
        if wishlist_id is None:
            raise DaoException("wishlist_id is None")
        if reader_id is None:
            raise DaoException("reader_id is None")

        with self.connection.cursor() as cursor:
            cursor.execute(self.SQL_INSERT_WISHLIST_READER, [wishlist_id, reader_id])


    def deleteReaderFromWishlist(self, reader_id: int, wishlist_id: int):
        if wishlist_id is None:
            raise DaoException("wishlist_id is None")
        if reader_id is None:
            raise DaoException("reader_id is None")

        with self.connection.cursor() as cursor:
            cursor.execute(self.SQL_DELETE_WISHLIST_READER, [wishlist_id, reader_id])

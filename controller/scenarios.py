import enum


@enum.unique
class CreateWishlistCase(enum.Enum):
    name_enter = 1
    description_enter_ask = 2
    description_enter = 3
    correct_ask = 4
    has_finished = 5


@enum.unique
class ListWishlistsCase(enum.Enum):
    see_wishlist_ask = 1
    choose_wishlist = 2
    has_finished = 3


@enum.unique
class EditWishlistCase(enum.Enum):
    number_enter = 1
    choose_option = 2
    change_name = 3
    change_description = 4
    has_finished = 5


@enum.unique
class AddWishCase(enum.Enum):
    choose_wishlist = 1
    name_enter = 2
    description_enter_ask = 3
    description_enter = 4
    link_enter_ask = 5
    link_enter = 6
    correct_ask = 7
    add_to_another_wishlist_ask = 8
    add_to_another_wishlist = 9
    add_another_wish = 10
    has_finished = 11


@enum.unique
class FindWishCase(enum.Enum):
    pattern_enter = 1
    choose_option = 2
    number_enter = 3
    choose_option_to_edit = 4
    change_name = 5
    change_description = 6
    change_link = 7
    delete_description = 8
    delete_link = 9
    add_to_wishlists = 10
    delete_from_wishlists = 11
    has_finished = 12


@enum.unique
class ManageAccessCase(enum.Enum):
    choose_wishlist = 1
    choose_option = 2
    username_enter = 3
    has_finished = 4


@enum.unique
class SeeFriendWishlistCase(enum.Enum):
    username_enter = 1
    choose_option = 2
    number_enter_to_reserve = 3
    number_enter_to_unreserve = 4
    has_finished = 5

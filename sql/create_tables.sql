CREATE TABLE users (
	id BIGINT,
	username VARCHAR(32) NOT NULL,
	CONSTRAINT PK_users PRIMARY KEY(id),
	CONSTRAINT UNIQUE_users_username UNIQUE(username)
);

CREATE TABLE wishlists (
	id INTEGER AUTO_INCREMENT,
	owner_id BIGINT NOT NULL,
	name VARCHAR(128) NOT NULL,
	description TEXT,
	CONSTRAINT PK_wishlists PRIMARY KEY(id),
	CONSTRAINT FK_wishlists_users FOREIGN KEY(owner_id) REFERENCES users(id)
	ON DELETE CASCADE,
	CONSTRAINT UNIQUE_owner_id_name UNIQUE(owner_id, name)
);

CREATE TABLE contents (
	id BIGINT AUTO_INCREMENT,
	name VARCHAR(256) NOT NULL,
	description TEXT,
	link TEXT,
	reservator_id BIGINT,
	CONSTRAINT PK_contents PRIMARY KEY(id),
	CONSTRAINT FK_contents_users FOREIGN KEY(reserator_id) REFERENCES users(id)
);

CREATE TABLE wishlists_readers (
	wishlist_id INTEGER NOT NULL,
	reader_id BIGINT NOT NULL,
	CONSTRAINT PK_wishlists_readers PRIMARY KEY(wishlist_id, reader_id),
	CONSTRAINT FK_wishlists_readers_wishlists FOREIGN KEY(wishlist_id) REFERENCES wishlists(id)
	ON DELETE CASCADE,
	CONSTRAINT FK_wishlists_readers_users FOREIGN KEY(reader_id) REFERENCES users(id)
);

CREATE TABLE wishlists_contents (
	wishlist_id INTEGER NOT NULL,
	content_id BIGINT NOT NULL,
	CONSTRAINT PK_wishlists_contents PRIMARY KEY(wishlist_id, content_id),
	CONSTRAINT FK_wishlists_contents_wishlists FOREIGN KEY(wishlist_id) REFERENCES wishlists(id)
	ON DELETE CASCADE,
	CONSTRAINT FK_wishlists_contents_contents FOREIGN KEY(content_id) REFERENCES contents(id)
	ON DELETE CASCADE
);


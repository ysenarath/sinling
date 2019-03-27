--CREATE TABLE `hbc_words` (
 --`WORD_ID` int(10) unsigned NOT NULL DEFAULT '0',
 --`WORD` varchar(100) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL DEFAULT '',
 --`FREQUENCY` int(10) unsigned NOT NULL DEFAULT '0',
 --PRIMARY KEY (`WORD_ID`) USING BTREE,
 --KEY `Words` (`WORD`) USING BTREE
--) ENGINE=InnoDB DEFAULT CHARSET=latin1


CREATE TABLE `hb_exceptions` (
 `lemma_id` int(11) NOT NULL,
 `form_type` smallint(6) NOT NULL,
 `form_sub_type` smallint(6) NOT NULL,
 `word` varchar(100) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
 `user_id` smallint(6) NOT NULL,
 KEY `lemma_id` (`lemma_id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;


CREATE TABLE `hb_lemma` (
 `LEMMA_ID` int(11) NOT NULL AUTO_INCREMENT,
 `LEMMA` varchar(100) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
 `LEMMA_TYPE` tinyint(4) NOT NULL,
 `LEMMA_SUB_TYPE` smallint(6) NOT NULL,
 PRIMARY KEY (`LEMMA_ID`),
 KEY `LEMMA` (`LEMMA`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=latin1;


CREATE TABLE `hb_morph_confirmations` (
 `lemma_id` int(11) NOT NULL,
 `rule_set_id` smallint(6) NOT NULL,
 `user_id` smallint(6) NOT NULL,
 PRIMARY KEY (`lemma_id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

	CREATE TABLE `hb_users` (
 `user_name` varchar(50) NOT NULL,
 `pwd_hash` varchar(50) NOT NULL,
 `user_id` smallint(6) NOT NULL AUTO_INCREMENT,
 `user_role` smallint(6) NOT NULL,
 PRIMARY KEY (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

--truncate table hb_morph_confirmations;
--truncate table hb_exceptions;
--truncate table hb_lemma;
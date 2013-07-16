-- MySQL dump 10.13  Distrib 5.5.31, for debian-linux-gnu (x86_64)
--
-- Host: localhost    Database: forumsdb
-- ------------------------------------------------------
-- Server version	5.5.31-0ubuntu0.12.04.2

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Current Database: `forumsdb`
--

CREATE DATABASE /*!32312 IF NOT EXISTS*/ `forumsdb` /*!40100 DEFAULT CHARACTER SET utf8 COLLATE utf8_unicode_ci */;

USE `forumsdb`;

--
-- Table structure for table `FORUM_POSTS`
--

DROP TABLE IF EXISTS `FORUMS`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `FORUMS` (
  `forum_id` int(11) NOT NULL AUTO_INCREMENT,
  `forum_name` varchar(50) COLLATE utf8_unicode_ci DEFAULT NULL,
  `forum_url` varchar(50) COLLATE utf8_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`forum_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

DROP TABLE IF EXISTS `SUBFORUMS`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;

CREATE TABLE `SUBFORUMS` (
  `subforum_id` int(11) NOT NULL AUTO_INCREMENT,
  `subforum_name` varchar(50) COLLATE utf8_unicode_ci DEFAULT NULL,
  `subforum_url` varchar(50) COLLATE utf8_unicode_ci DEFAULT NULL,
  `forum_id` int(11) REFERENCES FORUMS(forum_id),
  PRIMARY KEY (`subforum_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

DROP TABLE IF EXISTS `THREADS`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;

CREATE TABLE `THREADS` (
  `thread_id` int(11) NOT NULL AUTO_INCREMENT,
  `thread_name` varchar(100) COLLATE utf8_unicode_ci DEFAULT NULL,
  `subforum_id` int(11) REFERENCES SUBFORUMS(subforum_id),
  `subforum_page` varchar(50) COLLATE utf8_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`thread_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

DROP TABLE IF EXISTS `POSTS`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;

CREATE TABLE `POSTS` (
  `post_id` int(11) NOT NULL AUTO_INCREMENT,
  `postdate` varchar(50) COLLATE utf8_unicode_ci DEFAULT NULL,
  `postlink` varchar(50) COLLATE utf8_unicode_ci DEFAULT NULL,
  `msg` varchar(100000) COLLATE utf8_unicode_ci DEFAULT NULL,
  `edits` varchar(1000) COLLATE utf8_unicode_ci DEFAULT NULL,
  `thread_id` int(11) REFERENCES THREADS(thread_id),
  `user_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`post_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;


DROP TABLE IF EXISTS `USERS`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;

/*`userlink` varchar(100) COLLATE utf8_unicode_ci DEFAULT NULL,*/;
CREATE TABLE `USERS` (
  `user_id` int(11) NOT NULL AUTO_INCREMENT,
  `forum_id` int(11) REFERENCES FORUMS(forum_id),
  `username` varchar(50) COLLATE utf8_unicode_ci DEFAULT NULL,
  `usertitle` varchar(50) COLLATE utf8_unicode_ci DEFAULT NULL,
  `joindate` varchar(50) COLLATE utf8_unicode_ci DEFAULT NULL,
  `sig` varchar(10000) COLLATE utf8_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

DROP TABLE IF EXISTS `IMAGES`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;

/*`userlink` varchar(100) COLLATE utf8_unicode_ci DEFAULT NULL,*/;
CREATE TABLE `IMAGES` (
  `image_id` int(11) NOT NULL AUTO_INCREMENT,
  `thread_id` int(11) REFERENCES THREADS(thread_id),
  `user_id` int(11) REFERENCES USERS(user_id),
  `post_id` int(11) REFERENCES POSTS(post_id),
  `image_src` varchar(200) COLLATE utf8_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`image_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;




/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2013-06-11 11:04:36

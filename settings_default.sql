-- phpMyAdmin SQL Dump
-- version 3.3.7deb5
-- http://www.phpmyadmin.net
--
-- Host: localhost
-- Generation Time: Jan 21, 2012 at 06:19 PM
-- Server version: 5.1.49
-- PHP Version: 5.3.3-7+squeeze1

SET SQL_MODE="NO_AUTO_VALUE_ON_ZERO";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;

--
-- Database: `honstatus`
--

--
-- Dumping data for table `settings`
--

INSERT INTO `settings` (`id`, `name`, `key`, `value`) VALUES
(1, 'Account Username', 'username', 'userName'),
(2, 'Account Password', 'password', 'md5password'),
(3, 'Invisible', 'invis', 'True'),
(4, 'HoN Client Version', 'honver', '2.1.10.0'),
(5, 'Chat Port', 'chatport', '11031'),
(6, 'Chat Protocol Version', 'chatver', '21'),
(7, 'Master Server', 'masterserver', 'http://masterserver.hon.s2games.com/'),
(8, 'Basic Server', 'basicserver', 'http://heroesofnewerth.com/');

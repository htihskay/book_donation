-- phpMyAdmin SQL Dump
-- version 5.0.2
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1:3306
-- Generation Time: Jan 22, 2021 at 02:51 AM
-- Server version: 5.7.31
-- PHP Version: 7.3.21

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `book_donation`
--

-- --------------------------------------------------------

--
-- Table structure for table `admin`
--

DROP TABLE IF EXISTS `admin`;
CREATE TABLE IF NOT EXISTS `admin` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `firstName` varchar(125) NOT NULL,
  `lastName` varchar(125) NOT NULL,
  `email` varchar(100) NOT NULL,
  `mobile` varchar(25) NOT NULL,
  `address` text NOT NULL,
  `password` varchar(100) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=latin1;

--
-- Dumping data for table `admin`
--

INSERT INTO `admin` (`id`, `firstName`, `lastName`, `email`, `mobile`, `address`, `password`) VALUES
(7, 'yakshith', 'p', 'yakshith@gmail.com', '1234567890', 'Mangaluru', 'password');

-- --------------------------------------------------------

--
-- Table structure for table `books`
--

DROP TABLE IF EXISTS `books`;
CREATE TABLE IF NOT EXISTS `books` (
  `b_id` int(11) NOT NULL AUTO_INCREMENT,
  `d_id` int(11) NOT NULL,
  `bname` varchar(100) NOT NULL,
  `author` varchar(100) NOT NULL,
  `category` varchar(20) NOT NULL,
  `description` text NOT NULL,
  `picture` text NOT NULL,
  `date` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`b_id`),
  KEY `foreignkeyd_id` (`d_id`)
) ENGINE=InnoDB AUTO_INCREMENT=23 DEFAULT CHARSET=latin1;

--
-- Dumping data for table `books`
--

INSERT INTO `books` (`b_id`, `d_id`, `bname`, `author`, `category`, `description`, `picture`, `date`) VALUES
(15, 2, 'Networking', 'Charles', 'ec', 'Netwoking book', 'umberto-jXd2FSvcRr8-unsplash.jpg', '2021-01-19 07:11:53'),
(16, 1, 'AI', 'Peter', 'cs', 'Artificial Intelligence', 'owen-beard-K21Dn4OVxNw-unsplash.jpg', '2021-01-19 07:44:12'),
(17, 1, 'Python', 'Charles', 'cs', 'Python coding', 'shahadat-rahman-BfrQnKBulYQ-unsplash.jpg', '2021-01-19 07:47:06'),
(18, 2, 'The Art of Electronics', 'Charles', 'ec', 'Electronics', 'frank-wang-ogxlyCA1BQc-unsplash.jpg', '2021-01-19 07:49:53'),
(19, 3, 'Machine Design', 'Guptha', 'me', 'Machine designing', 'mykola-makhlai-etw8edKg0KE-unsplash.jpg', '2021-01-19 15:16:47'),
(20, 3, 'Theory Machines', 'Sando', 'me', 'Book for mech. student', 'mika-baumeister-LXi_v9yr6s4-unsplash.jpg', '2021-01-19 15:19:29'),
(21, 4, 'Dynamic of structures', 'Anil Kumar', 'cv', 'books for the civil students', 'ralph-ravi-kayden-_wcvlHMyXBg-unsplash.jpg', '2021-01-19 15:24:22'),
(22, 4, 'Concrete Technology', 'M.S. Kumar', 'cv', 'About concrete technology', 'ms-sue-huan-0E_pAtaMszk-unsplash.jpg', '2021-01-19 15:28:02');

-- --------------------------------------------------------

--
-- Table structure for table `donors`
--

DROP TABLE IF EXISTS `donors`;
CREATE TABLE IF NOT EXISTS `donors` (
  `d_id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(50) NOT NULL,
  `email` varchar(50) NOT NULL,
  `username` varchar(25) NOT NULL,
  `password` varchar(100) NOT NULL,
  `mobile` varchar(20) NOT NULL,
  `address` varchar(100) NOT NULL,
  PRIMARY KEY (`d_id`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=latin1;

--
-- Dumping data for table `donors`
--

INSERT INTO `donors` (`d_id`, `name`, `email`, `username`, `password`, `mobile`, `address`) VALUES
(1, 'Suhas', 'suhas@gmail.com', 'suhas', '$5$rounds=535000$IrKMjsI66vcW8A/V$GMv5AEqcwjang6ZEH7FX2KiOhFKqmKQDroOvWorJQo5', '12345678910', 'Mangaluru,Karnataka'),
(2, 'varun', 'varun@gmail.com', 'varun', '$5$rounds=535000$bt2dS0XW.quP/Q6u$RQVuy4BdaBUgP2lJVHV3ocwVRq6xk3ILbqrUEIjSS/1', '12345678910', 'Mangaluru,Karnataka'),
(3, 'Mohan', 'mohan@gmail.com', 'mohan', '$5$rounds=535000$PeuJuaeQBxUPcMkj$y77DtpfC8ETLPh1tcDdbC/ML.03LsEEPz8xOewhfk82', '+91 9874563210', 'Vittal,Puttur'),
(4, 'Adithya', 'adithya@gmail.com', 'adithya', '$5$rounds=535000$rQqDF5jnV3P3Yb7H$XueKniljmAvtGiSXDYjqVFZr5ElIhbOeYiuhS2L.uHA', '+91 9874563210', 'Mangaluru,Karnataka');

-- --------------------------------------------------------

--
-- Table structure for table `orders`
--

DROP TABLE IF EXISTS `orders`;
CREATE TABLE IF NOT EXISTS `orders` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `uid` int(11) DEFAULT NULL,
  `ofname` text NOT NULL,
  `pid` int(11) NOT NULL,
  `oplace` text NOT NULL,
  `mobile` varchar(15) NOT NULL,
  `area_pin` varchar(6) NOT NULL,
  `odate` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `foreignkey` (`uid`),
  KEY `ordforeignkey` (`pid`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=latin1;

--
-- Dumping data for table `orders`
--

INSERT INTO `orders` (`id`, `uid`, `ofname`, `pid`, `oplace`, `mobile`, `area_pin`, `odate`) VALUES
(1, 20, 'Yashas', 16, 'Padil,Mangalore', '984756231', '574331', '2021-01-19 14:50:45');

-- --------------------------------------------------------

--
-- Table structure for table `users`
--

DROP TABLE IF EXISTS `users`;
CREATE TABLE IF NOT EXISTS `users` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(50) NOT NULL,
  `email` varchar(50) NOT NULL,
  `username` varchar(25) NOT NULL,
  `password` varchar(100) NOT NULL,
  `mobile` varchar(20) NOT NULL,
  `reg_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `online` varchar(1) NOT NULL DEFAULT '0',
  `activation` varchar(3) NOT NULL DEFAULT 'yes',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=21 DEFAULT CHARSET=latin1;

--
-- Dumping data for table `users`
--

INSERT INTO `users` (`id`, `name`, `email`, `username`, `password`, `mobile`, `reg_time`, `online`, `activation`) VALUES
(20, 'Yashas', 'yashas@gmail.com', 'yashas', '$5$rounds=535000$wPqGHa3YCZkafhqA$BLg1nbNSLHxZZjObfxvHxhD/dYS2J6zsQJ1Gc6Fyul9', '+91 9874563210', '2021-01-19 14:48:07', '0', 'yes');

--
-- Constraints for dumped tables
--

--
-- Constraints for table `orders`
--
ALTER TABLE `orders`
  ADD CONSTRAINT `ordforeignkey` FOREIGN KEY (`pid`) REFERENCES `books` (`b_id`) ON DELETE CASCADE ON UPDATE CASCADE;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;

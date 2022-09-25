-- phpMyAdmin SQL Dump
-- version 4.8.0.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Sep 13, 2020 at 12:27 PM
-- Server version: 10.1.32-MariaDB
-- PHP Version: 7.2.5

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET AUTOCOMMIT = 0;
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `pi`
--

-- --------------------------------------------------------

--
-- Table structure for table `pantaujati`
--

CREATE TABLE `pantaujati` (
  `nodeId` tinyint(2) UNSIGNED NOT NULL,
  `soilMoist` float UNSIGNED NOT NULL,
  `soilStatus` varchar(25) NOT NULL,
  `ketinggian` tinyint(3) UNSIGNED NOT NULL,
  `timeStamp` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Dumping data for table `pantaujati`
--

INSERT INTO `pantaujati` (`nodeId`, `soilMoist`, `soilStatus`, `ketinggian`, `timeStamp`) VALUES
(1, 23.1, 'GOOD', 6, '2020-09-13 07:08:51'),
(2, 21.131, 'GOOD', 8, '2020-09-13 07:08:57'),
(3, 23.1, 'GOOD', 4, '2020-09-13 07:08:51'),
(4, 21.131, 'GOOD', 7, '2020-09-13 07:11:20');

--
-- Indexes for dumped tables
--

--
-- Indexes for table `pantaujati`
--
ALTER TABLE `pantaujati`
  ADD PRIMARY KEY (`nodeId`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;

-- phpMyAdmin SQL Dump
-- version 4.8.0.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Nov 01, 2020 at 09:38 AM
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
-- Table structure for table `parkirpolinema_nodelogging`
--

CREATE TABLE `parkirpolinema_nodelogging` (
  `no` int(10) UNSIGNED NOT NULL,
  `nodeId` tinyint(2) UNSIGNED NOT NULL,
  `meshNodeId` tinyint(2) UNSIGNED DEFAULT NULL,
  `jumlahKendaraan` smallint(5) UNSIGNED NOT NULL,
  `parkirStatus` varchar(128) NOT NULL,
  `timeStamp` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Dumping data for table `parkirpolinema_nodelogging`
--

INSERT INTO `parkirpolinema_nodelogging` (`no`, `nodeId`, `meshNodeId`, `jumlahKendaraan`, `parkirStatus`, `timeStamp`) VALUES
(0, 1, 4, 23, 'Tersedia', '2020-11-01 08:15:19'),
(1, 1, 4, 13, 'Tersedia', '2020-11-01 08:15:22'),
(2, 1, 4, 13, 'Tersedia', '2020-11-01 08:15:25');

--
-- Indexes for dumped tables
--

--
-- Indexes for table `parkirpolinema_nodelogging`
--
ALTER TABLE `parkirpolinema_nodelogging`
  ADD PRIMARY KEY (`no`),
  ADD UNIQUE KEY `no` (`no`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `parkirpolinema_nodelogging`
--
ALTER TABLE `parkirpolinema_nodelogging`
  MODIFY `no` int(10) UNSIGNED NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=4;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;

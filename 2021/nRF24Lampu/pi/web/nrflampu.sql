-- phpMyAdmin SQL Dump
-- version 5.0.2
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Jun 29, 2021 at 08:50 AM
-- Server version: 10.4.13-MariaDB
-- PHP Version: 7.4.7

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
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
-- Table structure for table `nrf24lampu`
--

DROP TABLE IF EXISTS `nrf24lampu`;
CREATE TABLE `nrf24lampu` (
  `id` int(10) UNSIGNED NOT NULL,
  `acVoltage` float NOT NULL,
  `dcVoltage` float NOT NULL,
  `acCurrent` float NOT NULL,
  `dcCurrent` float NOT NULL,
  `timeStamp` timestamp NOT NULL DEFAULT current_timestamp(),
  `meshId` int(10) UNSIGNED NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Dumping data for table `nrf24lampu`
--

INSERT INTO `nrf24lampu` (`id`, `acVoltage`, `dcVoltage`, `acCurrent`, `dcCurrent`, `timeStamp`, `meshId`) VALUES
(1, 231, 11, 11, 0, '2021-06-12 08:36:29', 10),
(2, 229, 22, 22, 0, '2021-06-12 08:36:34', 20),
(3, 221, 33, 33, 0, '2021-06-12 08:36:43', 30);

--
-- Triggers `nrf24lampu`
--
DROP TRIGGER IF EXISTS `nrf24lampu_logging`;
DELIMITER $$
CREATE TRIGGER `nrf24lampu_logging` AFTER UPDATE ON `nrf24lampu` FOR EACH ROW REPLACE INTO nrf24lampulog(id, acVoltage, dcVoltage, acCurrent, dcCurrent, timeStamp, nodeId, meshId)
        VALUES(NULL, new.acVoltage, new.dcVoltage, new.acCurrent, new.dcCurrent, new.timeStamp, new.id, new.meshId)
$$
DELIMITER ;

-- --------------------------------------------------------

--
-- Table structure for table `nrf24lampulog`
--

DROP TABLE IF EXISTS `nrf24lampulog`;
CREATE TABLE `nrf24lampulog` (
  `id` int(10) UNSIGNED NOT NULL,
  `acVoltage` float NOT NULL,
  `dcVoltage` float NOT NULL,
  `acCurrent` float NOT NULL,
  `dcCurrent` float NOT NULL,
  `timeStamp` timestamp NOT NULL DEFAULT current_timestamp(),
  `nodeId` int(10) UNSIGNED NOT NULL,
  `meshId` int(10) UNSIGNED NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Dumping data for table `nrf24lampulog`
--

INSERT INTO `nrf24lampulog` (`id`, `acVoltage`, `dcVoltage`, `acCurrent`, `dcCurrent`, `timeStamp`, `nodeId`, `meshId`) VALUES
(1, 11, 1, 1, 0, '2021-06-12 08:17:22', 1, 10),
(2, 2, 22, 2, 0, '2021-06-12 08:17:40', 2, 20),
(3, 3, 3, 33, 0, '2021-06-12 08:17:44', 3, 30),
(4, 11, 11, 1, 0, '2021-06-12 08:17:48', 1, 10),
(5, 11, 11, 11, 0, '2021-06-12 08:17:51', 1, 10),
(6, 22, 22, 2, 0, '2021-06-12 08:17:54', 2, 20),
(7, 22, 22, 22, 0, '2021-06-12 08:17:57', 2, 20),
(8, 33, 3, 33, 0, '2021-06-12 08:18:00', 3, 30),
(9, 33, 33, 33, 0, '2021-06-12 08:18:05', 3, 30),
(10, 231, 11, 11, 0, '2021-06-12 08:36:29', 1, 10),
(11, 229, 22, 22, 0, '2021-06-12 08:36:34', 2, 20),
(12, 221, 33, 33, 0, '2021-06-12 08:36:43', 3, 30);

--
-- Indexes for dumped tables
--

--
-- Indexes for table `nrf24lampu`
--
ALTER TABLE `nrf24lampu`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `nrf24lampulog`
--
ALTER TABLE `nrf24lampulog`
  ADD PRIMARY KEY (`id`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `nrf24lampulog`
--
ALTER TABLE `nrf24lampulog`
  MODIFY `id` int(10) UNSIGNED NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=13;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;

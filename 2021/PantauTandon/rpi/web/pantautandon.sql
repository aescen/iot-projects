-- phpMyAdmin SQL Dump
-- version 5.0.2
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Jul 17, 2021 at 08:35 AM
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
-- Table structure for table `pantautandon`
--

DROP TABLE IF EXISTS `pantautandon`;
CREATE TABLE `pantautandon` (
  `id` tinyint(3) UNSIGNED NOT NULL,
  `objectType` varchar(16) COLLATE utf8mb4_unicode_ci NOT NULL,
  `valObject` float NOT NULL,
  `timeStamp` timestamp NOT NULL DEFAULT current_timestamp(),
  `nodeId` tinyint(3) UNSIGNED NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Dumping data for table `pantautandon`
--

INSERT INTO `pantautandon` (`id`, `objectType`, `valObject`, `timeStamp`, `nodeId`) VALUES
(1, 'ph', 111, '2021-05-23 01:17:53', 1),
(2, 'conductivity', 222, '2021-05-23 01:18:12', 1),
(3, 'turbidity', 333, '2021-05-23 01:18:03', 1),
(4, 'ultrasonic', 44, '2021-05-23 00:07:23', 1);

--
-- Triggers `pantautandon`
--
DROP TRIGGER IF EXISTS `pantautandon_logging`;
DELIMITER $$
CREATE TRIGGER `pantautandon_logging` AFTER UPDATE ON `pantautandon` FOR EACH ROW REPLACE INTO pantautandonlog(id, objectType, valObject, timeStamp, nodeId)
        VALUES(NULL, new.objectType, new.valObject, CURRENT_TIMESTAMP, new.nodeId)
$$
DELIMITER ;

-- --------------------------------------------------------

--
-- Table structure for table `pantautandonlog`
--

DROP TABLE IF EXISTS `pantautandonlog`;
CREATE TABLE `pantautandonlog` (
  `id` int(11) UNSIGNED NOT NULL,
  `objectType` varchar(16) NOT NULL,
  `valObject` float NOT NULL,
  `timeStamp` timestamp NOT NULL DEFAULT current_timestamp(),
  `nodeId` tinyint(4) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Dumping data for table `pantautandonlog`
--

INSERT INTO `pantautandonlog` (`id`, `objectType`, `valObject`, `timeStamp`, `nodeId`) VALUES
(1, 'ph', 111, '2021-07-17 05:43:58', 1),
(2, 'conductivity', 222, '2021-07-17 05:44:09', 1),
(3, 'turbidity', 333, '2021-07-17 05:44:19', 1),
(4, 'ultrasonic', 44, '2021-07-17 05:44:37', 1);

--
-- Indexes for dumped tables
--

--
-- Indexes for table `pantautandon`
--
ALTER TABLE `pantautandon`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `pantautandonlog`
--
ALTER TABLE `pantautandonlog`
  ADD PRIMARY KEY (`id`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `pantautandonlog`
--
ALTER TABLE `pantautandonlog`
  MODIFY `id` int(11) UNSIGNED NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=6;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;

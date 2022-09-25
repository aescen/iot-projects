-- phpMyAdmin SQL Dump
-- version 5.0.2
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Jul 05, 2021 at 12:49 PM
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
-- Table structure for table `zonabuta`
--

DROP TABLE IF EXISTS `zonabuta`;
CREATE TABLE `zonabuta` (
  `id` int(11) NOT NULL,
  `objectCount` int(11) NOT NULL,
  `objectType` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL CHECK (json_valid(`objectType`)),
  `totalDetection` float NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Dumping data for table `zonabuta`
--

INSERT INTO `zonabuta` (`id`, `objectCount`, `objectType`, `totalDetection`) VALUES
(1, 6, '{\"mobil\": 1, \"sepeda_motor\": 2, \"orang\": 3}', 48);

--
-- Triggers `zonabuta`
--
DROP TRIGGER IF EXISTS `zonabuta_logging`;
DELIMITER $$
CREATE TRIGGER `zonabuta_logging` AFTER UPDATE ON `zonabuta` FOR EACH ROW REPLACE INTO zonabutalog(id, objectCount, objectType, totalDetection, timeStamp)
        VALUES(NULL, new.objectCount, new.objectType, new.totalDetection, CURRENT_TIMESTAMP)
$$
DELIMITER ;

-- --------------------------------------------------------

--
-- Table structure for table `zonabutalog`
--

DROP TABLE IF EXISTS `zonabutalog`;
CREATE TABLE `zonabutalog` (
  `id` int(11) NOT NULL,
  `objectCount` float NOT NULL,
  `objectType` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL CHECK (json_valid(`objectType`)),
  `totalDetection` float NOT NULL,
  `timeStamp` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Dumping data for table `zonabutalog`
--

INSERT INTO `zonabutalog` (`id`, `objectCount`, `objectType`, `totalDetection`, `timeStamp`) VALUES
(1, 6, '{\"mobil\": 1, \"sepeda_motor\": 2, \"orang\": 3}', 16, '2021-07-05 09:55:30'),
(2, 6, '{\"mobil\": 1, \"sepeda_motor\": 2, \"orang\": 3}', 24, '2021-07-05 09:55:49'),
(3, 6, '{\"mobil\": 1, \"sepeda_motor\": 2, \"orang\": 3}', 32, '2021-07-05 09:55:56'),
(4, 6, '{\"mobil\": 1, \"sepeda_motor\": 2, \"orang\": 3}', 48, '2021-07-05 09:56:00');

--
-- Indexes for dumped tables
--

--
-- Indexes for table `zonabuta`
--
ALTER TABLE `zonabuta`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `zonabutalog`
--
ALTER TABLE `zonabutalog`
  ADD PRIMARY KEY (`id`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `zonabutalog`
--
ALTER TABLE `zonabutalog`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=5;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;

-- phpMyAdmin SQL Dump
-- version 5.0.2
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Jul 23, 2021 at 09:01 PM
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
-- Table structure for table `pantausopir`
--

DROP TABLE IF EXISTS `pantausopir`;
CREATE TABLE `pantausopir` (
  `id` int(11) NOT NULL,
  `bpmVal` float NOT NULL,
  `oxyVal` float NOT NULL,
  `isCapturePicture` tinyint(1) NOT NULL,
  `imgPath` varchar(64) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL,
  `nodeId` tinyint(3) UNSIGNED NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Dumping data for table `pantausopir`
--

INSERT INTO `pantausopir` (`id`, `bpmVal`, `oxyVal`, `isCapturePicture`, `imgPath`, `nodeId`) VALUES
(0, 59, 95, 0, '2021-07-13_11.22.02', 0);

--
-- Triggers `pantausopir`
--
DROP TRIGGER IF EXISTS `pantausopir_logging`;
DELIMITER $$
CREATE TRIGGER `pantausopir_logging` AFTER UPDATE ON `pantausopir` FOR EACH ROW REPLACE INTO pantausopirlog(id, bpmVal, oxyVal, isCapturePicture, imgPath, nodeId, timeStamp)
        VALUES(NULL, new.bpmVal, new.oxyVal, new.isCapturePicture, new.imgPath, new.nodeId, CURRENT_TIMESTAMP)
$$
DELIMITER ;

-- --------------------------------------------------------

--
-- Table structure for table `pantausopirlog`
--

DROP TABLE IF EXISTS `pantausopirlog`;
CREATE TABLE `pantausopirlog` (
  `id` int(11) NOT NULL,
  `bpmVal` float NOT NULL,
  `oxyVal` float NOT NULL,
  `isCapturePicture` tinyint(1) NOT NULL,
  `imgPath` varchar(64) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL,
  `nodeId` tinyint(3) UNSIGNED NOT NULL,
  `timeStamp` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Dumping data for table `pantausopirlog`
--

INSERT INTO `pantausopirlog` (`id`, `bpmVal`, `oxyVal`, `isCapturePicture`, `imgPath`, `nodeId`, `timeStamp`) VALUES
(1, 59, 95, 0, '2021-07-13_11.22.00', 0, '2021-07-13 13:10:29'),
(2, 59, 95, 0, '2021-07-13_11.22.01', 0, '2021-07-13 13:10:36');

--
-- Indexes for dumped tables
--

--
-- Indexes for table `pantausopir`
--
ALTER TABLE `pantausopir`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `nodeId` (`nodeId`);

--
-- Indexes for table `pantausopirlog`
--
ALTER TABLE `pantausopirlog`
  ADD PRIMARY KEY (`id`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `pantausopirlog`
--
ALTER TABLE `pantausopirlog`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=6;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;

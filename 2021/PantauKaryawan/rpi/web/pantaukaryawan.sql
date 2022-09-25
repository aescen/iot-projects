-- phpMyAdmin SQL Dump
-- version 5.0.2
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Jul 19, 2021 at 04:46 AM
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
-- Table structure for table `pantaukaryawan`
--

DROP TABLE IF EXISTS `pantaukaryawan`;
CREATE TABLE `pantaukaryawan` (
  `id` int(11) NOT NULL,
  `valBpm` float NOT NULL,
  `valOxy` float NOT NULL,
  `valTemp` float NOT NULL,
  `valLoc` varchar(16) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL,
  `nodeId` tinyint(3) UNSIGNED NOT NULL,
  `timeStamp` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Dumping data for table `pantaukaryawan`
--

INSERT INTO `pantaukaryawan` (`id`, `valBpm`, `valOxy`, `valTemp`, `valLoc`, `nodeId`, `timeStamp`) VALUES
(0, 1, 2, 39, 'Gedung A', 0, '2021-07-19 02:41:37'),
(1, 2, 4, 37, 'Gedung B', 1, '2021-07-19 02:40:42');

--
-- Triggers `pantaukaryawan`
--
DROP TRIGGER IF EXISTS `pantaukaryawan_logging`;
DELIMITER $$
CREATE TRIGGER `pantaukaryawan_logging` AFTER UPDATE ON `pantaukaryawan` FOR EACH ROW REPLACE INTO pantaukaryawanlog(id, valBpm, valOxy, valTemp, valLoc, nodeId, timeStamp)
        VALUES(NULL, new.valBpm, new.valOxy, new.valTemp, new.valLoc, new.nodeId, CURRENT_TIMESTAMP)
$$
DELIMITER ;

-- --------------------------------------------------------

--
-- Table structure for table `pantaukaryawanlog`
--

DROP TABLE IF EXISTS `pantaukaryawanlog`;
CREATE TABLE `pantaukaryawanlog` (
  `id` int(11) NOT NULL,
  `valBpm` float NOT NULL,
  `valOxy` float NOT NULL,
  `valTemp` float NOT NULL,
  `valLoc` varchar(16) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL,
  `nodeId` tinyint(3) UNSIGNED NOT NULL,
  `timeStamp` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Dumping data for table `pantaukaryawanlog`
--

INSERT INTO `pantaukaryawanlog` (`id`, `valBpm`, `valOxy`, `valTemp`, `valLoc`, `nodeId`, `timeStamp`) VALUES
(1, 1, 2, 36, 'Gedung A', 0, '2021-07-19 02:39:06'),
(2, 2, 4, 35.85, 'Gedung B', 1, '2021-07-19 02:40:05'),
(3, 2, 4, 37, 'Gedung B', 1, '2021-07-19 02:40:42'),
(4, 1, 2, 39, 'Gedung A', 0, '2021-07-19 02:41:37');

--
-- Indexes for dumped tables
--

--
-- Indexes for table `pantaukaryawan`
--
ALTER TABLE `pantaukaryawan`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `nodeId` (`nodeId`);

--
-- Indexes for table `pantaukaryawanlog`
--
ALTER TABLE `pantaukaryawanlog`
  ADD PRIMARY KEY (`id`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `pantaukaryawanlog`
--
ALTER TABLE `pantaukaryawanlog`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=5;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;

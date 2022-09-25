-- phpMyAdmin SQL Dump
-- version 5.0.2
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Jul 14, 2021 at 05:12 AM
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
-- Table structure for table `pantausungai`
--

DROP TABLE IF EXISTS `pantausungai`;
CREATE TABLE `pantausungai` (
  `id` int(11) NOT NULL,
  `sensorType` varchar(12) NOT NULL,
  `sensorVal` float NOT NULL,
  `objectStatus` tinyint(3) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Dumping data for table `pantausungai`
--

INSERT INTO `pantausungai` (`id`, `sensorType`, `sensorVal`, `objectStatus`) VALUES
(0, 'turbidity', 11.111, -1);

--
-- Triggers `pantausungai`
--
DROP TRIGGER IF EXISTS `pantausungai_logging`;
DELIMITER $$
CREATE TRIGGER `pantausungai_logging` AFTER UPDATE ON `pantausungai` FOR EACH ROW REPLACE INTO pantausungailog(id, sensorType, sensorVal, objectStatus, timeStamp)
        VALUES(NULL, new.sensorType, new.sensorVal, new.objectStatus, CURRENT_TIMESTAMP)
$$
DELIMITER ;

-- --------------------------------------------------------

--
-- Table structure for table `pantausungailog`
--

DROP TABLE IF EXISTS `pantausungailog`;
CREATE TABLE `pantausungailog` (
  `id` int(11) NOT NULL,
  `sensorType` varchar(12) NOT NULL,
  `sensorVal` float NOT NULL,
  `objectStatus` tinyint(4) NOT NULL,
  `timeStamp` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Dumping data for table `pantausungailog`
--

INSERT INTO `pantausungailog` (`id`, `sensorType`, `sensorVal`, `objectStatus`, `timeStamp`) VALUES
(1, 'turbidity', 11.111, 0, '2021-07-10 10:25:01'),
(2, 'turbidity', 11.111, 0, '2021-07-10 10:26:00'),
(3, 'turbidity', 11.111, 1, '2021-07-10 10:48:42'),
(4, 'turbidity', 11.111, 0, '2021-07-10 10:51:39'),
(5, 'turbidity', 11.111, 0, '2021-07-10 10:56:08'),
(6, 'turbidity', 11.111, -1, '2021-07-10 10:56:16');

--
-- Indexes for dumped tables
--

--
-- Indexes for table `pantausungai`
--
ALTER TABLE `pantausungai`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `pantausungailog`
--
ALTER TABLE `pantausungailog`
  ADD PRIMARY KEY (`id`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `pantausungailog`
--
ALTER TABLE `pantausungailog`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=7;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;

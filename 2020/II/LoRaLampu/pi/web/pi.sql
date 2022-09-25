-- phpMyAdmin SQL Dump
-- version 4.8.0.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Jun 19, 2020 at 09:37 AM
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
-- Table structure for table `loralampu`
--

CREATE TABLE `loralampu` (
  `no` int(1) UNSIGNED NOT NULL,
  `id` varchar(5) NOT NULL,
  `current` float NOT NULL,
  `voltage` float NOT NULL,
  `timestamp` datetime NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Dumping data for table `loralampu`
--

INSERT INTO `loralampu` (`no`, `id`, `current`, `voltage`, `timestamp`) VALUES
(1, 'A0', 25.124, 12.4, '2020-06-15 16:24:09'),
(2, 'A1', 23.124, 11.8, '2020-06-15 16:32:09'),
(3, 'A2', 27.254, 12.9, '2020-06-15 16:12:12'),
(4, 'A3', 22.812, 11.3, '2020-06-15 16:01:03');

--
-- Triggers `loralampu`
--
DELIMITER $$
CREATE TRIGGER `loralampu_logging` AFTER UPDATE ON `loralampu` FOR EACH ROW INSERT INTO loralampulog(no, id, current, voltage, timestamp)
        VALUES(NULL, new.id, new.current, new.voltage, new.timestamp)
$$
DELIMITER ;

-- --------------------------------------------------------

--
-- Table structure for table `loralampulog`
--

CREATE TABLE `loralampulog` (
  `no` int(1) UNSIGNED NOT NULL,
  `id` varchar(5) NOT NULL,
  `current` float NOT NULL,
  `voltage` float NOT NULL,
  `timestamp` datetime NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Dumping data for table `loralampulog`
--

INSERT INTO `loralampulog` (`no`, `id`, `current`, `voltage`, `timestamp`) VALUES
(1, 'A0', 25.823, 0, '2020-05-31 14:10:13'),
(2, 'A1', 23.216, 0, '2020-05-31 13:44:27'),
(3, 'A2', 17.024, 0, '2020-05-31 13:45:44'),
(4, 'A3', 13.459, 0, '2020-05-31 13:46:08'),
(6, 'A0', 25.124, 12.4, '2020-06-15 16:24:09'),
(7, 'A1', 23.124, 11.8, '2020-06-15 16:32:09'),
(8, 'A2', 27.254, 12.9, '2020-06-15 16:12:12'),
(9, 'A3', 22.812, 11.3, '2020-06-15 16:01:03');

--
-- Indexes for dumped tables
--

--
-- Indexes for table `loralampu`
--
ALTER TABLE `loralampu`
  ADD PRIMARY KEY (`no`),
  ADD UNIQUE KEY `id` (`id`);

--
-- Indexes for table `loralampulog`
--
ALTER TABLE `loralampulog`
  ADD PRIMARY KEY (`no`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `loralampu`
--
ALTER TABLE `loralampu`
  MODIFY `no` int(1) UNSIGNED NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=5;

--
-- AUTO_INCREMENT for table `loralampulog`
--
ALTER TABLE `loralampulog`
  MODIFY `no` int(1) UNSIGNED NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=10;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;

-- phpMyAdmin SQL Dump
-- version 4.8.0.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Jul 15, 2020 at 08:01 AM
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
-- Table structure for table `loratrain`
--

CREATE TABLE `loratrain` (
  `id` int(10) UNSIGNED NOT NULL,
  `traincount` varchar(3) DEFAULT NULL,
  `directionlamp` varchar(9) DEFAULT NULL,
  `stopgolamp` varchar(4) DEFAULT NULL,
  `timestamps` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Dumping data for table `loratrain`
--

INSERT INTO `loratrain` (`id`, `traincount`, `directionlamp`, `stopgolamp`, `timestamps`) VALUES
(1, '2', 'FromRight', 'Stop', '2020-07-13 21:00:00');

--
-- Triggers `loratrain`
--
DELIMITER $$
CREATE TRIGGER `loratrain_logging` AFTER UPDATE ON `loratrain` FOR EACH ROW INSERT INTO loratrainlog(id, traincount, directionlamp, stopgolamp, timestamps)
        VALUES(NULL, new.traincount, new.directionlamp, new.stopgolamp, new.timestamps)
$$
DELIMITER ;

-- --------------------------------------------------------

--
-- Table structure for table `loratrainlog`
--

CREATE TABLE `loratrainlog` (
  `id` int(10) UNSIGNED NOT NULL,
  `traincount` varchar(3) DEFAULT NULL,
  `directionlamp` varchar(9) DEFAULT NULL,
  `stopgolamp` varchar(4) DEFAULT NULL,
  `timestamps` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Dumping data for table `loratrainlog`
--

INSERT INTO `loratrainlog` (`id`, `traincount`, `directionlamp`, `stopgolamp`, `timestamps`) VALUES
(1, '1', 'FromLeft', 'Stop', '2020-07-13 19:00:00'),
(3, '2', 'FromRight', 'Stop', '2020-07-13 21:00:00'),
(4, '2', 'FromRight', 'Stop', '2020-07-13 21:00:00');

--
-- Indexes for dumped tables
--

--
-- Indexes for table `loratrain`
--
ALTER TABLE `loratrain`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `loratrainlog`
--
ALTER TABLE `loratrainlog`
  ADD PRIMARY KEY (`id`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `loratrainlog`
--
ALTER TABLE `loratrainlog`
  MODIFY `id` int(10) UNSIGNED NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=5;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;

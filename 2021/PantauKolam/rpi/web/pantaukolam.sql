-- phpMyAdmin SQL Dump
-- version 5.0.2
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Jul 14, 2021 at 08:15 AM
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
-- Table structure for table `pantaukolam_kolam`
--

DROP TABLE IF EXISTS `pantaukolam_kolam`;
CREATE TABLE `pantaukolam_kolam` (
  `id` int(10) UNSIGNED NOT NULL,
  `valPhB` float NOT NULL,
  `valTurbidity` float NOT NULL,
  `timeStamp` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Dumping data for table `pantaukolam_kolam`
--

INSERT INTO `pantaukolam_kolam` (`id`, `valPhB`, `valTurbidity`, `timeStamp`) VALUES
(0, 6.93, 96.3, '2021-07-14 05:51:22');

--
-- Triggers `pantaukolam_kolam`
--
DROP TRIGGER IF EXISTS `pantaukolam_kolam_logging`;
DELIMITER $$
CREATE TRIGGER `pantaukolam_kolam_logging` AFTER UPDATE ON `pantaukolam_kolam` FOR EACH ROW REPLACE INTO pantaukolam_kolamlog(id, valPhB, valTurbidity, timeStamp)
        VALUES(NULL, new.valPhB, new.valTurbidity, CURRENT_TIMESTAMP)
$$
DELIMITER ;

-- --------------------------------------------------------

--
-- Table structure for table `pantaukolam_kolamlog`
--

DROP TABLE IF EXISTS `pantaukolam_kolamlog`;
CREATE TABLE `pantaukolam_kolamlog` (
  `id` int(10) UNSIGNED NOT NULL,
  `valPhB` float NOT NULL,
  `valTurbidity` float NOT NULL,
  `timeStamp` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Dumping data for table `pantaukolam_kolamlog`
--

INSERT INTO `pantaukolam_kolamlog` (`id`, `valPhB`, `valTurbidity`, `timeStamp`) VALUES
(0, 6.93, 96.3, '2021-07-14 05:51:41');

-- --------------------------------------------------------

--
-- Table structure for table `pantaukolam_turbin`
--

DROP TABLE IF EXISTS `pantaukolam_turbin`;
CREATE TABLE `pantaukolam_turbin` (
  `id` int(10) UNSIGNED NOT NULL,
  `valRpm` float NOT NULL,
  `valDaya` float NOT NULL,
  `valDebitA` float NOT NULL,
  `valDebitB` float NOT NULL,
  `valPhA` float NOT NULL,
  `timeStamp` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Dumping data for table `pantaukolam_turbin`
--

INSERT INTO `pantaukolam_turbin` (`id`, `valRpm`, `valDaya`, `valDebitA`, `valDebitB`, `valPhA`, `timeStamp`) VALUES
(0, 963, 9.99, 693, 396, 6.93, '2021-07-14 05:50:41');

--
-- Triggers `pantaukolam_turbin`
--
DROP TRIGGER IF EXISTS `pantaukolam_turbin_logging`;
DELIMITER $$
CREATE TRIGGER `pantaukolam_turbin_logging` AFTER UPDATE ON `pantaukolam_turbin` FOR EACH ROW REPLACE INTO pantaukolam_turbinlog(id, valRpm, valDaya, valDebitA, valDebitB, valPhA, timeStamp)
        VALUES(NULL, new.valRpm, new.valDaya, new.valDebitA, new.valDebitB, new.valPhA, CURRENT_TIMESTAMP)
$$
DELIMITER ;

-- --------------------------------------------------------

--
-- Table structure for table `pantaukolam_turbinlog`
--

DROP TABLE IF EXISTS `pantaukolam_turbinlog`;
CREATE TABLE `pantaukolam_turbinlog` (
  `id` int(10) UNSIGNED NOT NULL,
  `valRpm` float NOT NULL,
  `valDaya` float NOT NULL,
  `valDebitA` float NOT NULL,
  `valDebitB` float NOT NULL,
  `valPhA` float NOT NULL,
  `timeStamp` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Dumping data for table `pantaukolam_turbinlog`
--

INSERT INTO `pantaukolam_turbinlog` (`id`, `valRpm`, `valDaya`, `valDebitA`, `valDebitB`, `valPhA`, `timeStamp`) VALUES
(0, 963, 9.99, 693, 396, 6.93, '2021-07-14 05:49:04');

--
-- Indexes for dumped tables
--

--
-- Indexes for table `pantaukolam_kolam`
--
ALTER TABLE `pantaukolam_kolam`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `pantaukolam_kolamlog`
--
ALTER TABLE `pantaukolam_kolamlog`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `pantaukolam_turbin`
--
ALTER TABLE `pantaukolam_turbin`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `pantaukolam_turbinlog`
--
ALTER TABLE `pantaukolam_turbinlog`
  ADD PRIMARY KEY (`id`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `pantaukolam_kolam`
--
ALTER TABLE `pantaukolam_kolam`
  MODIFY `id` int(10) UNSIGNED NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;

--
-- AUTO_INCREMENT for table `pantaukolam_kolamlog`
--
ALTER TABLE `pantaukolam_kolamlog`
  MODIFY `id` int(10) UNSIGNED NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- AUTO_INCREMENT for table `pantaukolam_turbinlog`
--
ALTER TABLE `pantaukolam_turbinlog`
  MODIFY `id` int(10) UNSIGNED NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;

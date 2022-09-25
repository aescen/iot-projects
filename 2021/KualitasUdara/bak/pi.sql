-- phpMyAdmin SQL Dump
-- version 4.6.6deb5
-- https://www.phpmyadmin.net/
--
-- Host: localhost:3306
-- Generation Time: May 26, 2021 at 07:50 PM
-- Server version: 10.3.27-MariaDB-0+deb10u1
-- PHP Version: 7.3.27-1~deb10u1

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
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
-- Table structure for table `kualitasudara`
--

DROP TABLE IF EXISTS `kualitasudara`;
CREATE TABLE `kualitasudara` (
  `id` tinyint(3) UNSIGNED NOT NULL,
  `ppm1` float NOT NULL,
  `ppm2` float NOT NULL,
  `ppm3` float NOT NULL,
  `dust` float NOT NULL,
  `jumlah` int(4) UNSIGNED NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Dumping data for table `kualitasudara`
--

INSERT INTO `kualitasudara` (`id`, `ppm1`, `ppm2`, `ppm3`, `dust`, `jumlah`) VALUES
(1, 45.5867, 39.7862, 39.7862, 39.2924, 0);

--
-- Triggers `kualitasudara`
--
DROP TRIGGER IF EXISTS `kualitasudara_logging`;
DELIMITER $$
CREATE TRIGGER `kualitasudara_logging` AFTER UPDATE ON `kualitasudara` FOR EACH ROW REPLACE INTO kualitasudaralog(id, ppm1, ppm2, ppm3, dust, jumlah, timestamp)
        VALUES(NULL, new.ppm1, new.ppm2, new.ppm3, new.dust, new.jumlah, CURRENT_TIMESTAMP)
$$
DELIMITER ;

-- --------------------------------------------------------

--
-- Table structure for table `kualitasudaralog`
--

DROP TABLE IF EXISTS `kualitasudaralog`;
CREATE TABLE `kualitasudaralog` (
  `id` int(9) UNSIGNED NOT NULL,
  `ppm1` float NOT NULL,
  `ppm2` float NOT NULL,
  `ppm3` float NOT NULL,
  `dust` float NOT NULL,
  `jumlah` int(4) UNSIGNED NOT NULL,
  `timestamp` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Dumping data for table `kualitasudaralog`
--

INSERT INTO `kualitasudaralog` (`id`, `ppm1`, `ppm2`, `ppm3`, `dust`, `jumlah`, `timestamp`) VALUES
(1, 24.1121, 66.7193, 84.7477, 24.4438, 0, '2021-05-22 14:17:16'),
(2, 3.57286, 66.7193, 84.7477, 5.95824, 0, '2021-05-22 14:17:21'),
(3, 2.29637, 66.7193, 84.7477, 3.88242, 0, '2021-05-22 14:17:26'),
(4, 15.0309, 66.7193, 84.7477, 13.3433, 0, '2021-05-22 14:17:31'),
(5, 43.9352, 66.7193, 84.7477, 37.1351, 0, '2021-05-22 14:17:36'),
(6, 31.2529, 66.7193, 84.7477, 29.8608, 0, '2021-05-22 14:17:41'),
(7, 13.2356, 66.7193, 84.7477, 15.7448, 0, '2021-05-22 14:17:46'),
(8, 2.33731, 66.7193, 84.7477, 4.31568, 0, '2021-05-22 14:17:51'),
(9, 4.04212, 66.7193, 84.7477, 4.95061, 0, '2021-05-22 14:17:56'),
(10, 15.1483, 66.7193, 84.7477, 13.6701, 0, '2021-05-22 14:18:01'),
(11, 46.1494, 66.7193, 84.7477, 38.5617, 0, '2021-05-22 14:18:06'),
(12, 45.5867, 66.7193, 84.7477, 39.2924, 0, '2021-05-22 14:18:11'),
(13, 45.5867, 19.675, 12.2916, 39.2924, 0, '2021-05-22 14:18:25'),
(14, 45.5867, 5.19302, 6.43164, 39.2924, 0, '2021-05-22 14:18:30'),
(15, 45.5867, 48.4632, 45.5867, 39.2924, 0, '2021-05-22 15:07:14'),
(16, 45.5867, 48.1683, 46.4331, 39.2924, 0, '2021-05-22 15:07:18'),
(17, 45.5867, 26.6865, 28.5192, 39.2924, 0, '2021-05-22 15:07:23'),
(18, 45.5867, 12.088, 13.8908, 39.2924, 0, '2021-05-22 15:07:28'),
(19, 45.5867, 13.1284, 14.3396, 39.2924, 0, '2021-05-22 15:07:33'),
(20, 45.5867, 38.081, 35.0795, 39.2924, 0, '2021-05-22 15:07:38'),
(21, 45.5867, 48.7596, 45.8673, 39.2924, 0, '2021-05-22 15:07:43'),
(22, 45.5867, 49.3575, 46.7183, 39.2924, 0, '2021-05-22 15:07:48'),
(23, 45.5867, 39.7862, 39.7862, 39.2924, 0, '2021-05-22 15:07:53');

--
-- Indexes for dumped tables
--

--
-- Indexes for table `kualitasudara`
--
ALTER TABLE `kualitasudara`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `kualitasudaralog`
--
ALTER TABLE `kualitasudaralog`
  ADD PRIMARY KEY (`id`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `kualitasudaralog`
--
ALTER TABLE `kualitasudaralog`
  MODIFY `id` int(9) UNSIGNED NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=24;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;

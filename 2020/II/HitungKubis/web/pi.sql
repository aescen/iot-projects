-- phpMyAdmin SQL Dump
-- version 4.8.0.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Jun 19, 2020 at 12:29 PM
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
-- Table structure for table `kubis`
--

CREATE TABLE `kubis` (
  `id` int(9) UNSIGNED NOT NULL,
  `warna` varchar(16) NOT NULL,
  `kualitas` varchar(16) NOT NULL,
  `jumlah` int(9) NOT NULL,
  `kloter` varchar(50) NOT NULL,
  `r` varchar(7) NOT NULL,
  `g` varchar(7) NOT NULL,
  `b` varchar(7) NOT NULL,
  `timestamp` datetime NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Dumping data for table `kubis`
--

INSERT INTO `kubis` (`id`, `warna`, `kualitas`, `jumlah`, `kloter`, `r`, `g`, `b`, `timestamp`) VALUES
(1, 'Hijau', 'Baik', 0, 'KUBIS A', '0', '0', '0', '2020-06-19 17:21:36'),
(2, 'Cokelat', 'Buruk', 0, 'KUBIS A', '0', '0', '0', '2020-06-19 17:21:36');

--
-- Triggers `kubis`
--
DELIMITER $$
CREATE TRIGGER `kubis_log` AFTER UPDATE ON `kubis` FOR EACH ROW INSERT INTO kubislog(id, warna, kualitas, jumlah, kloter, r, g, b, timestamp)
        VALUES(NULL, new.warna, new.kualitas, new.jumlah, new.kloter, new.r, new.g, new.b, new.timestamp)
$$
DELIMITER ;

-- --------------------------------------------------------

--
-- Table structure for table `kubislog`
--

CREATE TABLE `kubislog` (
  `id` int(9) UNSIGNED NOT NULL,
  `warna` varchar(16) NOT NULL,
  `kualitas` varchar(16) NOT NULL,
  `jumlah` int(9) NOT NULL,
  `kloter` varchar(50) NOT NULL,
  `r` varchar(7) NOT NULL,
  `g` varchar(7) NOT NULL,
  `b` varchar(7) NOT NULL,
  `timestamp` datetime NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Dumping data for table `kubislog`
--

INSERT INTO `kubislog` (`id`, `warna`, `kualitas`, `jumlah`, `kloter`, `r`, `g`, `b`, `timestamp`) VALUES
(1, 'Cokelat', 'Buruk', 2, '-', '211.62', '221', '126.22', '2020-06-14 16:25:32'),
(2, 'Hijau', 'Baik', 1, '-', '148.62', '255', '148.22', '2020-06-14 16:25:23'),
(3, 'Hijau', 'Baik', 1, '-', '148.62', '255', '148.22', '2020-06-15 20:11:35'),
(4, 'Cokelat', 'Buruk', 2, '-', '128.62', '221', '126.22', '2020-06-15 20:11:35');

--
-- Indexes for dumped tables
--

--
-- Indexes for table `kubis`
--
ALTER TABLE `kubis`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `warna` (`warna`),
  ADD UNIQUE KEY `kualitas` (`kualitas`);

--
-- Indexes for table `kubislog`
--
ALTER TABLE `kubislog`
  ADD PRIMARY KEY (`id`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `kubis`
--
ALTER TABLE `kubis`
  MODIFY `id` int(9) UNSIGNED NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;

--
-- AUTO_INCREMENT for table `kubislog`
--
ALTER TABLE `kubislog`
  MODIFY `id` int(9) UNSIGNED NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=60;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;

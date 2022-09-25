-- phpMyAdmin SQL Dump
-- version 5.0.2
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Aug 01, 2022 at 03:55 PM
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
CREATE DATABASE IF NOT EXISTS `pi` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;
USE `pi`;

-- --------------------------------------------------------

--
-- Table structure for table `pantauternak`
--

CREATE TABLE `pantauternak` (
  `id` int(10) UNSIGNED NOT NULL,
  `tipe` varchar(16) NOT NULL,
  `berat` int(4) UNSIGNED NOT NULL,
  `Harga` int(10) UNSIGNED NOT NULL,
  `suhu` tinyint(2) NOT NULL,
  `keterangan` varchar(16) NOT NULL,
  `time_stamp` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  `img_path` text NOT NULL,
  `img_cert` varchar(48) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Dumping data for table `pantauternak`
--

INSERT INTO `pantauternak` (`id`, `tipe`, `berat`, `Harga`, `suhu`, `keterangan`, `time_stamp`, `img_path`, `img_cert`) VALUES
(0, 'Kambing', 40, 2150000, 36, 'sehat', '2022-08-01 13:27:42', 'Kambing.jpg', '2022-07-08_12.33.15.png'),
(1, 'Kambing', 60, 2800000, 36, 'Sehat', '2022-08-01 13:27:42', 'Kambing2.jpg\r\n', '2022-07-08_12.33.15.png'),
(2, 'Kambing', 40, 3200000, 36, 'Sehat', '2022-08-01 13:27:42', 'Kambing3.jpg', '2022-07-08_12.33.15.png'),
(3, 'Kambing', 59, 2200000, 36, 'Sehat', '2022-08-01 13:27:42', 'Kambing4.jpg', '2022-07-08_12.33.15.png');

--
-- Triggers `pantauternak`
--
DELIMITER $$
CREATE TRIGGER `pantauternak_logging` AFTER UPDATE ON `pantauternak` FOR EACH ROW REPLACE INTO pantauternak_log(id, tipe, berat, suhu, keterangan, time_stamp, img_path, img_cert)
        VALUES(NULL, new.tipe, new.berat, new.suhu, new.keterangan, CURRENT_TIMESTAMP, new.img_path, new.img_cert)
$$
DELIMITER ;

-- --------------------------------------------------------

--
-- Table structure for table `pantauternak_log`
--

CREATE TABLE `pantauternak_log` (
  `id` int(10) UNSIGNED NOT NULL,
  `tipe` varchar(16) NOT NULL,
  `berat` int(4) UNSIGNED NOT NULL,
  `suhu` tinyint(2) NOT NULL,
  `keterangan` varchar(16) NOT NULL,
  `time_stamp` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  `img_path` text NOT NULL,
  `img_cert` varchar(48) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Dumping data for table `pantauternak_log`
--

INSERT INTO `pantauternak_log` (`id`, `tipe`, `berat`, `suhu`, `keterangan`, `time_stamp`, `img_path`, `img_cert`) VALUES
(1, 'Kambing', 50, 36, 'sehat', '2022-08-01 13:26:59', '2022-07-08_12.33.15.png', '2022-07-08_12.33.15.png'),
(2, 'Kambing', 60, 36, 'Sehat', '2022-08-01 13:27:03', '2022-07-08_12.33.15.png\r\n', '2022-07-08_12.33.15.png'),
(3, 'Kambing', 40, 36, 'Sehat', '2022-08-01 13:27:24', '2022-07-08_12.33.15.png\r\n', '2022-07-08_12.33.15.png'),
(4, 'Kambing', 59, 36, 'Sehat', '2022-08-01 13:27:24', '2022-07-08_12.33.15.png', '2022-07-08_12.33.15.png'),
(5, 'Kambing', 50, 36, 'sehat', '2022-08-01 13:27:24', '2022-07-08_12.33.15.png', '2022-07-08_12.33.15.png'),
(6, 'Kambing', 60, 36, 'Sehat', '2022-08-01 13:27:24', '2022-07-08_12.33.15.png\r\n', '2022-07-08_12.33.15.png'),
(7, 'Kambing', 40, 36, 'Sehat', '2022-08-01 13:27:24', '2022-07-08_12.33.15.png\r\n', '2022-07-08_12.33.15.png'),
(8, 'Kambing', 59, 36, 'Sehat', '2022-08-01 13:27:24', '2022-07-08_12.33.15.png', '2022-07-08_12.33.15.png'),
(9, 'Kambing', 50, 36, 'sehat', '2022-08-01 13:27:24', 'Kambing1.jpg', '2022-07-08_12.33.15.png'),
(10, 'Kambing', 60, 36, 'Sehat', '2022-08-01 13:27:24', 'Kambing2.jpg\r\n', '2022-07-08_12.33.15.png'),
(11, 'Kambing', 40, 36, 'Sehat', '2022-08-01 13:27:24', 'Kambing3.jpg', '2022-07-08_12.33.15.png'),
(12, 'Kambing', 59, 36, 'Sehat', '2022-08-01 13:27:24', 'Kambing4.jpg', '2022-07-08_12.33.15.png'),
(13, 'Kambing', 40, 36, 'sehat', '2022-08-01 13:27:24', 'Kambing.jpg', '2022-07-08_12.33.15.png'),
(14, 'Kambing', 40, 36, 'sehat', '2022-08-01 13:27:42', 'Kambing.jpg', '2022-07-08_12.33.15.png'),
(15, 'Kambing', 60, 36, 'Sehat', '2022-08-01 13:27:42', 'Kambing2.jpg\r\n', '2022-07-08_12.33.15.png'),
(16, 'Kambing', 40, 36, 'Sehat', '2022-08-01 13:27:42', 'Kambing3.jpg', '2022-07-08_12.33.15.png'),
(17, 'Kambing', 59, 36, 'Sehat', '2022-08-01 13:27:42', 'Kambing4.jpg', '2022-07-08_12.33.15.png');

-- --------------------------------------------------------

--
-- Table structure for table `pantauternak_users`
--

CREATE TABLE `pantauternak_users` (
  `id` int(10) UNSIGNED NOT NULL,
  `email` varchar(48) NOT NULL,
  `username` varchar(48) NOT NULL,
  `password` text NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Dumping data for table `pantauternak_users`
--

INSERT INTO `pantauternak_users` (`id`, `email`, `username`, `password`) VALUES
(1, 'ashad@gmail.com', 'ashad', '$2y$10$qlQOEibnlotJ7xKOfQPYoOQhBL3RViqimJlqepyCKXxYd29IA3o7m'),
(5, 'qwerty@gmail.com', 'qwerty', '$2y$10$hMijyke.pNxRRgNpP9mF3eew.G08shvHzadpIk6f9SVJ04duADo2m');

--
-- Indexes for dumped tables
--

--
-- Indexes for table `pantauternak`
--
ALTER TABLE `pantauternak`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `pantauternak_log`
--
ALTER TABLE `pantauternak_log`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `pantauternak_users`
--
ALTER TABLE `pantauternak_users`
  ADD PRIMARY KEY (`id`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `pantauternak_log`
--
ALTER TABLE `pantauternak_log`
  MODIFY `id` int(10) UNSIGNED NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=18;

--
-- AUTO_INCREMENT for table `pantauternak_users`
--
ALTER TABLE `pantauternak_users`
  MODIFY `id` int(10) UNSIGNED NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=6;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;

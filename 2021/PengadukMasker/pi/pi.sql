-- phpMyAdmin SQL Dump
-- version 5.0.2
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Feb 26, 2022 at 06:21 AM
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
-- Table structure for table `pengadukmasker`
--

CREATE TABLE `pengadukmasker` (
  `id` int(11) NOT NULL,
  `nama` varchar(11) NOT NULL,
  `status` int(11) NOT NULL,
  `total` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Dumping data for table `pengadukmasker`
--

INSERT INTO `pengadukmasker` (`id`, `nama`, `status`, `total`) VALUES
(1, 'Mixer 1', 1, 11),
(2, 'Mixer 2', 2, 22),
(3, 'Mixer 3', 3, 33);

--
-- Triggers `pengadukmasker`
--
DELIMITER $$
CREATE TRIGGER `pengadukmasker_logging` AFTER UPDATE ON `pengadukmasker` FOR EACH ROW REPLACE INTO pengadukmaskerlog(id, nama, status, total, waktu)
        VALUES(NULL, new.nama, new.status, new.total, CURRENT_TIMESTAMP)
$$
DELIMITER ;

-- --------------------------------------------------------

--
-- Table structure for table `pengadukmaskerlog`
--

CREATE TABLE `pengadukmaskerlog` (
  `id` int(11) NOT NULL,
  `nama` varchar(16) NOT NULL,
  `status` int(11) NOT NULL,
  `total` int(11) NOT NULL,
  `waktu` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Dumping data for table `pengadukmaskerlog`
--

INSERT INTO `pengadukmaskerlog` (`id`, `nama`, `status`, `total`, `waktu`) VALUES
(1, 'Mixer 1', 11, 11, '2021-06-19 07:40:39'),
(2, 'Mixer 2', 22, 22, '2021-06-19 07:40:39'),
(3, 'Mixer 3', 33, 33, '2021-06-19 07:40:39'),
(4, 'Mixer 1', 1, 11, '2021-06-19 08:55:51'),
(5, 'Mixer 2', 2, 22, '2021-06-19 08:55:51'),
(6, 'Mixer 3', 3, 33, '2021-06-19 08:55:51'),
(7, 'Mixer 1', 3, 11, '2021-06-19 09:00:43'),
(8, 'Mixer 3', 1, 33, '2021-06-19 09:00:43'),
(9, 'Mixer 1', 1, 11, '2021-06-19 09:01:08'),
(10, 'Mixer 3', 3, 33, '2021-06-19 09:01:08');

--
-- Indexes for dumped tables
--

--
-- Indexes for table `pengadukmasker`
--
ALTER TABLE `pengadukmasker`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `nama` (`nama`);

--
-- Indexes for table `pengadukmaskerlog`
--
ALTER TABLE `pengadukmaskerlog`
  ADD PRIMARY KEY (`id`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `pengadukmaskerlog`
--
ALTER TABLE `pengadukmaskerlog`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=11;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;

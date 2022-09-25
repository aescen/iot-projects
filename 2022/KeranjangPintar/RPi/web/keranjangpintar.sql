-- phpMyAdmin SQL Dump
-- version 5.0.2
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Jul 26, 2022 at 06:56 PM
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
-- Table structure for table `keranjang_history`
--

CREATE TABLE `keranjang_history` (
  `id` int(10) UNSIGNED NOT NULL,
  `id_keranjang` int(10) UNSIGNED NOT NULL,
  `id_produk` varchar(32) NOT NULL,
  `id_user` int(10) UNSIGNED NOT NULL,
  `jumlah` int(10) UNSIGNED NOT NULL,
  `time_stamp` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Dumping data for table `keranjang_history`
--

INSERT INTO `keranjang_history` (`id`, `id_keranjang`, `id_produk`, `id_user`, `jumlah`, `time_stamp`) VALUES
(1, 1, '211_162_175_93_131', 1, 3, '2022-07-23 09:58:52'),
(2, 1, '211_114_175_93_83', 1, 2, '2022-07-23 09:58:52'),
(4, 1, '19_134_175_93_103', 1, 4, '2022-07-23 14:56:53'),
(5, 2, '195_120_175_93_73', 1, 6, '2022-07-23 14:57:08');

-- --------------------------------------------------------

--
-- Table structure for table `keranjang_keranjang`
--

CREATE TABLE `keranjang_keranjang` (
  `id` int(10) UNSIGNED NOT NULL,
  `keranjang` varchar(32) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Dumping data for table `keranjang_keranjang`
--

INSERT INTO `keranjang_keranjang` (`id`, `keranjang`) VALUES
(1, '111_000_000_000_111'),
(2, '222_000_000_000_222');

-- --------------------------------------------------------

--
-- Table structure for table `keranjang_pos`
--

CREATE TABLE `keranjang_pos` (
  `id` int(10) UNSIGNED NOT NULL,
  `id_keranjang` int(10) UNSIGNED NOT NULL,
  `id_user` int(10) UNSIGNED NOT NULL,
  `id_produk` varchar(32) NOT NULL,
  `jumlah` int(10) UNSIGNED NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Dumping data for table `keranjang_pos`
--

INSERT INTO `keranjang_pos` (`id`, `id_keranjang`, `id_user`, `id_produk`, `jumlah`) VALUES
(3, 1, 1, '211_162_175_93_131', 2),
(4, 1, 1, '211_114_175_93_83', 3);

-- --------------------------------------------------------

--
-- Table structure for table `keranjang_produk`
--

CREATE TABLE `keranjang_produk` (
  `id` varchar(32) NOT NULL,
  `nama` varchar(32) NOT NULL,
  `deskripsi` text NOT NULL,
  `harga` int(10) UNSIGNED NOT NULL,
  `sisa` int(10) UNSIGNED NOT NULL,
  `img_url` varchar(128) NOT NULL DEFAULT 'https://placekitten.com/360/360'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Dumping data for table `keranjang_produk`
--

INSERT INTO `keranjang_produk` (`id`, `nama`, `deskripsi`, `harga`, `sisa`, `img_url`) VALUES
('195_120_175_93_73', 'Produk 3', 'Produk 3', 300000, 33, 'https://placekitten.com/360/360'),
('195_132_175_93_181', 'Produk 7', 'Produk 7', 770000, 77, 'https://placekitten.com/360/360'),
('195_138_175_93_187', 'Produk 9', 'Produk 9', 990000, 99, 'https://placekitten.com/360/360'),
('195_168_175_93_153', 'Produk 6', 'Produk 6', 660000, 66, 'https://placekitten.com/360/360'),
('195_174_175_93_159', 'Produk 4', 'Produk 4', 440000, 44, 'https://placekitten.com/360/360'),
('195_180_175_93_133', 'Produk 1', 'Produk 1', 110000, 11, 'https://placekitten.com/360/360'),
('19_134_175_93_103', 'Produk 5', 'Produk 5', 550000, 55, 'https://placekitten.com/360/360'),
('211_114_175_93_83', 'Produk 2', 'Produk 2', 220000, 22, 'https://placekitten.com/360/360'),
('211_162_175_93_131', 'Produk 8', 'Produk 8', 880000, 88, 'https://placekitten.com/360/360');

-- --------------------------------------------------------

--
-- Table structure for table `keranjang_user`
--

CREATE TABLE `keranjang_user` (
  `id` int(11) UNSIGNED NOT NULL,
  `nama` varchar(32) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Dumping data for table `keranjang_user`
--

INSERT INTO `keranjang_user` (`id`, `nama`) VALUES
(1, 'Lili');

--
-- Indexes for dumped tables
--

--
-- Indexes for table `keranjang_history`
--
ALTER TABLE `keranjang_history`
  ADD PRIMARY KEY (`id`),
  ADD KEY `history_keranjang` (`id_keranjang`),
  ADD KEY `history_produk` (`id_produk`),
  ADD KEY `history_user` (`id_user`);

--
-- Indexes for table `keranjang_keranjang`
--
ALTER TABLE `keranjang_keranjang`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `keranjang_pos`
--
ALTER TABLE `keranjang_pos`
  ADD PRIMARY KEY (`id`),
  ADD KEY `pos_keranjang` (`id_keranjang`),
  ADD KEY `pos_produk` (`id_produk`),
  ADD KEY `pos_user` (`id_user`);

--
-- Indexes for table `keranjang_produk`
--
ALTER TABLE `keranjang_produk`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `id` (`id`);

--
-- Indexes for table `keranjang_user`
--
ALTER TABLE `keranjang_user`
  ADD PRIMARY KEY (`id`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `keranjang_history`
--
ALTER TABLE `keranjang_history`
  MODIFY `id` int(10) UNSIGNED NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=6;

--
-- AUTO_INCREMENT for table `keranjang_keranjang`
--
ALTER TABLE `keranjang_keranjang`
  MODIFY `id` int(10) UNSIGNED NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;

--
-- AUTO_INCREMENT for table `keranjang_pos`
--
ALTER TABLE `keranjang_pos`
  MODIFY `id` int(10) UNSIGNED NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=5;

--
-- AUTO_INCREMENT for table `keranjang_user`
--
ALTER TABLE `keranjang_user`
  MODIFY `id` int(11) UNSIGNED NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- Constraints for dumped tables
--

--
-- Constraints for table `keranjang_history`
--
ALTER TABLE `keranjang_history`
  ADD CONSTRAINT `history_keranjang` FOREIGN KEY (`id_keranjang`) REFERENCES `keranjang_keranjang` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  ADD CONSTRAINT `history_produk` FOREIGN KEY (`id_produk`) REFERENCES `keranjang_produk` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  ADD CONSTRAINT `history_user` FOREIGN KEY (`id_user`) REFERENCES `keranjang_user` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION;

--
-- Constraints for table `keranjang_pos`
--
ALTER TABLE `keranjang_pos`
  ADD CONSTRAINT `pos_keranjang` FOREIGN KEY (`id_keranjang`) REFERENCES `keranjang_keranjang` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  ADD CONSTRAINT `pos_produk` FOREIGN KEY (`id_produk`) REFERENCES `keranjang_produk` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  ADD CONSTRAINT `pos_user` FOREIGN KEY (`id_user`) REFERENCES `keranjang_user` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;

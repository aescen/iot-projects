-- phpMyAdmin SQL Dump
-- version 4.8.0.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Waktu pembuatan: 12 Jun 2020 pada 12.33
-- Versi server: 10.1.32-MariaDB
-- Versi PHP: 7.2.5

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
-- Struktur dari tabel `etching`
--

CREATE TABLE `etching` (
  `id` int(3) NOT NULL,
  `etching` varchar(16) NOT NULL,
  `relaytuang` tinyint(1) NOT NULL,
  `relaybuang` tinyint(1) NOT NULL,
  `relaygoyang` tinyint(1) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Dumping data untuk tabel `etching`
--

INSERT INTO `etching` (`id`, `etching`, `relaytuang`, `relaybuang`, `relaygoyang`) VALUES
(1, 'Etching 4x', 0, 0, 1);

-- --------------------------------------------------------

--
-- Struktur dari tabel `platenumbers`
--

CREATE TABLE `platenumbers` (
  `ids` int(4) NOT NULL,
  `plateNumbers` varchar(16) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Dumping data untuk tabel `platenumbers`
--

INSERT INTO `platenumbers` (`ids`, `plateNumbers`) VALUES
(1, 'B 457 UTY'),
(2, 'N 6920 GM');

-- --------------------------------------------------------

--
-- Struktur dari tabel `platenumbershistory`
--

CREATE TABLE `platenumbershistory` (
  `ids` int(11) NOT NULL,
  `plateNumbers` varchar(16) NOT NULL,
  `comeIn` datetime DEFAULT NULL,
  `comeOut` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Dumping data untuk tabel `platenumbershistory`
--

INSERT INTO `platenumbershistory` (`ids`, `plateNumbers`, `comeIn`, `comeOut`) VALUES
(1, 'B 457 UTY', '2020-06-06 08:00:00', '2020-06-06 16:00:00'),
(2, 'N 6920 GM', '2020-06-06 08:00:00', '2020-06-06 08:00:00'),
(3, 'B 457 UTY', '2020-06-07 08:00:00', '2020-06-07 16:15:00'),
(4, 'N 6920 GM', '2020-06-07 08:01:00', '2020-06-07 16:10:00'),
(5, 'B 457 UTY', '2020-06-11 10:32:16', '2020-06-11 10:35:19'),
(7, 'N 6920 GM', '2020-06-11 10:51:58', '2020-06-11 10:52:14'),
(8, 'N 6920 GM', '2020-06-11 10:52:32', '2020-06-11 10:52:46'),
(9, 'N 6920 GM', '2020-06-11 04:02:24', '2020-06-11 04:02:29'),
(10, 'N 6920 GM', '2020-06-11 11:05:24', '2020-06-11 11:05:40'),
(11, 'B 457 UTY', '2020-06-11 11:15:56', '2020-06-11 11:35:42'),
(12, 'B 457 UTY', '2020-06-11 11:36:29', '2020-06-11 11:36:37'),
(13, 'B 457 UTY', '2020-06-11 11:36:51', '2020-06-11 11:36:57'),
(14, 'B 457 UTY', '2020-06-11 11:37:03', '2020-06-11 11:37:09'),
(15, 'B 457 UTY', '2020-06-11 11:37:15', '2020-06-11 11:37:21'),
(16, 'B 457 UTY', '2020-06-11 11:37:25', '2020-06-11 11:37:30'),
(17, 'B 457 UTY', '2020-06-11 11:37:35', '2020-06-11 11:37:44'),
(18, 'N 6920 GM', '2020-06-11 11:38:31', '2020-06-11 11:38:40'),
(19, 'N 6920 GM', '2020-06-11 11:38:58', '2020-06-11 11:39:06'),
(20, 'N 6920 GM', '2020-06-11 11:39:13', '2020-06-11 11:39:18'),
(21, 'N 6920 GM', '2020-06-11 11:39:28', '2020-06-11 11:39:33'),
(22, 'N 6920 GM', '2020-06-11 11:39:38', '2020-06-11 11:39:43'),
(23, 'N 6920 GM', '2020-06-11 11:39:48', '2020-06-11 11:39:59'),
(24, 'N 6920 GM', '2020-06-11 11:40:04', '2020-06-11 11:40:11'),
(25, 'N 6920 GM', '2020-06-11 11:40:17', '2020-06-11 11:40:23'),
(26, 'N 6920 GM', '2020-06-11 11:40:41', '2020-06-11 11:40:48'),
(27, 'B 457 UTY', '2020-06-11 11:41:24', '2020-06-11 11:41:27'),
(28, 'B 457 UTY', '2020-06-11 11:41:32', '2020-06-11 11:41:42'),
(29, 'B 457 UTY', '2020-06-11 11:42:12', '2020-06-11 11:42:24'),
(30, 'N 6920 GM', '2020-06-11 11:42:35', '2020-06-11 11:42:39'),
(31, 'N 6920 GM', '2020-06-11 11:42:44', '2020-06-11 11:42:48'),
(32, 'N 6920 GM', '2020-06-11 11:42:52', '2020-06-11 11:43:36'),
(33, 'B 457 UTY', '2020-06-11 11:43:12', '2020-06-11 11:43:27'),
(34, 'N 6920 GM', '2020-06-11 11:43:40', '2020-06-11 11:44:36'),
(35, 'N 6920 GM', '2020-06-11 11:44:40', NULL);

-- --------------------------------------------------------

--
-- Struktur dari tabel `uv`
--

CREATE TABLE `uv` (
  `id` varchar(12) NOT NULL,
  `value` varchar(5) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Dumping data untuk tabel `uv`
--

INSERT INTO `uv` (`id`, `value`) VALUES
('fan1', '1'),
('fan2', '0'),
('humidity1', '75'),
('humidity2', '85'),
('lamp1', '0'),
('lamp2', '1'),
('lux1', '152'),
('lux2', '532'),
('temperature1', '25'),
('temperature2', '22'),
('uvIntensity1', '2'),
('uvIntensity2', '5'),
('uvLambda1', '350'),
('uvLambda2', '370'),
('uvLevel1', '1'),
('uvLevel2', '3');

--
-- Indexes for dumped tables
--

--
-- Indeks untuk tabel `etching`
--
ALTER TABLE `etching`
  ADD PRIMARY KEY (`id`);

--
-- Indeks untuk tabel `platenumbers`
--
ALTER TABLE `platenumbers`
  ADD PRIMARY KEY (`ids`),
  ADD UNIQUE KEY `platenumber` (`plateNumbers`) USING HASH;

--
-- Indeks untuk tabel `platenumbershistory`
--
ALTER TABLE `platenumbershistory`
  ADD PRIMARY KEY (`ids`);

--
-- Indeks untuk tabel `uv`
--
ALTER TABLE `uv`
  ADD PRIMARY KEY (`id`);

--
-- AUTO_INCREMENT untuk tabel yang dibuang
--

--
-- AUTO_INCREMENT untuk tabel `platenumbers`
--
ALTER TABLE `platenumbers`
  MODIFY `ids` int(4) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;

--
-- AUTO_INCREMENT untuk tabel `platenumbershistory`
--
ALTER TABLE `platenumbershistory`
  MODIFY `ids` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=36;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;

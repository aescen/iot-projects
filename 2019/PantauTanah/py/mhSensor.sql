-- phpMyAdmin SQL Dump
-- version 4.2.12deb2+deb8u5
-- http://www.phpmyadmin.net
--
-- Host: localhost
-- Generation Time: Mar 02, 2019 at 07:40 AM
-- Server version: 5.5.62-0+deb8u1
-- PHP Version: 5.6.40-0+deb8u1

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;

--
-- Database: `mnet`
--

-- --------------------------------------------------------

--
-- Table structure for table `mhSensor`
--

CREATE TABLE IF NOT EXISTS `mhSensor` (
  `nodeID` int(10) unsigned NOT NULL,
  `meshNodeID` int(10) unsigned NOT NULL,
  `soilRead` int(11) NOT NULL,
  `soilStatus` varchar(32) NOT NULL,
  `timeStamp` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

--
-- Dumping data for table `mhSensor`
--

INSERT INTO `mhSensor` (`nodeID`, `meshNodeID`, `soilRead`, `soilStatus`, `timeStamp`) VALUES
(1, 5, 1023, 'Sensor terputus/di udara!', '2019-03-02 07:40:08'),
(2, 36, 1023, 'Sensor terputus/di udara!', '2019-03-02 07:39:42'),
(3, 34, 1023, 'Sensor terputus/di udara!', '2019-03-02 04:41:54'),
(4, 2, 1022, 'Sensor terputus/di udara!', '2019-03-02 07:40:33'),
(5, 26, 1021, 'Sensor terputus/di udara!', '2019-03-02 07:40:35'),
(6, 4, 1023, 'Sensor terputus/di udara!', '2019-03-02 07:39:23');

--
-- Indexes for dumped tables
--

--
-- Indexes for table `mhSensor`
--
ALTER TABLE `mhSensor`
 ADD PRIMARY KEY (`nodeID`), ADD UNIQUE KEY `nodeID` (`nodeID`);

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;

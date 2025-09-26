-- MySQL dump 10.13  Distrib 8.4.6, for macos15.4 (arm64)
--
-- Host: localhost    Database: pizza_ordering
-- ------------------------------------------------------
-- Server version	9.4.0

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Current Database: `pizza_ordering`
--

CREATE DATABASE /*!32312 IF NOT EXISTS*/ `pizza_ordering` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci */ /*!80016 DEFAULT ENCRYPTION='N' */;

USE `pizza_ordering`;

--
-- Table structure for table `customers`
--

DROP TABLE IF EXISTS `customers`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `customers` (
  `Customer_ID` int NOT NULL,
  `Name` varchar(100) NOT NULL,
  `Gender` varchar(10) DEFAULT NULL,
  `Birthdate` date DEFAULT NULL,
  `Postcode_ID` int DEFAULT NULL,
  `Street_Number` int DEFAULT NULL,
  `Email_Address` varchar(100) DEFAULT NULL,
  `Phone_Number` varchar(15) DEFAULT NULL,
  `Username` varchar(50) DEFAULT NULL,
  `Password` varchar(255) DEFAULT NULL,
  `canBirthDay` tinyint(1) NOT NULL DEFAULT '0',
  `canDiscount` tinyint(1) NOT NULL DEFAULT '0',
  `PizzasOrdered` int NOT NULL DEFAULT '0',
  `Street_Name` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`Customer_ID`),
  UNIQUE KEY `uq_customers_email` (`Email_Address`),
  KEY `idx_customers_postcode` (`Postcode_ID`),
  CONSTRAINT `fk_customers_postcode` FOREIGN KEY (`Postcode_ID`) REFERENCES `postcode` (`postcode_id`) ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `customers`
--

LOCK TABLES `customers` WRITE;
/*!40000 ALTER TABLE `customers` DISABLE KEYS */;
/*!40000 ALTER TABLE `customers` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `delivery_person`
--

DROP TABLE IF EXISTS `delivery_person`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `delivery_person` (
  `DeliveryDriver_ID` int NOT NULL,
  `DeliveryDriver_Name` varchar(100) NOT NULL,
  `isAvailable` tinyint(1) NOT NULL DEFAULT '1',
  `unavailable_until` timestamp NULL DEFAULT NULL,
  PRIMARY KEY (`DeliveryDriver_ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `delivery_person`
--

LOCK TABLES `delivery_person` WRITE;
/*!40000 ALTER TABLE `delivery_person` DISABLE KEYS */;
/*!40000 ALTER TABLE `delivery_person` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `delivery_person_postcode`
--

DROP TABLE IF EXISTS `delivery_person_postcode`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `delivery_person_postcode` (
  `DeliveryDriver_ID` int NOT NULL,
  `Postcode_ID` int NOT NULL,
  `assigned_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`DeliveryDriver_ID`,`Postcode_ID`),
  KEY `Postcode_ID` (`Postcode_ID`),
  CONSTRAINT `delivery_person_postcode_ibfk_1` FOREIGN KEY (`DeliveryDriver_ID`) REFERENCES `delivery_person` (`DeliveryDriver_ID`) ON DELETE CASCADE,
  CONSTRAINT `delivery_person_postcode_ibfk_2` FOREIGN KEY (`Postcode_ID`) REFERENCES `postcode` (`postcode_id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `delivery_person_postcode`
--

LOCK TABLES `delivery_person_postcode` WRITE;
/*!40000 ALTER TABLE `delivery_person_postcode` DISABLE KEYS */;
/*!40000 ALTER TABLE `delivery_person_postcode` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `discount_code`
--

DROP TABLE IF EXISTS `discount_code`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `discount_code` (
  `DiscountCode_ID` int NOT NULL,
  `Discount_Value` decimal(10,0) DEFAULT NULL,
  `is_active` tinyint DEFAULT NULL,
  `code` varchar(32) DEFAULT NULL,
  `valid_from` date DEFAULT NULL,
  `valid_to` date DEFAULT NULL,
  PRIMARY KEY (`DiscountCode_ID`),
  UNIQUE KEY `uq_discount_code` (`code`),
  CONSTRAINT `chk_discount_validity` CHECK (((`valid_from` is null) or (`valid_to` is null) or (`valid_from` <= `valid_to`))),
  CONSTRAINT `chk_discount_value_range` CHECK (((`Discount_Value` >= 0) and (`Discount_Value` <= 100)))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `discount_code`
--

LOCK TABLES `discount_code` WRITE;
/*!40000 ALTER TABLE `discount_code` DISABLE KEYS */;
/*!40000 ALTER TABLE `discount_code` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `driver_group`
--

DROP TABLE IF EXISTS `driver_group`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `driver_group` (
  `Group_ID` int NOT NULL AUTO_INCREMENT,
  `Created_At` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `DeliveryDriver_ID` int NOT NULL,
  `Postcode_ID` int NOT NULL,
  `IsDispatched` tinyint(1) NOT NULL DEFAULT '0',
  PRIMARY KEY (`Group_ID`),
  KEY `idx_driver_group_driver` (`DeliveryDriver_ID`),
  KEY `idx_driver_group_postcode` (`Postcode_ID`),
  CONSTRAINT `fk_driver_group_driver` FOREIGN KEY (`DeliveryDriver_ID`) REFERENCES `delivery_person` (`DeliveryDriver_ID`) ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT `fk_driver_group_postcode` FOREIGN KEY (`Postcode_ID`) REFERENCES `postcode` (`postcode_id`) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `driver_group`
--

LOCK TABLES `driver_group` WRITE;
/*!40000 ALTER TABLE `driver_group` DISABLE KEYS */;
/*!40000 ALTER TABLE `driver_group` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `group`
--

DROP TABLE IF EXISTS `group`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `group` (
  `Group_ID` int NOT NULL,
  `Created_At` timestamp NULL DEFAULT NULL,
  `DeliveryDriver_Name` varchar(255) DEFAULT NULL,
  `Postcode` varchar(10) DEFAULT NULL,
  `IsDispatched` tinyint DEFAULT NULL,
  PRIMARY KEY (`Group_ID`),
  KEY `AK` (`Group_ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `group`
--

LOCK TABLES `group` WRITE;
/*!40000 ALTER TABLE `group` DISABLE KEYS */;
/*!40000 ALTER TABLE `group` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `ingredients`
--

DROP TABLE IF EXISTS `ingredients`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `ingredients` (
  `ingredient_id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(100) NOT NULL,
  `cost` decimal(8,2) NOT NULL,
  `is_meat` tinyint(1) NOT NULL DEFAULT '0',
  `is_dairy` tinyint(1) NOT NULL DEFAULT '0',
  `is_vegan` tinyint(1) NOT NULL DEFAULT '0',
  PRIMARY KEY (`ingredient_id`),
  UNIQUE KEY `name` (`name`),
  CONSTRAINT `chk_ingredient_cost_positive` CHECK ((`cost` > 0)),
  CONSTRAINT `ingredients_chk_1` CHECK ((`cost` > 0))
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ingredients`
--

LOCK TABLES `ingredients` WRITE;
/*!40000 ALTER TABLE `ingredients` DISABLE KEYS */;
INSERT INTO `ingredients` VALUES (1,'Tomato sauce',0.30,0,0,1),(2,'Mozzarella',0.80,0,1,0),(3,'Basil',0.10,0,0,1),(4,'Pepperoni',0.90,1,0,0);
/*!40000 ALTER TABLE `ingredients` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `menu_items`
--

DROP TABLE IF EXISTS `menu_items`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `menu_items` (
  `item_id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(100) NOT NULL,
  `type` enum('pizza','drink','dessert') NOT NULL,
  `base_price` decimal(8,2) DEFAULT NULL,
  `is_vegan` tinyint(1) NOT NULL DEFAULT '0',
  `is_vegetarian` tinyint(1) NOT NULL DEFAULT '0',
  `active` tinyint(1) NOT NULL DEFAULT '1',
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`item_id`),
  UNIQUE KEY `uq_menu_items_name_type` (`name`,`type`),
  CONSTRAINT `chk_base_price_positive` CHECK ((`base_price` > 0))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `menu_items`
--

LOCK TABLES `menu_items` WRITE;
/*!40000 ALTER TABLE `menu_items` DISABLE KEYS */;
/*!40000 ALTER TABLE `menu_items` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `order_items`
--

DROP TABLE IF EXISTS `order_items`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `order_items` (
  `OrderItem_ID` int NOT NULL,
  `Order_ID` int DEFAULT NULL,
  `Customer_ID` int DEFAULT NULL,
  `Pizza_ID` int DEFAULT NULL,
  `Dessert_ID` int DEFAULT NULL,
  `Drink_ID` int DEFAULT NULL,
  `pizza_numbers` int DEFAULT NULL,
  PRIMARY KEY (`OrderItem_ID`),
  KEY `idx_order_items_order` (`Order_ID`),
  CONSTRAINT `fk_order_items_order` FOREIGN KEY (`Order_ID`) REFERENCES `orders` (`Order_ID`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `order_items`
--

LOCK TABLES `order_items` WRITE;
/*!40000 ALTER TABLE `order_items` DISABLE KEYS */;
/*!40000 ALTER TABLE `order_items` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `orders`
--

DROP TABLE IF EXISTS `orders`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `orders` (
  `Order_ID` int NOT NULL,
  `Customer_ID` int NOT NULL,
  `Total_Amount` decimal(10,0) DEFAULT NULL,
  `Order_Date` date DEFAULT NULL,
  `DeliveryDriver_ID` int DEFAULT NULL,
  `Order_Status` varchar(50) DEFAULT NULL,
  `Order_StartTime` time DEFAULT NULL,
  `Order_EndTime` time DEFAULT NULL,
  `Group_ID` int DEFAULT NULL,
  `Postcode` varchar(10) DEFAULT NULL,
  `DiscountCode_ID` int DEFAULT NULL,
  PRIMARY KEY (`Order_ID`),
  KEY `idx_orders_status_date` (`Order_Status`,`Order_Date`),
  CONSTRAINT `chk_order_status` CHECK ((`Order_Status` in (_utf8mb4'new',_utf8mb4'preparing',_utf8mb4'dispatched',_utf8mb4'delivered',_utf8mb4'failed')))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `orders`
--

LOCK TABLES `orders` WRITE;
/*!40000 ALTER TABLE `orders` DISABLE KEYS */;
/*!40000 ALTER TABLE `orders` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `pizza_ingredients`
--

DROP TABLE IF EXISTS `pizza_ingredients`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `pizza_ingredients` (
  `pizza_id` int NOT NULL,
  `ingredient_id` int NOT NULL,
  `quantity_unit` varchar(20) NOT NULL,
  `quantity` decimal(8,2) NOT NULL,
  PRIMARY KEY (`pizza_id`,`ingredient_id`),
  UNIQUE KEY `uc_pizza_ingredient` (`pizza_id`,`ingredient_id`),
  KEY `ingredient_id` (`ingredient_id`),
  CONSTRAINT `pizza_ingredients_ibfk_1` FOREIGN KEY (`pizza_id`) REFERENCES `pizzas` (`pizza_id`) ON DELETE CASCADE,
  CONSTRAINT `pizza_ingredients_ibfk_2` FOREIGN KEY (`ingredient_id`) REFERENCES `ingredients` (`ingredient_id`) ON DELETE RESTRICT,
  CONSTRAINT `chk_pizza_ingredient_quantity` CHECK ((`quantity` > 0))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `pizza_ingredients`
--

LOCK TABLES `pizza_ingredients` WRITE;
/*!40000 ALTER TABLE `pizza_ingredients` DISABLE KEYS */;
/*!40000 ALTER TABLE `pizza_ingredients` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Temporary view structure for view `pizza_menu_prices`
--

DROP TABLE IF EXISTS `pizza_menu_prices`;
/*!50001 DROP VIEW IF EXISTS `pizza_menu_prices`*/;
SET @saved_cs_client     = @@character_set_client;
/*!50503 SET character_set_client = utf8mb4 */;
/*!50001 CREATE VIEW `pizza_menu_prices` AS SELECT 
 1 AS `pizza_id`,
 1 AS `pizza_name`,
 1 AS `calculated_price`,
 1 AS `pizza_isvegan`,
 1 AS `pizza_isvegetarian`*/;
SET character_set_client = @saved_cs_client;

--
-- Table structure for table `pizzas`
--

DROP TABLE IF EXISTS `pizzas`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `pizzas` (
  `pizza_id` int NOT NULL,
  `pizza_name` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`pizza_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `pizzas`
--

--
-- Table structure for table `postcode`
--

DROP TABLE IF EXISTS `postcode`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `postcode` (
  `postcode_id` int NOT NULL,
  `postcode` varchar(20) NOT NULL,
  `DeliveryDriver_ID` int DEFAULT NULL,
  PRIMARY KEY (`postcode_id`),
  UNIQUE KEY `AK_postcode` (`postcode`),
  KEY `idx_postcode_driver` (`DeliveryDriver_ID`),
  CONSTRAINT `fk_postcode_driver` FOREIGN KEY (`DeliveryDriver_ID`) REFERENCES `delivery_person` (`DeliveryDriver_ID`) ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `postcode`
--

LOCK TABLES `postcode` WRITE;
/*!40000 ALTER TABLE `postcode` DISABLE KEYS */;
/*!40000 ALTER TABLE `postcode` ENABLE KEYS */;
UNLOCK TABLES;
--
-- Dumping events for database 'pizza_ordering'
--

--
-- Dumping routines for database 'pizza_ordering'
--

--
-- Current Database: `pizza_ordering`
--

USE `pizza_ordering`;

--
-- Final view structure for view `pizza_menu_prices`
--

/*!50001 DROP VIEW IF EXISTS `pizza_menu_prices`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_0900_ai_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`pizza_app`@`127.0.0.1` SQL SECURITY DEFINER */
/*!50001 VIEW `pizza_menu_prices` AS select `p`.`pizza_id` AS `pizza_id`,`p`.`pizza_name` AS `pizza_name`,round(((sum(`i`.`cost`) * 1.4) * 1.09),2) AS `calculated_price`,(case when (min((case when ((`i`.`is_meat` = 0) and (`i`.`is_dairy` = 0)) then 1 else 0 end)) = 1) then 1 else 0 end) AS `pizza_isvegan`,(case when (min((case when (`i`.`is_meat` = 0) then 1 else 0 end)) = 1) then 1 else 0 end) AS `pizza_isvegetarian` from ((`pizzas` `p` join `pizza_ingredients` `pi` on((`pi`.`pizza_id` = `p`.`pizza_id`))) join `ingredients` `i` on((`i`.`ingredient_id` = `pi`.`ingredient_id`))) group by `p`.`pizza_id`,`p`.`pizza_name` */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-09-19 16:23:19

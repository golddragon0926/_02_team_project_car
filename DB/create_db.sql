USE car_oil_db;

SET FOREIGN_KEY_CHECKS = 0;

DROP TABLE IF EXISTS `Subsidy`;
DROP TABLE IF EXISTS `Oil_price`;
DROP TABLE IF EXISTS `Region`;
DROP TABLE IF EXISTS `New_Registration`;
DROP TABLE IF EXISTS `Fuel_Type`;
DROP TABLE IF EXISTS `FAQ`;

CREATE TABLE `Region` (
	`region_id`	INT	NOT NULL AUTO_INCREMENT,
	`region_code`	VARCHAR(10)	NOT NULL,
	`region_name`	VARCHAR(20)	NOT NULL,
	PRIMARY KEY (`region_id`)
);

CREATE TABLE `Fuel_Type` (
	`fuel_id`	INT	NOT NULL AUTO_INCREMENT,
	`fuel_code`	VARCHAR(10)	NOT NULL,
	`fuel_name`	VARCHAR(20)	NOT NULL,
	PRIMARY KEY (`fuel_id`)
);

CREATE TABLE `Subsidy` (
	`id`	INT	NOT NULL AUTO_INCREMENT,
	`region_id`	INT	NOT NULL,
	`year`	YEAR	NOT NULL,
	`sigungu`	VARCHAR(20)	NOT NULL,
	`vehicle_type`	VARCHAR(10)	NOT NULL,
	`manufacturer`	VARCHAR(30)	NOT NULL,
	`model_name`	VARCHAR(50)	NOT NULL,
	`national_subsidy`	DECIMAL(7,1)	NOT NULL,
	`local_subsidy`	DECIMAL(7,1)	NOT NULL,
	`total_subsidy`	DECIMAL(7,1)	NOT NULL,
	PRIMARY KEY (`id`)
);

CREATE TABLE `Oil_price` (
	`id`	INT	NOT NULL AUTO_INCREMENT,
	`region_id`	INT	NOT NULL,
	`price_date`	DATE	NOT NULL,
	`fuel_code`	VARCHAR(10)	NOT NULL,
	`price`	DECIMAL(7,2)	NOT NULL,
	PRIMARY KEY (`id`)
);

CREATE TABLE `New_Registration` (
	`id`	INT	NOT NULL AUTO_INCREMENT,
	`region_id`	INT	NOT NULL,
	`fuel_id`	INT	NOT NULL,
	`reg_year`	YEAR	NOT NULL,
	`reg_month`	INT	NOT NULL,
	`vehicle_type`	VARCHAR(10)	NOT NULL,
	`count`	INT	NOT NULL,
	PRIMARY KEY (`id`)
);

CREATE TABLE `FAQ` (
	`id`	INT	NOT NULL AUTO_INCREMENT,
	`brand`	VARCHAR(20)	NOT NULL,
	`title`	VARCHAR(500)	NOT NULL,
	`content`	TEXT	NOT NULL,
	`category`	VARCHAR(50)	NULL,
	PRIMARY KEY (`id`)
);

ALTER TABLE `Subsidy` ADD CONSTRAINT `FK_Region_TO_Subsidy_1` FOREIGN KEY (`region_id`) REFERENCES `Region` (`region_id`);
ALTER TABLE `Oil_price` ADD CONSTRAINT `FK_Region_TO_Oil_price_1` FOREIGN KEY (`region_id`) REFERENCES `Region` (`region_id`);
ALTER TABLE `New_Registration` ADD CONSTRAINT `FK_Region_TO_New_Registration_1` FOREIGN KEY (`region_id`) REFERENCES `Region` (`region_id`);
ALTER TABLE `New_Registration` ADD CONSTRAINT `FK_Fuel_Type_TO_New_Registration_1` FOREIGN KEY (`fuel_id`) REFERENCES `Fuel_Type` (`fuel_id`);

SET FOREIGN_KEY_CHECKS = 1;
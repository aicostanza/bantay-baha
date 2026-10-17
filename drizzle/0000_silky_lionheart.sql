CREATE TABLE `readings` (
	`id` integer PRIMARY KEY AUTOINCREMENT NOT NULL,
	`sensor_id` text NOT NULL,
	`water_level_cm` real NOT NULL,
	`timestamp` text NOT NULL
);

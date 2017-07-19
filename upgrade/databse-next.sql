ALTER TABLE `canvas_versions` CHANGE `version_number` `version_number` INT(11)  NULL  DEFAULT NULL;
ALTER TABLE `canvases` DROP `current_version`;


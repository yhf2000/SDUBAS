/*
 Navicat Premium Data Transfer

 Source Server         : mysql
 Source Server Type    : MySQL
 Source Server Version : 80031
 Source Host           : localhost:3306
 Source Schema         : sdubas

 Target Server Type    : MySQL
 Target Server Version : 80031
 File Encoding         : 65001

 Date: 07/09/2023 20:07:22
*/

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ----------------------------
-- Table structure for project_content
-- ----------------------------
DROP TABLE IF EXISTS `project_content`;
CREATE TABLE `project_content`  (
  `id` int(0) NOT NULL AUTO_INCREMENT,
  `project_id` int(0) NOT NULL,
  `type` int(0) NOT NULL,
  `prefix` varchar(64) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL,
  `name` varchar(64) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `file_id` int(0) NULL DEFAULT NULL,
  `content` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL,
  `weight` float NOT NULL,
  `feature` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL,
  `has_delete` int(0) NOT NULL,
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `ix_project_content_id`(`id`) USING BTREE,
  INDEX `ix_project_content_type`(`type`) USING BTREE,
  INDEX `ix_project_content_project_id`(`project_id`) USING BTREE,
  CONSTRAINT `project_content_ibfk_1` FOREIGN KEY (`project_id`) REFERENCES `project` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 42 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of project_content
-- ----------------------------
INSERT INTO `project_content` VALUES (34, 12, 0, '数据结构/数据', '原生1', NULL, NULL, 0.5, NULL, 0);
INSERT INTO `project_content` VALUES (35, 12, 0, '数据结构/数据', '原生2', NULL, NULL, 0.5, NULL, 0);
INSERT INTO `project_content` VALUES (36, 12, 0, '数据结构/结构', '原生3', NULL, NULL, 0.5, NULL, 0);
INSERT INTO `project_content` VALUES (37, 13, 0, '数据结构/数据', '原生1', NULL, NULL, 0.5, NULL, 0);
INSERT INTO `project_content` VALUES (38, 13, 0, '数据结构/数据', '原生2', NULL, NULL, 0.5, NULL, 0);
INSERT INTO `project_content` VALUES (39, 13, 0, '数据结构/结构', '原生3', NULL, NULL, 0.5, NULL, 0);
INSERT INTO `project_content` VALUES (40, 14, 0, '数据结构/数据', '原生1', NULL, NULL, 0.5, NULL, 1);
INSERT INTO `project_content` VALUES (41, 14, 0, '数据结构/数据', '原生2', NULL, NULL, 0.5, NULL, 1);
INSERT INTO `project_content` VALUES (42, 14, 0, '数据结构/结构', '原生3', NULL, NULL, 0.5, NULL, 1);
INSERT INTO `project_content` VALUES (43, 15, 0, '数据结构/数据', '原生1', NULL, NULL, 0.5, NULL, 0);
INSERT INTO `project_content` VALUES (44, 15, 0, '数据结构/数据', '原生2', NULL, NULL, 0.5, NULL, 0);
INSERT INTO `project_content` VALUES (45, 15, 0, '数据结构/结构', '原生3', NULL, NULL, 0.5, NULL, 0);
INSERT INTO `project_content` VALUES (46, 16, 0, '数据结构/数据', '原生1', NULL, NULL, 0.5, NULL, 0);
INSERT INTO `project_content` VALUES (47, 16, 0, '数据结构/数据', '原生2', NULL, NULL, 0.5, NULL, 0);
INSERT INTO `project_content` VALUES (48, 16, 0, '数据结构/结构', '原生3', NULL, NULL, 0.5, NULL, 0);

SET FOREIGN_KEY_CHECKS = 1;

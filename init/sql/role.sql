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

 Date: 07/09/2023 19:58:59
*/

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ----------------------------
-- Table structure for role
-- ----------------------------
DROP TABLE IF EXISTS `role`;
CREATE TABLE `role`  (
  `id` int(0) NOT NULL AUTO_INCREMENT,
  `name` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `description` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `superiorId` int(0) NOT NULL,
  `template` int(0) NOT NULL,
  `template_val` varchar(4096) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL,
  `tplt_id` int(0) NULL DEFAULT NULL,
  `status` int(0) NOT NULL,
  `superiorListId` varchar(4096) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL,
  `has_delete` int(0) NOT NULL,
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `id`(`id`) USING BTREE,
  INDEX `ix_role_superiorId`(`superiorId`) USING BTREE,
  INDEX `ix_role_tplt_id`(`tplt_id`) USING BTREE,
  INDEX `ix_role_status`(`status`) USING BTREE,
  INDEX `ix_role_has_delete`(`has_delete`) USING BTREE,
  INDEX `ix_role_template`(`template`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 32 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of role
-- ----------------------------
INSERT INTO `role` VALUES (1, '超级管理员', '', 0, 0, NULL, NULL, 0, NULL, 0);
INSERT INTO `role` VALUES (2, '学校', '', 1, 0, NULL, NULL, 0, '{\"ids\": [1]}', 0);
INSERT INTO `role` VALUES (3, '学院', '', 2, 0, NULL, NULL, 0, '{\"ids\": [1, 2]}', 0);
INSERT INTO `role` VALUES (4, '教师', '', 3, 0, NULL, NULL, 0, '{\"ids\": [1, 2, 3]}', 0);
INSERT INTO `role` VALUES (5, '学生', '', 4, 0, NULL, NULL, 0, '{\"ids\": [1, 2, 3, 4]}', 0);
INSERT INTO `role` VALUES (29, 'default', '', 1, 0, NULL, NULL, 0, '{\"ids\": [1]}', 0);
INSERT INTO `role` VALUES (30, 'project1-1', 'project1-1', 1, 0, NULL, NULL, 0, '{\"ids\": [1]}', 0);
INSERT INTO `role` VALUES (31, 'project2-1', 'project2-1', 1, 0, NULL, NULL, 0, '{\"ids\": [1]}', 0);
INSERT INTO `role` VALUES (32, 'project3-1', 'project3-1', 1, 0, NULL, NULL, 0, '{\"ids\": [1]}', 0);
INSERT INTO `role` VALUES (33, 'project4-1', 'project4-1', 1, 0, NULL, NULL, 0, '{\"ids\": [1]}', 0);
INSERT INTO `role` VALUES (34, 'project1-2', 'project1-2', 1, 0, NULL, NULL, 0, '{\"ids\": [1]}', 0);
INSERT INTO `role` VALUES (35, 'project2-2', 'project2-2', 1, 0, NULL, NULL, 0, '{\"ids\": [1]}', 0);
INSERT INTO `role` VALUES (36, 'project3-2', 'project3-2', 1, 0, NULL, NULL, 0, '{\"ids\": [1]}', 0);
INSERT INTO `role` VALUES (37, 'project4-2', 'project4-2', 1, 0, NULL, NULL, 0, '{\"ids\": [1]}', 0);
INSERT INTO `role` VALUES (38, 'project5-1', 'project5-1', 1, 0, NULL, NULL, 0, '{\"ids\": [1]}', 0);
INSERT INTO `role` VALUES (39, 'project5-2', 'project5-2', 1, 0, NULL, NULL, 0, '{\"ids\": [1]}', 0);
INSERT INTO `role` VALUES (40, 'project1', 'project1', 29, 0, NULL, NULL, 0, '{\"ids\": [1, 29]}', 0);
INSERT INTO `role` VALUES (41, 'project1', 'project1', 29, 0, NULL, NULL, 0, '{\"ids\": [1, 29]}', 0);
INSERT INTO `role` VALUES (42, 'role1', 'role1', 1, 0, NULL, NULL, 0, '{\"ids\": [1]}', 0);
INSERT INTO `role` VALUES (43, 'role2', 'role2', 1, 0, NULL, NULL, 0, '{\"ids\": [1]}', 0);
INSERT INTO `role` VALUES (44, 'role3', 'role3', 1, 0, NULL, NULL, 0, '{\"ids\": [1]}', 0);
INSERT INTO `role` VALUES (45, 'role4', 'role4', 1, 0, NULL, NULL, 0, '{\"ids\": [1]}', 0);

SET FOREIGN_KEY_CHECKS = 1;

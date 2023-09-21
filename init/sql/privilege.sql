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

 Date: 07/09/2023 19:59:39
*/

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ----------------------------
-- Table structure for privilege
-- ----------------------------
DROP TABLE IF EXISTS `privilege`;
CREATE TABLE `privilege`  (
  `id` int(0) NOT NULL AUTO_INCREMENT,
  `service_type` int(0) NULL DEFAULT NULL,
  `service_id` int(0) NULL DEFAULT NULL,
  `key` varchar(64) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL,
  `name` varchar(64) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL,
  `name_alias` varchar(64) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL,
  `has_delete` int(0) NOT NULL,
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `id`(`id`) USING BTREE,
  INDEX `ix_privilege_name`(`name`) USING BTREE,
  INDEX `ix_privilege_service_id`(`service_id`) USING BTREE,
  INDEX `ix_privilege_key`(`key`) USING BTREE,
  INDEX `ix_privilege_service_type`(`service_type`) USING BTREE,
  INDEX `ix_privilege_has_delete`(`has_delete`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 36 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of privilege
-- ----------------------------
INSERT INTO `privilege` VALUES (1, 7, NULL, '', '项目查看', NULL, 0);
INSERT INTO `privilege` VALUES (2, 7, NULL, '', '项目提交', NULL, 0);
INSERT INTO `privilege` VALUES (3, 7, NULL, '', '项目批阅', NULL, 0);
INSERT INTO `privilege` VALUES (4, 7, NULL, '', '项目编辑', NULL, 0);
INSERT INTO `privilege` VALUES (5, 7, NULL, '', '项目删除', NULL, 0);
INSERT INTO `privilege` VALUES (6, 7, NULL, '', '项目学分认定', NULL, 0);
INSERT INTO `privilege` VALUES (7, 5, NULL, NULL, '资源编辑', NULL, 0);
INSERT INTO `privilege` VALUES (8, 5, NULL, NULL, '资源申请', NULL, 0);
INSERT INTO `privilege` VALUES (9, 5, NULL, NULL, '资源审批', NULL, 0);
INSERT INTO `privilege` VALUES (10, 5, NULL, NULL, '资源删除', NULL, 0);
INSERT INTO `privilege` VALUES (11, 5, NULL, NULL, '添加资源', NULL, 0);
INSERT INTO `privilege` VALUES (12, 6, NULL, NULL, '查看资金', NULL, 0);
INSERT INTO `privilege` VALUES (13, 6, NULL, NULL, '资金管理', NULL, 0);
INSERT INTO `privilege` VALUES (14, NULL, NULL, '', '添加角色', NULL, 0);
INSERT INTO `privilege` VALUES (15, 0, NULL, NULL, '添加用户', NULL, 0);
INSERT INTO `privilege` VALUES (16, 0, NULL, NULL, '用户管理', NULL, 0);
INSERT INTO `privilege` VALUES (17, 1, NULL, NULL, '添加学校', NULL, 0);
INSERT INTO `privilege` VALUES (18, 1, NULL, NULL, '学校管理', NULL, 0);
INSERT INTO `privilege` VALUES (19, 2, NULL, NULL, '添加学院', NULL, 0);
INSERT INTO `privilege` VALUES (20, 2, NULL, NULL, '学院管理', NULL, 0);
INSERT INTO `privilege` VALUES (21, 3, NULL, NULL, '添加专业', NULL, 0);
INSERT INTO `privilege` VALUES (22, 3, NULL, NULL, '专业管理', NULL, 0);
INSERT INTO `privilege` VALUES (23, 4, NULL, NULL, '添加班级', NULL, 0);
INSERT INTO `privilege` VALUES (24, 4, NULL, NULL, '班级管理', NULL, 0);
INSERT INTO `privilege` VALUES (25, NULL, NULL, NULL, '查看', NULL, 0);
INSERT INTO `privilege` VALUES (33, 7, NULL, NULL, '项目新建', NULL, 0);
INSERT INTO `privilege` VALUES (34, 1, NULL, NULL, '学校查看', NULL, 0);
INSERT INTO `privilege` VALUES (35, 2, NULL, NULL, '学院查看 ', NULL, 0);

SET FOREIGN_KEY_CHECKS = 1;

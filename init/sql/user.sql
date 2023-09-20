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

 Date: 07/09/2023 19:55:20
*/

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ----------------------------
-- Table structure for user
-- ----------------------------
DROP TABLE IF EXISTS `user`;
CREATE TABLE `user`  (
  `id` int(0) NOT NULL AUTO_INCREMENT,
  `username` varchar(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `password` varchar(128) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `email` varchar(64) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `card_id` varchar(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL,
  `registration_dt` datetime(0) NOT NULL ON UPDATE CURRENT_TIMESTAMP(0),
  `storage_quota` int(0) NOT NULL,
  `status` int(0) NOT NULL,
  `has_delete` int(0) NOT NULL,
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `id`(`id`) USING BTREE,
  UNIQUE INDEX `username`(`username`) USING BTREE,
  UNIQUE INDEX `email`(`email`) USING BTREE,
  UNIQUE INDEX `card_id`(`card_id`) USING BTREE,
  INDEX `ix_user_has_delete`(`has_delete`) USING BTREE,
  INDEX `ix_user_status`(`status`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 3 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of user
-- ----------------------------
INSERT INTO `user` VALUES (1, '1', '1', '1', NULL, '2023-08-02 09:14:18', 1, 1, 0);
INSERT INTO `user` VALUES (2, '2', '2', '2', NULL, '2023-09-04 22:28:58', 2, 2, 0);
INSERT INTO `user` VALUES (3, '3', '3', '3', NULL, '2023-09-07 10:42:34', 3, 3, 0);
INSERT INTO `user` VALUES (4, '4', '4', '4', NULL, '2023-09-20 10:42:45', 4, 4, 0);
INSERT INTO `user` VALUES (5, '5', '5', '5', NULL, '2023-09-07 10:43:02', 5, 5, 0);
INSERT INTO `user` VALUES (6, '6', '6', '6', NULL, '2023-09-07 18:42:04', 6, 6, 0);
INSERT INTO `user` VALUES (7, '7', '7', '7', NULL, '2023-09-07 18:42:24', 7, 7, 0);
INSERT INTO `user` VALUES (8, '8', '8', '8', NULL, '2023-09-07 18:42:51', 8, 8, 0);
INSERT INTO `user` VALUES (9, '9', '9', '9', NULL, '2023-09-07 18:43:11', 9, 9, 0);
INSERT INTO `user` VALUES (10, '10', '10', '10', NULL, '2023-09-07 18:43:36', 10, 10, 0);

SET FOREIGN_KEY_CHECKS = 1;

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

 Date: 07/09/2023 19:57:14
*/

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ----------------------------
-- Table structure for project
-- ----------------------------
DROP TABLE IF EXISTS `project`;
CREATE TABLE `project`  (
  `id` int(0) NOT NULL AUTO_INCREMENT,
  `name` varchar(64) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `type` varchar(64) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `tag` varchar(64) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `img_id` int(0) NOT NULL,
  `active` int(0) NOT NULL,
  `create_dt` datetime(0) NOT NULL,
  `has_delete` int(0) NOT NULL,
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `ix_project_id`(`id`) USING BTREE,
  INDEX `ix_project_tag`(`tag`) USING BTREE,
  INDEX `ix_project_type_tag`(`type`, `tag`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 14 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of project
-- ----------------------------
INSERT INTO `project` VALUES (12, '数据结构和算法', '课程', '105', 1, 2, '2023-09-05 15:08:54', 0);
INSERT INTO `project` VALUES (13, '数据结构和', '课程', '1,2,3,学习', 1, 0, '2023-09-05 15:19:15', 0);
INSERT INTO `project` VALUES (14, '数据结构和算法', '课程', '105', 1, 2, '2023-09-05 15:26:33', 1);
INSERT INTO `project` VALUES (15, '数据结构1', '课程', '1,2,3,学习', 1, 0, '2023-09-07 10:25:15', 0);
INSERT INTO `project` VALUES (16, '数据结构1', '课程', '1,2,3,学习', 1, 0, '2023-09-07 10:25:59', 0);

SET FOREIGN_KEY_CHECKS = 1;

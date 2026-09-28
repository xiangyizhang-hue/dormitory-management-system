CREATE DATABASE IF NOT EXISTS dorm_manage_system DEFAULT CHARACTER SET utf8mb4;
USE dorm_manage_system;

CREATE TABLE IF NOT EXISTS student (
    stu_id VARCHAR(20) PRIMARY KEY,
    stu_name VARCHAR(50) NOT NULL,
    gender CHAR(2) NOT NULL,
    department VARCHAR(50) NOT NULL,
    grade VARCHAR(10) NOT NULL,
    major VARCHAR(50) NOT NULL,
    phone VARCHAR(20) DEFAULT NULL
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS dormitory (
    dorm_id VARCHAR(20) PRIMARY KEY,
    building VARCHAR(10) NOT NULL,
    floor INT NOT NULL,
    bed_count INT NOT NULL DEFAULT 4,
    empty_bed INT NOT NULL DEFAULT 4,
    CONSTRAINT chk_bed_count CHECK (bed_count > 0),
    CONSTRAINT chk_empty_bed CHECK (empty_bed BETWEEN 0 AND bed_count)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS dorm_allocation (
    id INT AUTO_INCREMENT PRIMARY KEY,
    stu_id VARCHAR(20) NOT NULL,
    dorm_id VARCHAR(20) NOT NULL,
    check_in_date DATE NOT NULL,
    CONSTRAINT uq_allocation_student UNIQUE (stu_id),
    CONSTRAINT fk_allocation_student FOREIGN KEY (stu_id) REFERENCES student(stu_id),
    CONSTRAINT fk_allocation_dorm FOREIGN KEY (dorm_id) REFERENCES dormitory(dorm_id),
    INDEX idx_allocation_dorm (dorm_id)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS repair (
    repair_id INT AUTO_INCREMENT PRIMARY KEY,
    stu_id VARCHAR(20) NOT NULL,
    dorm_id VARCHAR(20) NOT NULL,
    repair_content VARCHAR(200) NOT NULL,
    repair_status ENUM('待处理', '维修中', '已完成') NOT NULL DEFAULT '待处理',
    create_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_repair_student FOREIGN KEY (stu_id) REFERENCES student(stu_id),
    CONSTRAINT fk_repair_dorm FOREIGN KEY (dorm_id) REFERENCES dormitory(dorm_id),
    INDEX idx_repair_status (repair_status)
) ENGINE=InnoDB;

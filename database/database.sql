CREATE TABLE book (
    id INT NOT NULL AUTO_INCREMENT,
    baslik VARCHAR(150) NOT NULL,
    yazar VARCHAR(150) NOT NULL,
    mevcut INT DEFAULT 0,
    image_url VARCHAR(200),
    detay VARCHAR(400),
    kategori_id INT,
    
    PRIMARY KEY (id),
    INDEX idx_kategori (kategori_id)
);

CREATE TABLE borrow (
    id INT NOT NULL AUTO_INCREMENT,
    user_id INT,
    book_id INT,
    alis_tarihi DATETIME,
    iade_tarihi DATETIME,
    gercek_iade_tarihi DATETIME,
    ceza FLOAT DEFAULT 0,
    durum VARCHAR(20),
    last_penalty_date DATE,
    gecikme_gun INT DEFAULT 0,
    PRIMARY KEY (id)
);

CREATE TABLE category (
    id INT AUTO_INCREMENT PRIMARY KEY,
    isim VARCHAR(50) NOT NULL
);

CREATE TABLE yazar (
    id INT NOT NULL AUTO_INCREMENT,
    isim VARCHAR(50) NOT NULL,
    PRIMARY KEY (id)
);

CREATE TABLE user (
    id INT NOT NULL AUTO_INCREMENT,
    isim VARCHAR(50) NOT NULL,
    email VARCHAR(100) NOT NULL,
    parola VARCHAR(300) NOT NULL,
    rol VARCHAR(50) NOT NULL DEFAULT 'kullanici',
    giris_tarihi DATETIME,

    PRIMARY KEY (id),
    UNIQUE KEY uq_user_email (email)
);

CREATE TABLE email_queue (
    id INT NOT NULL AUTO_INCREMENT,
    user_id INT,
    subjectt VARCHAR(255) NOT NULL,
    body TEXT NOT NULL,
    sent TINYINT(1) DEFAULT 0,
    create_at DATETIME,
    recipient_email VARCHAR(120),

    PRIMARY KEY (id),

    CONSTRAINT fk_email_user
        FOREIGN KEY (user_id)
        REFERENCES user(id)
        ON DELETE SET NULL
        ON UPDATE CASCADE
);


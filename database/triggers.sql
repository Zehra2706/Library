--CEZA 100’Ü GEÇERSE BORROW ENGELLE
DELIMITER $$

CREATE TRIGGER trg_block_borrow_if_penalty
BEFORE INSERT ON borrow
FOR EACH ROW
BEGIN
    DECLARE toplam_ceza INT;

    SELECT IFNULL(SUM(ceza), 0)
    INTO toplam_ceza
    FROM borrow
    WHERE user_id = NEW.user_id
      AND durum <> 'iade_edildi';

    IF toplam_ceza >= 100 THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Toplam cezanız 100 TL ve üzeri. Ödünç alamazsınız.';
    END IF;
END$$

DELIMITER ;

--AYNI ANDA 5 AKTİF KİTAP SINIRI
DELIMITER $$

CREATE TRIGGER trg_block_if_5_active_books
BEFORE INSERT ON borrow
FOR EACH ROW
BEGIN
    DECLARE aktif_sayi INT;

    SELECT COUNT(*)
    INTO aktif_sayi
    FROM borrow
    WHERE user_id = NEW.user_id
      AND durum = 'onaylandı';

    IF aktif_sayi >= 5 THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Aynı anda en fazla 5 kitap alabilirsiniz.';
    END IF;
END$$

DELIMITER ;

--KİTAP İADE EDİLİNCE GECİKME GÜNÜ SIFIRLA
DELIMITER $$

CREATE TRIGGER trg_reset_gecikme
BEFORE UPDATE ON borrow
FOR EACH ROW
BEGIN
    IF NEW.durum = 'iade_edildi' THEN
        SET NEW.gecikme_gun = 0;
    END IF;
END$$

DELIMITER ;

--BORROW ONAYLANINCA STOK AZALT
DELIMITER $$

CREATE TRIGGER trg_borrow_after_insert
AFTER UPDATE ON borrow
FOR EACH ROW
BEGIN
    IF OLD.durum <> NEW.durum AND NEW.durum = 'onaylandı' THEN
        UPDATE book
        SET mevcut = CASE
            WHEN mevcut > 0 THEN mevcut - 1
            ELSE 0
        END
        WHERE id = NEW.book_id;
    END IF;
END$$

DELIMITER ;

--KİTAP İADE EDİLİNCE STOK ARTTIR
DELIMITER $$

CREATE TRIGGER trg_increase_stock_on_return
AFTER UPDATE ON borrow
FOR EACH ROW
BEGIN
    IF NEW.durum = 'iade_edildi'
       AND OLD.durum <> 'iade_edildi' THEN

        UPDATE book
        SET mevcut = mevcut + 1
        WHERE id = NEW.book_id;

    END IF;
END$$

DELIMITER ;

--KİTAP ONAYLANINCA MAİL KUYRUKLA
DELIMITER $$

CREATE TRIGGER BorrowedBookTrigger
AFTER UPDATE ON borrow
FOR EACH ROW
BEGIN
    DECLARE mail VARCHAR(255);
    DECLARE kitap_baslik VARCHAR(150);

    IF OLD.durum <> NEW.durum AND NEW.durum = 'onaylandı' THEN

        SELECT email INTO mail
        FROM user
        WHERE id = NEW.user_id;

        SELECT baslik INTO kitap_baslik
        FROM book
        WHERE id = NEW.book_id;

        INSERT INTO email_queue (
            user_id, subjectt, body, sent, create_at, recipient_email
        )
        VALUES (
            NEW.user_id,
            'Kitap Ödünç Alındı',
            CONCAT('Ödünç aldığınız kitap: ', kitap_baslik),
            0,
            NOW(),
            mail
        );
    END IF;
END$$

DELIMITER ;

--KİTAP İADE EDİLİNCE MAİL
DELIMITER $$

CREATE TRIGGER ReturnBookTrigger
AFTER UPDATE ON borrow
FOR EACH ROW
BEGIN
    DECLARE mail VARCHAR(255);
    DECLARE kitap_baslik VARCHAR(150);

    IF OLD.durum <> 'iade_edildi'
       AND NEW.durum = 'iade_edildi' THEN

        SELECT email INTO mail
        FROM user
        WHERE id = NEW.user_id;

        SELECT baslik INTO kitap_baslik
        FROM book
        WHERE id = NEW.book_id;

        INSERT INTO email_queue (
            user_id, subjectt, body, sent, create_at, recipient_email
        )
        VALUES (
            NEW.user_id,
            'Kitap İade Edildi',
            CONCAT('İade edilen kitap: ', kitap_baslik),
            0,
            NOW(),
            mail
        );
    END IF;
END$$

DELIMITER ;

--CEZA ARTTIĞINDA MAİL GÖNDER
DELIMITER $$

CREATE TRIGGER trg_borrow_penalty_mail
AFTER UPDATE ON borrow
FOR EACH ROW
BEGIN
    DECLARE mail_body TEXT;

    SET mail_body = '';

    IF NEW.ceza > OLD.ceza THEN
        SET mail_body = CONCAT(
            'Kitabın iade süresi geçmiştir.', CHAR(10),
            'Toplam cezanız: ', NEW.ceza, ' TL'
        );

        INSERT INTO email_queue (
            user_id, subjectt, body, sent, create_at, recipient_email
        )
        VALUES (
            NEW.user_id,
            'Gecikme Cezası',
            mail_body,
            0,
            NOW(),
            (SELECT email FROM user WHERE id = NEW.user_id)
        );
    END IF;
END$$

DELIMITER ;

--KULLANICI KAYIT OLUNCA HOŞGELDİN MAİLİ
DELIMITER $$

CREATE TRIGGER trg_user_after_insert
AFTER INSERT ON user
FOR EACH ROW
BEGIN
    INSERT INTO email_queue (
        user_id, subjectt, body, sent, create_at, recipient_email
    )
    VALUES (
        NEW.id,
        'Hoşgeldiniz',
        CONCAT('Merhaba ', NEW.isim, ', hesabınız başarıyla oluşturuldu.'),
        0,
        NOW(),
        NEW.email
    );
END$$

DELIMITER ;

--KULLANICI SİLİNCE BİLGİ MAİLİ
DELIMITER $$

CREATE TRIGGER trg_user_after_delete
BEFORE DELETE ON user
FOR EACH ROW
BEGIN
    INSERT INTO email_queue (
        user_id, subjectt, body, sent, create_at, recipient_email
    )
    VALUES (
        OLD.id,
        'Hesap Silindi',
        CONCAT('Merhaba ', OLD.isim, ', hesabınız sistemden silindi.'),
        0,
        NOW(),
        OLD.email
    );
END$$

DELIMITER ;

--CEZA ÖDENDİĞİNDE MAİL EKLEYEN 
DELIMITER $$

CREATE TRIGGER trg_user_total_ceza_zero_mail
AFTER UPDATE ON borrow
FOR EACH ROW
BEGIN
    DECLARE total_ceza DECIMAL(10,2);

    -- sadece ceza 0'a düştüyse kontrol et
    IF OLD.ceza > 0 AND NEW.ceza = 0 THEN

        -- kullanıcının kalan toplam cezası
        SELECT IFNULL(SUM(ceza), 0)
        INTO total_ceza
        FROM borrow
        WHERE user_id = NEW.user_id;

        -- toplam ceza 0 ise mail kuyruğuna ekle
        IF total_ceza = 0 THEN

            INSERT INTO email_queue (
                user_id,
                subjectt,
                body,
                sent,
                create_at,
                recipient_email
            )
            SELECT
                u.id,
                'Kütüphane Ceza Bilgilendirmesi',
                CONCAT(
                    'Merhaba ', u.isim, ',\n\n',
                    'Kütüphaneye olan tüm borçlarınız kapatılmıştır.\n',
                    'Mevcut toplam cezanız: 0 TL.\n\n',
                    'İyi günler dileriz.'
                ),
                0,
                NOW(),
                u.email
            FROM user u
            WHERE u.id = NEW.user_id;

        END IF;
    END IF;
END$$

DELIMITER ;

--Bir kitabın aktif ödünçlerini kontrol eder.
DELIMITER $$

CREATE TRIGGER trg_block_book_delete_if_active_borrow
BEFORE DELETE ON book
FOR EACH ROW
BEGIN
    DECLARE aktif_sayi INT;

    SELECT COUNT(*)
    INTO aktif_sayi
    FROM borrow
    WHERE book_id = OLD.id
      AND durum = 'onaylandı';

    IF aktif_sayi > 0 THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Bu kitap şu anda ödünçte. Silinemez.';
    END IF;
END$$

DELIMITER ;
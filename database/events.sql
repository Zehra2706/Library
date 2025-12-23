--İlk gecikmede ceza başlatır (dakikalık kontrol).
DELIMITER $$

CREATE EVENT ev_check_first_delay
ON SCHEDULE EVERY 1 MINUTE
STARTS CURRENT_TIMESTAMP
DO
BEGIN
    UPDATE borrow
    SET 
        ceza = 10,
        last_penalty_date = CURRENT_DATE
    WHERE
        durum = 'onaylandı'
        AND ceza = 0
        AND CURRENT_TIMESTAMP > iade_tarihi;
END$$

DELIMITER ;

--Her gün geciken ödünçlere günlük ceza ekler.
DELIMITER $$
CREATE EVENT ev_daily_penalty
ON SCHEDULE EVERY 1 DAY
STARTS CURRENT_DATE + INTERVAL 1 DAY
DO
BEGIN
    UPDATE borrow
    SET 
        ceza = ceza + 10,
        last_penalty_date = CURRENT_DATE
    WHERE
        durum = 'onaylandı'
        AND CURRENT_TIMESTAMP > iade_tarihi
        AND (
            last_penalty_date IS NULL
            OR last_penalty_date < CURRENT_DATE
        );
END$$
DELIMITER ;

--Gecikme gün sayısını her gün günceller.
DELIMITER $$

CREATE EVENT ev_update_gecikme_gun
ON SCHEDULE EVERY 1 DAY
STARTS CURRENT_DATE
DO
BEGIN
    UPDATE borrow
    SET gecikme_gun = DATEDIFF(CURRENT_DATE, DATE(iade_tarihi))
    WHERE
        durum = 'onaylandı'
        AND CURRENT_DATE > DATE(iade_tarihi);
END$$

DELIMITER ;

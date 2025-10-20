DROP VIEW IF EXISTS pizza_menu_prices;
DROP VIEW IF EXISTS staff_undelivered_orders;
DROP VIEW IF EXISTS staff_top_pizzas_last_month;
DROP VIEW IF EXISTS staff_monthly_earnings_by_gender;
DROP VIEW IF EXISTS staff_monthly_earnings_by_age_group;
DROP VIEW IF EXISTS staff_monthly_earnings_by_postcode;

CREATE VIEW pizza_menu_prices AS
SELECT
  p.pizza_id                                   AS pizza_id,
  p.pizza_name                                 AS pizza_name,
  ROUND(SUM(i.cost) * 1.4 * 1.09, 2)           AS calculated_price,
  CASE
    WHEN MIN(CASE WHEN i.is_meat = 0 AND i.is_dairy = 0 THEN 1 ELSE 0 END) = 1 THEN 1
    ELSE 0
  END                                          AS pizza_isvegan,
  CASE
    WHEN MIN(CASE WHEN i.is_meat = 0 THEN 1 ELSE 0 END) = 1 THEN 1
    ELSE 0
  END                                          AS pizza_isvegetarian
FROM pizzas p
JOIN pizza_ingredients pi ON pi.pizza_id = p.pizza_id
JOIN ingredients i        ON i.ingredient_id = pi.ingredient_id
GROUP BY p.pizza_id, p.pizza_name;

CREATE VIEW staff_undelivered_orders AS
SELECT
  o.Order_ID                                                   AS order_id,
  o.Order_Status                                               AS order_status,
  o.Placed_At                                                  AS placed_at,
  TIMESTAMPDIFF(MINUTE, o.Placed_At, UTC_TIMESTAMP())          AS minutes_since_placed,
  c.Customer_ID                                                AS customer_id,
  c.Name                                                       AS customer_name,
  c.Email_Address                                              AS customer_email,
  pc.postcode                                                  AS delivery_postcode,
  dp.DeliveryDriver_ID                                         AS driver_id,
  dp.DeliveryDriver_Name                                       AS driver_name,
  COUNT(oi.OrderItem_ID)                                       AS item_count,
  ROUND(SUM((oi.Unit_Price * oi.Quantity) - oi.Discount_Amount), 2) AS order_value
FROM orders o
JOIN customers c             ON c.Customer_ID = o.Customer_ID
LEFT JOIN postcode pc        ON pc.postcode_id = o.Delivery_Postcode_ID
LEFT JOIN delivery_person dp ON dp.DeliveryDriver_ID = o.DeliveryDriver_ID
JOIN order_items oi          ON oi.Order_ID = o.Order_ID
WHERE o.Order_Status NOT IN ('delivered', 'failed')
GROUP BY
  o.Order_ID,
  o.Order_Status,
  o.Placed_At,
  c.Customer_ID,
  c.Name,
  c.Email_Address,
  pc.postcode,
  dp.DeliveryDriver_ID,
  dp.DeliveryDriver_Name
ORDER BY o.Placed_At ASC;

CREATE VIEW staff_top_pizzas_last_month AS
SELECT
  oi.Pizza_ID AS pizza_id,
  p.pizza_name,
  SUM(oi.Quantity) AS total_quantity,
  SUM((oi.Unit_Price * oi.Quantity) - oi.Discount_Amount) AS pizza_revenue
FROM orders o
JOIN order_items oi ON oi.Order_ID = o.Order_ID
JOIN pizzas p       ON p.pizza_id = oi.Pizza_ID
WHERE
  oi.Item_Type = 'pizza'
  AND o.Order_Status <> 'failed'
  AND o.Placed_At >= DATE_SUB(UTC_TIMESTAMP(), INTERVAL 1 MONTH)
GROUP BY
  oi.Pizza_ID,
  p.pizza_name;

CREATE VIEW staff_monthly_earnings_by_gender AS
SELECT
  YEAR(o.Placed_At) AS report_year,
  MONTH(o.Placed_At) AS report_month,
  COALESCE(NULLIF(TRIM(c.Gender), ''), 'Unknown') AS gender,
  COUNT(DISTINCT o.Order_ID) AS order_count,
  ROUND(SUM((oi.Unit_Price * oi.Quantity) - oi.Discount_Amount), 2) AS revenue
FROM orders o
JOIN customers c    ON c.Customer_ID = o.Customer_ID
JOIN order_items oi ON oi.Order_ID = o.Order_ID
WHERE o.Order_Status <> 'failed'
GROUP BY
  YEAR(o.Placed_At),
  MONTH(o.Placed_At),
  COALESCE(NULLIF(TRIM(c.Gender), ''), 'Unknown');

CREATE VIEW staff_monthly_earnings_by_age_group AS
SELECT
  YEAR(o.Placed_At) AS report_year,
  MONTH(o.Placed_At) AS report_month,
  CASE
    WHEN c.Birthdate IS NULL THEN 'Unknown'
    WHEN TIMESTAMPDIFF(YEAR, c.Birthdate, o.Placed_At) < 25 THEN '18-24'
    WHEN TIMESTAMPDIFF(YEAR, c.Birthdate, o.Placed_At) BETWEEN 25 AND 34 THEN '25-34'
    WHEN TIMESTAMPDIFF(YEAR, c.Birthdate, o.Placed_At) BETWEEN 35 AND 44 THEN '35-44'
    WHEN TIMESTAMPDIFF(YEAR, c.Birthdate, o.Placed_At) BETWEEN 45 AND 54 THEN '45-54'
    ELSE '55+'
  END AS age_group,
  COUNT(DISTINCT o.Order_ID) AS order_count,
  ROUND(SUM((oi.Unit_Price * oi.Quantity) - oi.Discount_Amount), 2) AS revenue
FROM orders o
JOIN customers c    ON c.Customer_ID = o.Customer_ID
JOIN order_items oi ON oi.Order_ID = o.Order_ID
WHERE o.Order_Status <> 'failed'
GROUP BY
  YEAR(o.Placed_At),
  MONTH(o.Placed_At),
  age_group;

CREATE VIEW staff_monthly_earnings_by_postcode AS
SELECT
  YEAR(o.Placed_At) AS report_year,
  MONTH(o.Placed_At) AS report_month,
  pc.postcode       AS postcode,
  COUNT(DISTINCT o.Order_ID) AS order_count,
  ROUND(SUM((oi.Unit_Price * oi.Quantity) - oi.Discount_Amount), 2) AS revenue
FROM orders o
LEFT JOIN postcode pc ON pc.postcode_id = o.Delivery_Postcode_ID
JOIN order_items oi   ON oi.Order_ID = o.Order_ID
WHERE o.Order_Status <> 'failed'
GROUP BY
  YEAR(o.Placed_At),
  MONTH(o.Placed_At),
  pc.postcode;

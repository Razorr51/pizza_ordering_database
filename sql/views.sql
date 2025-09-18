CREATE OR REPLACE VIEW pizza_menu_prices AS
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

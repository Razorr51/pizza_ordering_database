-- Use your actual (singular) table names
DROP VIEW IF EXISTS pizza_menu_view;

CREATE VIEW pizza_menu_view AS
SELECT
  p.id   AS pizza_id,
  p.name AS pizza_name,
  ROUND(SUM(i.cost), 2)               AS base_cost,
  ROUND(SUM(i.cost) * 1.40 * 1.09, 2) AS final_price,  -- 40% margin + 9% VAT
  CASE
    WHEN MIN(i.is_vegan) = 1 THEN 'vegan'
    WHEN MIN(i.is_vegetarian) = 1 THEN 'vegetarian'
    ELSE 'contains meat'
  END AS veg_label
FROM pizza p
JOIN pizza_ingredient pi ON pi.pizza_id = p.id
JOIN ingredient i        ON i.id        = pi.ingredient_id
GROUP BY p.id, p.name;

-- Optional: keep your old name working as an alias
DROP VIEW IF EXISTS pizza_menu_prices;
CREATE VIEW pizza_menu_prices AS
SELECT * FROM pizza_menu_view;

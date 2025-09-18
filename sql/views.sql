

DROP VIEW IF EXISTS pizza_menu_view;

CREATE VIEW pizza_menu_view AS
SELECT
  p.id AS pizza_id,
  p.name AS pizza_name,
  ROUND(SUM(i.cost), 2) AS base_cost,
  ROUND(SUM(i.cost) * 1.4 * 1.09, 2) AS final_price,
  CASE
    WHEN MIN(CASE WHEN i.is_vegan = 1 THEN 1 ELSE 0 END) = 1 THEN 'vegan'
    WHEN MIN(CASE WHEN i.is_vegetarian = 1 THEN 1 ELSE 0 END) = 1 THEN 'vegetarian'
    ELSE 'contains meat'
  END AS veg_label
FROM pizza p
JOIN pizza_ingredient pi ON pi.pizza_id = p.id
JOIN ingredient i ON i.id = pi.ingredient_id
GROUP BY p.id, p.name;

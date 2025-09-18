
INSERT IGNORE INTO ingredients (ingredient_id, name, cost, is_meat, is_dairy, is_vegan) VALUES
  (1,'Tomato sauce', 0.30, 0, 0, 1),
  (2,'Mozzarella',    0.80, 0, 1, 0),
  (3,'Basil',         0.10, 0, 0, 1),
  (4,'Pepperoni',     0.90, 1, 0, 0);


INSERT IGNORE INTO pizzas (pizza_name) VALUES
  ('Margherita'),
  ('Pepperoni');


-- Margherita links
INSERT IGNORE INTO pizza_ingredients (pizza_id, ingredient_id)
SELECT p.pizza_id, i.ingredient_id
FROM pizzas p JOIN ingredients i
WHERE p.pizza_name = 'Margherita' AND i.name = 'Tomato sauce';

INSERT IGNORE INTO pizza_ingredients (pizza_id, ingredient_id)
SELECT p.pizza_id, i.ingredient_id
FROM pizzas p JOIN ingredients i
WHERE p.pizza_name = 'Margherita' AND i.name = 'Mozzarella';

INSERT IGNORE INTO pizza_ingredients (pizza_id, ingredient_id)
SELECT p.pizza_id, i.ingredient_id
FROM pizzas p JOIN ingredients i
WHERE p.pizza_name = 'Margherita' AND i.name = 'Basil';

-- Pepperoni links
INSERT IGNORE INTO pizza_ingredients (pizza_id, ingredient_id)
SELECT p.pizza_id, i.ingredient_id
FROM pizzas p JOIN ingredients i
WHERE p.pizza_name = 'Pepperoni' AND i.name = 'Tomato sauce';

INSERT IGNORE INTO pizza_ingredients (pizza_id, ingredient_id)
SELECT p.pizza_id, i.ingredient_id
FROM pizzas p JOIN ingredients i
WHERE p.pizza_name = 'Pepperoni' AND i.name = 'Mozzarella';

INSERT IGNORE INTO pizza_ingredients (pizza_id, ingredient_id)
SELECT p.pizza_id, i.ingredient_id
FROM pizzas p JOIN ingredients i
WHERE p.pizza_name = 'Pepperoni' AND i.name = 'Pepperoni';

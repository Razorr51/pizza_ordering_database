-- Insert pizzas
INSERT IGNORE INTO pizzas (pizza_id, pizza_name) VALUES
  (1,'Margherita'),
  (2,'Pepperoni'),
  (3,'Italian'),
  (4,'Vegetarian'),
  (5,'Diavola'),
  (6,'Hawaiian'),
  (7,'Special'),
  (8,'BBQ Chicken'),
  (9,'Hot honey pepperoni'),
  (10,'Cheese');

-- Link Margherita
INSERT IGNORE INTO pizza_ingredients (pizza_id, ingredient_id, quantity, quantity_unit)
SELECT p.pizza_id, i.ingredient_id, 1, 'portion'
FROM pizzas p JOIN ingredients i
WHERE p.pizza_name = 'Margherita'
  AND i.name IN ('Tomato sauce','Mozzarella','Basil');

-- Link Pepperoni
INSERT IGNORE INTO pizza_ingredients (pizza_id, ingredient_id, quantity, quantity_unit)
SELECT p.pizza_id, i.ingredient_id, 1, 'portion'
FROM pizzas p JOIN ingredients i
WHERE p.pizza_name = 'Pepperoni'
  AND i.name IN ('Tomato sauce','Mozzarella','Pepperoni');

-- Link Italian
INSERT IGNORE INTO pizza_ingredients (pizza_id, ingredient_id, quantity, quantity_unit)
SELECT p.pizza_id, i.ingredient_id, 1, 'portion'
FROM pizzas p JOIN ingredients i
WHERE p.pizza_name = 'Italian'
  AND i.name IN ('Tomato sauce','Mozzarella','Prosciutto','Pineapple');

-- Link Vegetarian
INSERT IGNORE INTO pizza_ingredients (pizza_id, ingredient_id, quantity, quantity_unit)
SELECT p.pizza_id, i.ingredient_id, 1, 'portion'
FROM pizzas p JOIN ingredients i
WHERE p.pizza_name = 'Vegetarian'
  AND i.name IN ('Tomato sauce','Vegan cheese','Basil','Onions','Olives','Peppers');

-- Link Diavola
INSERT IGNORE INTO pizza_ingredients (pizza_id, ingredient_id, quantity, quantity_unit)
SELECT p.pizza_id, i.ingredient_id, 1, 'portion'
FROM pizzas p JOIN ingredients i
WHERE p.pizza_name = 'Diavola'
  AND i.name IN ('Tomato sauce','Mozzarella','Pepperoni','Onions','Jalapenos');

-- Link Hawaiian
INSERT IGNORE INTO pizza_ingredients (pizza_id, ingredient_id, quantity, quantity_unit)
SELECT p.pizza_id, i.ingredient_id, 1, 'portion'
FROM pizzas p JOIN ingredients i
WHERE p.pizza_name = 'Hawaiian'
  AND i.name IN ('Tomato sauce','Mozzarella','Pineapple','Bacon');

-- Link Special
INSERT IGNORE INTO pizza_ingredients (pizza_id, ingredient_id, quantity, quantity_unit)
SELECT p.pizza_id, i.ingredient_id, 1, 'portion'
FROM pizzas p JOIN ingredients i
WHERE p.pizza_name = 'Special'
  AND i.name IN ('Tomato sauce','Mozzarella','Basil','Mushrooms','Bacon');

-- Link BBQ Chicken
INSERT IGNORE INTO pizza_ingredients (pizza_id, ingredient_id, quantity, quantity_unit)
SELECT p.pizza_id, i.ingredient_id, 1, 'portion'
FROM pizzas p JOIN ingredients i
WHERE p.pizza_name = 'BBQ Chicken'
  AND i.name IN ('BBQ Sauce','Mozzarella','Chicken','Bacon');

-- Link Hot honey pepperoni
INSERT IGNORE INTO pizza_ingredients (pizza_id, ingredient_id, quantity, quantity_unit)
SELECT p.pizza_id, i.ingredient_id, 1, 'portion'
FROM pizzas p JOIN ingredients i
WHERE p.pizza_name = 'Hot honey pepperoni'
  AND i.name IN ('Tomato sauce','Mozzarella','Pepperoni','Hot honey');

-- Link Cheese
INSERT IGNORE INTO pizza_ingredients (pizza_id, ingredient_id, quantity, quantity_unit)
SELECT p.pizza_id, i.ingredient_id, 1, 'portion'
FROM pizzas p JOIN ingredients i
WHERE p.pizza_name = 'Cheese'
  AND i.name IN ('Tomato sauce','Mozzarella','Cheddar');

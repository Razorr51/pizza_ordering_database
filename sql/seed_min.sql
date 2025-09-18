
INSERT IGNORE INTO ingredient (name, cost, is_vegan, is_vegetarian) VALUES
  ('Tomato sauce', 0.30, 1, 1),
  ('Mozzarella',    0.80, 0, 1),
  ('Basil',         0.10, 1, 1),
  ('Pepperoni',     0.90, 0, 0);

INSERT IGNORE INTO pizza (name) VALUES
  ('Margherita'),
  ('Pepperoni');


INSERT IGNORE INTO pizza_ingredient (pizza_id, ingredient_id)
SELECT p.id, i.id FROM pizza p JOIN ingredient i
  ON p.name = 'Margherita' AND i.name = 'Tomato sauce';
INSERT IGNORE INTO pizza_ingredient (pizza_id, ingredient_id)
SELECT p.id, i.id FROM pizza p JOIN ingredient i
  ON p.name = 'Margherita' AND i.name = 'Mozzarella';
INSERT IGNORE INTO pizza_ingredient (pizza_id, ingredient_id)
SELECT p.id, i.id FROM pizza p JOIN ingredient i
  ON p.name = 'Margherita' AND i.name = 'Basil';

INSERT IGNORE INTO pizza_ingredient (pizza_id, ingredient_id)
SELECT p.id, i.id FROM pizza p JOIN ingredient i
  ON p.name = 'Pepperoni' AND i.name = 'Tomato sauce';
INSERT IGNORE INTO pizza_ingredient (pizza_id, ingredient_id)
SELECT p.id, i.id FROM pizza p JOIN ingredient i
  ON p.name = 'Pepperoni' AND i.name = 'Mozzarella';
INSERT IGNORE INTO pizza_ingredient (pizza_id, ingredient_id)
SELECT p.id, i.id FROM pizza p JOIN ingredient i
  ON p.name = 'Pepperoni' AND i.name = 'Pepperoni';

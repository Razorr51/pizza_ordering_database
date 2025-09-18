
INSERT IGNORE INTO ingredients (ingredient_id, name, cost, is_meat, is_dairy, is_vegan) VALUES
  (1,'Tomato sauce', 0.30, 0, 0, 1),
  (2,'Mozzarella',    0.80, 0, 1, 0),
  (3,'Basil',         0.10, 0, 0, 1),
  (4,'Pepperoni',     0.90, 1, 0, 0),
  (5,'Peppers',0.50,0, 1,1),
  (6, 'Vegan cheese', 1.00,0,0,1),
  (7,'Mushrooms', 0.4, 0,1,1),
  (8,'Onions', 0.3, 0,0,1),
  (9,'Olives',0.7,0,0,1),
  (10,'Pineapple',0,0.5,0,1),
  (11,'Prosciutto', 0.90, 1,0,0),
  (12,'Bacon', 0.8,1,0,0),
  (13,'Jalapenos', 0.6,0,0,1),
  (14,'Chicken', 1.50, 1,0,0),
  (15, 'BBQ Sauce', 0.4, 0 ,0, 1),
  (16, 'Hot honey', 0.2, 0 ,0,1),
  (17, 'Cheddar', 0.7, 0,1,0);


INSERT IGNORE INTO pizzas (pizza_name) VALUES
  ('Margherita'),
  ('Pepperoni'),
  ('Italian'),
  ( 'Vegetarian'),
  ('Diavola'),
  ('Hawaiian'),
  ('Special'),
  ('BBQ Chicken'),
  ('Hot honey pepperoni'),
  ('Cheese')

;



-- Margherita links
INSERT IGNORE INTO pizza_ingredients (pizza_id, ingredient_id)
SELECT p.pizza_id, i.ingredient_id
FROM pizzas p JOIN ingredients i
WHERE p.pizza_name = 'Margherita' AND i.name IN( 'Tomato sauce', 'Mozzarella', 'Basil');


-- Pepperoni links
INSERT IGNORE INTO pizza_ingredients (pizza_id, ingredient_id)
SELECT p.pizza_id, i.ingredient_id
FROM pizzas p JOIN ingredients i
WHERE p.pizza_name = 'Pepperoni' AND i.name IN ('Tomato sauce','Mozzarella', 'Pepperoni');
-- Italian links
INSERT IGNORE INTO pizza_ingredients (pizza_id, ingredient_id)
SELECT p.pizza_id, i.ingredient_id
FROM pizzas p JOIN ingredients i
WHERE p.pizza_name = 'Italian' AND i.name IN( 'Tomato sauce', 'Mozzarella', 'Prosciutto','Pineapple');
-- Vegeterian links
INSERT IGNORE INTO pizza_ingredients (pizza_id, ingredient_id)
SELECT p.pizza_id, i.ingredient_id
FROM pizzas p JOIN ingredients i
WHERE p.pizza_name = 'Vegetarian' AND i.name IN( 'Tomato sauce', 'Vegan cheese', 'Basil', 'Onions', 'Olives', 'Peppers');
-- Special links
INSERT IGNORE INTO pizza_ingredients (pizza_id, ingredient_id)
SELECT p.pizza_id, i.ingredient_id
FROM pizzas p JOIN ingredients i
WHERE p.pizza_name = 'Special' AND i.name IN( 'Tomato sauce', 'Mozzarella', 'Basil', 'Mushrooms','Bacon');
-- Diavola links
INSERT IGNORE INTO pizza_ingredients (pizza_id, ingredient_id)
SELECT p.pizza_id, i.ingredient_id
FROM pizzas p JOIN ingredients i
WHERE p.pizza_name = 'Diavola' AND i.name IN( 'Tomato sauce', 'Mozzarella', 'Pepperoni', 'Onions','Jalapenos');
-- Hawaiian links
INSERT IGNORE INTO pizza_ingredients (pizza_id, ingredient_id)
SELECT p.pizza_id, i.ingredient_id
FROM pizzas p JOIN ingredients i
WHERE p.pizza_name = 'Hawaiian' AND i.name IN( 'Tomato sauce', 'Mozzarella', 'Pineapple','Bacon');
-- BBQ Chicken links
INSERT IGNORE INTO pizza_ingredients (pizza_id, ingredient_id)
SELECT p.pizza_id, i.ingredient_id
FROM pizzas p JOIN ingredients i
WHERE p.pizza_name = 'BBQ Chicken' AND i.name IN( 'BBQ Sauce', 'Mozzarella', 'Chicken','Bacon');
-- Hot honey pepperoni links
INSERT IGNORE INTO pizza_ingredients (pizza_id, ingredient_id)
SELECT p.pizza_id, i.ingredient_id
FROM pizzas p JOIN ingredients i
WHERE p.pizza_name = 'Hot honey pepperoni' AND i.name IN( 'Tomato sauce', 'Mozzarella', 'Pepperoni','Hot honey');
-- Cheese links
INSERT IGNORE INTO pizza_ingredients (pizza_id, ingredient_id)
SELECT p.pizza_id, i.ingredient_id
FROM pizzas p JOIN ingredients i
WHERE p.pizza_name = 'Cheese' AND i.name IN( 'Tomato sauce', 'Mozzarella', 'Cheddar');

-- Postcodes
INSERT IGNORE INTO postcode (postcode_id, postcode, DeliveryDriver_ID)
VALUES
  (1,'1000',NULL),(2,'1001',NULL),(3,'1002',NULL);

-- Delivery drivers
INSERT IGNORE INTO delivery_person (DeliveryDriver_ID, DeliveryDriver_Name, isAvailable)
VALUES (1,'Marco',1),(2,'Lina',1),(3,'Jakob',1);

-- Customers (link to Postcode_ID)
INSERT IGNORE INTO Customers (Customer_ID, Name, Gender, Birthdate, Postcode_ID,
  Street_Number, Email_Address, Phone_Number, Username, Password,
  canBirthDay, canDiscount, PizzasOrdered, Street_Name)
VALUES
  (1,'Alice Rossi','F','1998-05-10',1,12,'alice@example.com','+31000000001','alice','x',1,1,0,'Main St'),
  (2,'Bob Smith','M','1987-03-22',2,45,'bob@example.com','+31000000002','bob','x',1,1,0,'Side St'),
  (3,'Carla Gómez','F','1995-12-01',3,78,'carla@example.com','+31000000003','carla','x',1,1,0,'Park Ave');
INSERT IGNORE INTO menu_items (item_id, name, type, base_price, is_vegan, is_vegetarian, active, created_at)
VALUES
  (1,'Cola','drink', 2.50,1,1,1,NOW()),
  (2,'Water','drink',1.50,1,1,1,NOW()),
  (3,'Beer','drink', 3.00,1,1,1,NOW()),
  (4,'Tiramisu','dessert',4.00,0,1,1,NOW()),
  (5,'Gelato','dessert', 4.50,0,1,1,NOW()),
  (6,'ChocoPizza', 'dessert', 4.50,0,0,1,NOW() );

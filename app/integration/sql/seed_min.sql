
-- 1) INGREDIENTS
INSERT IGNORE INTO ingredients (name, cost, is_meat, is_dairy, is_vegan) VALUES
 ('Tomato sauce', 0.30, 0, 0, 1),
 ('Mozzarella',   0.80, 0, 1, 0),
 ('Basil',        0.10, 0, 0, 1),
 ('Pepperoni',    0.90, 1, 0, 0),
 ('Peppers',      0.50, 0, 0, 1),
 ('Vegan cheese', 1.00, 0, 0, 1),
 ('Mushrooms',    0.40, 0, 0, 1),
 ('Onions',       0.30, 0, 0, 1),
 ('Olives',       0.70, 0, 0, 1),
 ('Pineapple',    0.50, 0, 0, 1),
 ('Prosciutto',   0.90, 1, 0, 0),
 ('Bacon',        0.80, 1, 0, 0),
 ('Jalapenos',    0.60, 0, 0, 1),
 ('Chicken',      1.50, 1, 0, 0),
 ('BBQ Sauce',    0.40, 0, 0, 1),
 ('Hot honey',    0.20, 0, 0, 1),
 ('Cheddar',      0.70, 0, 1, 0);

-- Postcodes
INSERT IGNORE INTO postcode (postcode_id, postcode, DeliveryDriver_ID)
VALUES
    (1, '1000', NULL),
    (2, '1001', NULL),
    (3, '1002', NULL);

-- Delivery drivers
INSERT IGNORE INTO delivery_person (DeliveryDriver_ID, DeliveryDriver_Name, isAvailable)
VALUES
    (1, 'Marco', 1),
    (2, 'Lina', 1),
    (3, 'Jakob', 1);

-- Customers (link to Postcode_ID)
INSERT IGNORE INTO Customers (Customer_ID, Name, Gender, Birthdate, Postcode_ID, Street_Number, Email_Address,
Phone_Number, Username, Password, canBirthDay, canDiscount, PizzasOrdered, Street_Name) VALUES
    (1, 'Alice Rossi', 'F', '1998-05-10', 1, 12, 'alice@example.com', '+31000000001', 'alice', 'x', 1, 1, 0, 'Main St'),
    (2, 'Bob Smith',  'M', '1987-03-22', 2, 45, 'bob@example.com',   '+31000000002', 'bob',   'x', 1, 1, 0, 'Side St'),
    (3, 'Carla Gómez','F', '1995-12-01', 3, 78, 'carla@example.com', '+31000000003', 'carla', 'x', 1, 1, 0, 'Park Ave');

-- Menu items
INSERT IGNORE INTO menu_items (
    item_id,
    name,
    type,
    base_price,
    is_vegan,
    is_vegetarian,
    active,
    created_at
) VALUES
    (1, 'Cola',       'drink',   2.50, 1, 1, 1, NOW()),
    (2, 'Water',      'drink',   1.50, 1, 1, 1, NOW()),
    (3, 'Beer',       'drink',   3.00, 1, 1, 1, NOW()),
    (4, 'Tiramisu',   'dessert', 4.00, 0, 1, 1, NOW()),
    (5, 'Gelato',     'dessert', 4.50, 0, 1, 1, NOW()),
    (6, 'ChocoPizza', 'dessert', 4.50, 0, 0, 1, NOW());

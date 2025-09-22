-- Tables (singular names)
CREATE TABLE IF NOT EXISTS ingredients (
  id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(100) NOT NULL UNIQUE,
  cost DECIMAL(10,2) NOT NULL CHECK (cost > 0),
  is_vegan TINYINT(1) NOT NULL DEFAULT 0,
  is_vegetarian TINYINT(1) NOT NULL DEFAULT 0
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS pizza (
  id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(100) NOT NULL UNIQUE
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS pizza_ingredient (
  pizza_id INT NOT NULL,
  ingredient_id INT NOT NULL,
  PRIMARY KEY (pizza_id, ingredient_id),
  CONSTRAINT fk_pi_pizza      FOREIGN KEY (pizza_id)     REFERENCES pizza(id)      ON DELETE CASCADE,
  CONSTRAINT fk_pi_ingredient FOREIGN KEY (ingredient_id) REFERENCES ingredients(id) ON DELETE RESTRICT
) ENGINE=InnoDB;

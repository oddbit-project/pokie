-- Convert Northwind PKs to serial for full CRUD support

CREATE SEQUENCE IF NOT EXISTS products_product_id_seq OWNED BY products.product_id;
SELECT setval('products_product_id_seq', COALESCE((SELECT MAX(product_id) FROM products), 0) + 1, false);
ALTER TABLE products ALTER COLUMN product_id SET DEFAULT nextval('products_product_id_seq');

CREATE SEQUENCE IF NOT EXISTS suppliers_supplier_id_seq OWNED BY suppliers.supplier_id;
SELECT setval('suppliers_supplier_id_seq', COALESCE((SELECT MAX(supplier_id) FROM suppliers), 0) + 1, false);
ALTER TABLE suppliers ALTER COLUMN supplier_id SET DEFAULT nextval('suppliers_supplier_id_seq');

CREATE SEQUENCE IF NOT EXISTS categories_category_id_seq OWNED BY categories.category_id;
SELECT setval('categories_category_id_seq', COALESCE((SELECT MAX(category_id) FROM categories), 0) + 1, false);
ALTER TABLE categories ALTER COLUMN category_id SET DEFAULT nextval('categories_category_id_seq');

CREATE SEQUENCE IF NOT EXISTS shippers_shipper_id_seq OWNED BY shippers.shipper_id;
SELECT setval('shippers_shipper_id_seq', COALESCE((SELECT MAX(shipper_id) FROM shippers), 0) + 1, false);
ALTER TABLE shippers ALTER COLUMN shipper_id SET DEFAULT nextval('shippers_shipper_id_seq');

create database if not exists bosch;
use bosch;


DROP TABLE IF EXISTS employees;
DROP TABLE IF EXISTS sales;
DROP TABLE IF EXISTS orders;
DROP TABLE IF EXISTS products;

-- Employees Table
CREATE TABLE employees (
    employee_id INT PRIMARY KEY,
    name VARCHAR(50),
    department_id INT,
    job_title VARCHAR(50),
    salary DECIMAL(10, 2)
);

INSERT INTO employees VALUES
(1, 'Alice', 101, 'Engineer', 70000),
(2, 'Bob', 101, 'Engineer', 80000),
(3, 'Charlie', 102, 'Analyst', 65000),
(4, 'Daisy', 103, 'Manager', 90000),
(5, 'Ethan', 102, 'Analyst', 70000);

-- Sales Table
CREATE TABLE sales (
    sale_id INT PRIMARY KEY,
    product_id INT,
    category_id INT,
    sales_amount DECIMAL(10, 2),
    sale_date DATE
);

INSERT INTO sales VALUES
(1, 201, 10, 1000.00, '2024-01-01'),
(2, 202, 10, 1500.00, '2024-01-03'),
(3, 203, 11, 2000.00, '2024-01-04'),
(4, 201, 10, 500.00, '2024-01-05'),
(5, 203, 11, 1000.00, '2024-01-06');

-- Orders Table
CREATE TABLE orders (
    order_id INT PRIMARY KEY,
    customer_id INT,
    product_id INT,
    order_date DATE,
    region VARCHAR(50),
    status VARCHAR(20),
    sales_amount DECIMAL(10, 2)
);

INSERT INTO orders VALUES
(1001, 301, 201, '2024-02-01', 'North', 'Shipped', 500.00),
(1002, 302, 202, '2024-02-01', 'North', 'Pending', 600.00),
(1003, 303, 203, '2024-02-02', 'South', 'Shipped', 800.00),
(1004, 301, 202, '2024-02-03', 'North', 'Shipped', 900.00),
(1005, 304, 203, '2024-02-03', 'South', 'Cancelled', 750.00),
(1006, 302, 201, '2024-02-04', 'North', 'Pending', 300.00);

-- Products Table
CREATE TABLE products (
    product_id INT PRIMARY KEY,
    product_name VARCHAR(50),
    category_id INT,
    price DECIMAL(10, 2)
);

INSERT INTO products VALUES
(201, 'Widget', 10, 25.00),
(202, 'Gadget', 10, 40.00),
(203, 'Thingamajig', 11, 100.00),
(204, 'Doohickey', 12, 10.00);

-- select * from sales
-- selet * from product
-- select category_id, product_id, sum(sales_amount) as total_sales from sales  

-- Q1:
select s.category_id, s.product_id, p.product_name, s.total_sales
from (select category_id, product_id, sum(sales_amount) as total_sales from sales group by category_id, product_id) s
join (select category_id, max(total_sales) as max_category_sales 
from (select category_id, product_id, sum(sales_amount) as total_sales from sales 
group by category_id, product_id) t group by category_id) max_sales on s.category_id = max_sales.category_id 
and s.total_sales = max_sales.max_category_sales
join products p on s.product_id = p.product_id;

-- select * from sales;

-- Q2:
select department_id, avg(salary) as avg_salary
from employees group by department_id order by avg_salary desc limit 1;

-- select * from empl;

-- select department_id, avg(salary) as avg_sal from employees group by department_id


-- Q3: 
select e.employee_id, e.name, e.job_title, e.salary from employees e join (select department_id, avg(salary) 
as avg_sal from employees group by department_id) d on e.department_id = d.department_id where e.salary > d.avg_sal;

-- select * from orders;
-- select region, customer_id, count(order_id) as order_count from orders group by region, customer_id
-- select region, customer_id, count(order_id) as order_count from orders group by region, customer_id

-- Q4:
select t1.region, t1.customer_id, t1.order_count 
from (select region, customer_id, count(order_id) as order_count from orders group by region, customer_id) as t1 
join (select region, max(order_count) as max_orders from (select region, customer_id, count(order_id) as order_count 
from orders group by region, customer_id) as t group by region) as t2 on t1.region = t2.region and t1.order_count = t2.max_orders;

-- select * from products;


-- Q5: 
select category_id, avg(price) as avg_price from products group by category_id having avg_price > (select avg(price) from products);



-- Q6:
select p.product_id, p.product_name from products p left join orders o on p.product_id = o.product_id where o.product_id is null;

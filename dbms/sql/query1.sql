use bosch;
-- CREATE TABLE Student (
--     ID INT PRIMARY KEY,
--     Name VARCHAR(15) ,
--     Age INT,
--     Grade VARCHAR(5)
-- );

-- show tables;
-- select * from boschemp;
-- -- select name as nabe, age, salary from boschemp;
-- select * from boschemp where dept = 'IT';

-- select name, dept from boschemp where salary = (select max(salary) from boschemp);

-- select name, dept from boschemp where salary = (select min(salary) from boschemp);


-- insert into Student values(101,'A',23 ,'A');
-- insert into Student values(102,'B',22 ,'B');
-- insert into Student values(103,'C',21 ,'C');
-- insert into Student values(104,'D',20 ,'D');
-- insert into Student values(105,'E',24 ,'E')


-- update Student set Grade='A' where id=103;

-- update Student set Grade = 'First' where ID =104;
-- delete from Student where id = 105;

-- select * from Student order by age desc;

-- create table staff( id int primary key, name varchar(15), basic decimal(10,2), hra decimal(8,2), gross decimal(10,2));

-- insert into staff (id, name, basic) values (100, "A",  60000);
-- insert into staff (id, name, basic) values (101, "B",  50000);
-- insert into staff (id, name, basic) values (102, "C",  70000);
-- insert into staff (id, name, basic) values (103, "D",  80000);


-- update staff set hra=0.3*basic where basic > 0;
-- update staff set gross=basic+hra where basic > 0;
-- select * from staff;

-- create table bcust(custId int primary key,
--                   custname  varchar(15) not null);
--  
--  
-- insert into bcust values(10,'A');
-- insert into bcust values(20,'B');
-- insert into bcust values(30,'C');
-- insert into bcust values(40,'D');
--  
-- create table prod(pid    int primary key,
--                   pname  varchar(15) not null,
--                   custId int ,
--                   Foreign key (custId) references bcust(custId));
--  
--  
-- insert into prod values(100, 'Printer' ,  10);
-- insert into prod values(110, 'Head Set' , 20);
-- insert into prod values(120, 'LCD' ,      30);
-- insert into prod (pid,pname) values (130, 'Laser Printer');
--  
-- commit;
-- select * from bcust;
-- select * from prod;

-- SELECT
--     b.custId,
--     b.custname,
--     p.pname
-- FROM
--     bcust b
-- INNER JOIN
--     prod p
-- ON
--     b.custId = p.custId;

-- select b.custname
-- from
-- 	bcust b
-- inner join
-- 	prod p
-- on
-- 	p.pname = "LCD"
--     

-- create table xdept(   
--   deptno     numeric (2,0),   
--   dname      varchar(15),   
--   loc        varchar(15),   
--   constraint pk_xdept primary key (deptno)   
-- );
--  
--  
-- insert into xdept  values(10, 'ACCOUNTING', 'NEW YORK');
-- insert into xdept  values(20, 'RESEARCH', 'DALLAS');
-- insert into xdept  values(30, 'SALES', 'CHICAGO');
-- insert into xdept  values(40, 'OPERATIONS', 'BOSTON');

select * from xdept;
c-- reate table xemp(   
--   empno    numeric(4,0),   
--   ename    varchar2(10),   
--   job      varchar2(9),   
--   mgr      number(4,0),   
--   hiredate date,   
--   sal      number(7,2),   
--   comm     number(7,2),   
--   deptno   number(2,0),   
--   constraint pk_xemp primary key (empno),   
--   constraint fk__deptno foreign key (deptno) references xdept (deptno)   
-- ); 


-- Create the employee table 'xemp' with the specified columns and constraints.
CREATE TABLE xemp (
    empno      NUMERIC(4,0),
    ename      VARCHAR(10),
    job        VARCHAR(9),
    mgr        NUMERIC(4,0),
    hiredate   DATE,
    sal        NUMERIC(7,2),
    comm       NUMERIC(7,2),
    deptno     NUMERIC(2,0),
    CONSTRAINT pk_xemp PRIMARY KEY (empno),
    CONSTRAINT fk__deptno FOREIGN KEY (deptno) REFERENCES xdept (deptno)
);

-- Insert data for all employees into the 'xemp' table.
INSERT INTO xemp VALUES(7839, 'KING', 'PRESIDENT', null, to_date('17-11-1981','dd-mm-yyyy'), 5000, null, 10);
INSERT INTO xemp VALUES(7698, 'BLAKE', 'MANAGER', 7839, to_date('1-5-1981','dd-mm-yyyy'), 2850, null, 30);
INSERT INTO xemp VALUES(7782, 'CLARK', 'MANAGER', 7839, to_date('9-6-1981','dd-mm-yyyy'), 2450, null, 10);
INSERT INTO xemp VALUES(7566, 'JONES', 'MANAGER', 7839, to_date('2-4-1981','dd-mm-yyyy'), 2975, null, 20);
INSERT INTO xemp VALUES(7788, 'SCOTT', 'ANALYST', 7566, to_date('13-JUL-87','dd-mm-rr') - 85, 3000, null, 20);
INSERT INTO xemp VALUES(7902, 'FORD', 'ANALYST', 7566, to_date('3-12-1981','dd-mm-yyyy'), 3000, null, 20);
INSERT INTO xemp VALUES(7369, 'SMITH', 'CLERK', 7902, to_date('17-12-1980','dd-mm-yyyy'), 800, null, 20);
INSERT INTO xemp VALUES(7499, 'ALLEN', 'SALESMAN', 7698, to_date('20-2-1981','dd-mm-yyyy'), 1600, 300, 30);
INSERT INTO xemp VALUES(7521, 'WARD', 'SALESMAN', 7698, to_date('22-2-1981','dd-mm-yyyy'), 1250, 500, 30);
INSERT INTO xemp VALUES(7654, 'MARTIN', 'SALESMAN', 7698, to_date('28-9-1981','dd-mm-yyyy'), 1250, 1400, 30);
INSERT INTO xemp VALUES(7844, 'TURNER', 'SALESMAN', 7698, to_date('8-9-1981','dd-mm-yyyy'), 1500, 0, 30);
INSERT INTO xemp VALUES(7876, 'ADAMS', 'CLERK', 7788, to_date('13-JUL-87', 'dd-mm-rr') - 51, 1100, null, 20);
INSERT INTO xemp VALUES(7900, 'JAMES', 'CLERK', 7698, to_date('3-12-1981','dd-mm-yyyy'), 950, null, 30);
INSERT INTO xemp VALUES(7934, 'MILLER', 'CLERK', 7782, to_date('23-1-1982','dd-mm-yyyy'), 1300, null, 10);

COMMIT;

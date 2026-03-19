create database phone;
create table phonebook(
    id serial PRIMARY KEY ,
    first_name varchar(50),
    phone varchar(20)
);
select * from phonebook;
insert into phonebook (first_name, phone)
values ('Test', '123456789');
select * from phonebook;
delete from phonebook;
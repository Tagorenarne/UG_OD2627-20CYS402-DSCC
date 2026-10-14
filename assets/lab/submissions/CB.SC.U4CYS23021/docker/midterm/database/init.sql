create table users (
    id serial primary key, 
    username varchar(50) unique not null,
    password varchar(50) not null
);

insert into users(username, password) values('sanjai', 'sanjai235');
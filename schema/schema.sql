create table customers (
    id uuid primary key default gen_random_uuid(),
    customer_first text,
    customer_last text,
    customer_email text
)


create table accounts (
    id uuid primary key default gen_random_uuid(),
    balance numeric not null default 0,
    customer_id uuid references customers(id) not null
)

alter table customers add constraint customer_email_unique unique (customer_email);

drop table accounts;
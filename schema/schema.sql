-- We don't support deletion, becuase banks
-- are not allowed to delete their data. I think
-- That is why there is no 'on delete cascade'

create table customers (
    id uuid primary key default gen_random_uuid(),
    customer_first text,
    customer_last text,
    customer_email text unique,
    created_at timestamp not null default (now() at time zone 'utc')
)

create table accounts (
    id uuid primary key default gen_random_uuid(),
    balance numeric not null default 0,
    customer_id uuid references customers(id) not null,
    created_at timestamp not null default (now() at time zone 'utc')
)


create table transactions (
    id uuid primary key default gen_random_uuid(),
    amount numeric not null,
    sender_account_id uuid references accounts(id) not null,
    receiver_account_id uuid references accounts(id) not null,
    created_at timestamp not null default (now() at time zone 'utc')
)

drop table transaction;
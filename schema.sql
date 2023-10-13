create sequence user_id_seq
    as integer;

alter sequence user_id_seq owner to postgres;

grant select, update, usage on sequence user_id_seq to anon;

grant select, update, usage on sequence user_id_seq to authenticated;

grant select, update, usage on sequence user_id_seq to service_role;

create table retail_inventory
(
    potion_type_id integer not null,
    quantity_delta integer not null,
    price_delta    integer not null,
    id             serial
        constraint retail_inventory_pk2
            primary key,
    created_at     timestamp default CURRENT_TIMESTAMP
);

alter table retail_inventory
    owner to postgres;

grant select, update, usage on sequence retail_inventory_id_seq to anon;

grant select, update, usage on sequence retail_inventory_id_seq to authenticated;

grant select, update, usage on sequence retail_inventory_id_seq to service_role;

grant delete, insert, references, select, trigger, truncate, update on retail_inventory to anon;

grant delete, insert, references, select, trigger, truncate, update on retail_inventory to authenticated;

grant delete, insert, references, select, trigger, truncate, update on retail_inventory to service_role;

create table wholesale_inventory
(
    sku          text    not null,
    type         integer[]
        constraint enforce_length
            check (array_length(type, 1) = 4),
    num_ml_delta integer not null,
    id           serial
        constraint wholesale_inventory_pk3
            primary key,
    created_at   timestamp default CURRENT_TIMESTAMP
);

alter table wholesale_inventory
    owner to postgres;

grant select, update, usage on sequence wholesale_inventory_id_seq to anon;

grant select, update, usage on sequence wholesale_inventory_id_seq to authenticated;

grant select, update, usage on sequence wholesale_inventory_id_seq to service_role;

grant delete, insert, references, select, trigger, truncate, update on wholesale_inventory to anon;

grant delete, insert, references, select, trigger, truncate, update on wholesale_inventory to authenticated;

grant delete, insert, references, select, trigger, truncate, update on wholesale_inventory to service_role;

create table customer
(
    id         serial
        constraint customer_pk
            primary key,
    str        text not null
        constraint customer_pk2
            unique,
    created_at timestamp default CURRENT_TIMESTAMP
);

alter table customer
    owner to postgres;

grant select, update, usage on sequence customer_id_seq to anon;

grant select, update, usage on sequence customer_id_seq to authenticated;

grant select, update, usage on sequence customer_id_seq to service_role;

grant delete, insert, references, select, trigger, truncate, update on customer to anon;

grant delete, insert, references, select, trigger, truncate, update on customer to authenticated;

grant delete, insert, references, select, trigger, truncate, update on customer to service_role;

create table cart
(
    id          integer generated always as identity
        constraint cart_pk
            primary key,
    customer_id integer                 not null
        constraint cart_customer_id_fk
            references customer,
    checked_out boolean   default false not null,
    created_at  timestamp default CURRENT_TIMESTAMP
);

alter table cart
    owner to postgres;

grant select, update, usage on sequence cart_id_seq to anon;

grant select, update, usage on sequence cart_id_seq to authenticated;

grant select, update, usage on sequence cart_id_seq to service_role;

grant delete, insert, references, select, trigger, truncate, update on cart to anon;

grant delete, insert, references, select, trigger, truncate, update on cart to authenticated;

grant delete, insert, references, select, trigger, truncate, update on cart to service_role;

create table invoice
(
    id                     serial
        constraint invoice_pk
            primary key,
    wholesale_inventory_id integer
        constraint invoice_wholesale_inventory_id_fk
            references wholesale_inventory
            on delete set null,
    cart_id                integer
        constraint invoice_cart_id_fk
            references cart
            on delete set null,
    description            text,
    created_at             timestamp default CURRENT_TIMESTAMP
);

alter table invoice
    owner to postgres;

grant select, update, usage on sequence invoice_id_seq to anon;

grant select, update, usage on sequence invoice_id_seq to authenticated;

grant select, update, usage on sequence invoice_id_seq to service_role;

grant delete, insert, references, select, trigger, truncate, update on invoice to anon;

grant delete, insert, references, select, trigger, truncate, update on invoice to authenticated;

grant delete, insert, references, select, trigger, truncate, update on invoice to service_role;

create table transaction
(
    id           integer   default nextval('user_id_seq'::regclass) not null
        constraint transaction_pk
            primary key,
    created_at   timestamp default CURRENT_TIMESTAMP                not null,
    debit_credit integer                                            not null,
    invoice_id   integer
        constraint transaction_invoice_id_fk
            references invoice
            on delete set null
);

alter table transaction
    owner to postgres;

alter sequence user_id_seq owned by transaction.id;

grant delete, insert, references, select, trigger, truncate, update on transaction to anon;

grant delete, insert, references, select, trigger, truncate, update on transaction to authenticated;

grant delete, insert, references, select, trigger, truncate, update on transaction to service_role;

create table potion_type
(
    id    serial
        constraint potion_type_pk
            primary key,
    type  integer[]
        constraint potion_type_pk3
            unique,
    sku   text
        constraint potion_type_pk2
            unique,
    score integer default 0 not null,
    name  text              not null
);

alter table potion_type
    owner to postgres;

grant select, update, usage on sequence potion_type_id_seq to anon;

grant select, update, usage on sequence potion_type_id_seq to authenticated;

grant select, update, usage on sequence potion_type_id_seq to service_role;

grant delete, insert, references, select, trigger, truncate, update on potion_type to anon;

grant delete, insert, references, select, trigger, truncate, update on potion_type to authenticated;

grant delete, insert, references, select, trigger, truncate, update on potion_type to service_role;

create table cart_item
(
    id             serial
        constraint cart_item_pk
            primary key,
    cart_id        integer not null
        constraint cart_item_cart_id_fk
            references cart
            on delete cascade,
    potion_type_id integer
        constraint cart_item_potion_type_id_fk
            references potion_type
            on delete set null,
    quantity       integer not null,
    created_at     timestamp default CURRENT_TIMESTAMP
);

alter table cart_item
    owner to postgres;

grant select, update, usage on sequence cart_item_id_seq to anon;

grant select, update, usage on sequence cart_item_id_seq to authenticated;

grant select, update, usage on sequence cart_item_id_seq to service_role;

grant delete, insert, references, select, trigger, truncate, update on cart_item to anon;

grant delete, insert, references, select, trigger, truncate, update on cart_item to authenticated;

grant delete, insert, references, select, trigger, truncate, update on cart_item to service_role;

create view "current_catalog"(potion_type, potion_sku, potion_name, price, available_quantity) as
SELECT pt.type                                                AS potion_type,
       pt.sku                                                 AS potion_sku,
       pt.name                                                AS potion_name,
       ri_sum.price,
       ri_sum.quantity - COALESCE(ci_sum.quantity, 0::bigint) AS available_quantity
FROM potion_type pt
         LEFT JOIN (SELECT retail_inventory.potion_type_id,
                           sum(retail_inventory.price_delta)    AS price,
                           sum(retail_inventory.quantity_delta) AS quantity
                    FROM retail_inventory
                    GROUP BY retail_inventory.potion_type_id) ri_sum ON pt.id = ri_sum.potion_type_id
         LEFT JOIN (SELECT ci.potion_type_id,
                           sum(ci.quantity) AS quantity
                    FROM cart_item ci
                             JOIN cart ct ON ci.cart_id = ct.id
                    WHERE ct.checked_out = false
                    GROUP BY ci.potion_type_id) ci_sum ON pt.id = ci_sum.potion_type_id;

alter table "current_catalog"
    owner to postgres;

grant delete, insert, references, select, trigger, truncate, update on "current_catalog" to anon;

grant delete, insert, references, select, trigger, truncate, update on "current_catalog" to authenticated;

grant delete, insert, references, select, trigger, truncate, update on "current_catalog" to service_role;


create or replace procedure  upsert_contacts(p_name varchar,p_phone varchar)
language plpgsql
as $$
begin
    if exists(select 1 from contacts where name=p_name)then
        update contacts
        set phone=p_phone
        where name=p_name;
    else
        insert into contacts(name,phone)
        values(p_name,p_phone);

    end if;
end;
$$;
create or replace procedure insert_many_con(
    names text[],
    phones text[]
)
language plpgsql
as $$
declare
    i int;
begin
    for i in 1..array_length(names, 1)
    loop
        if phones[i] ~ '^[0-9]{10,}$' then

            if not exists (
                select 1 from contacts
                where name = names[i] and phone = phones[i]
            ) then
                insert into contacts(name, phone)
                values (names[i], phones[i]);
            else
                raise notice 'duplicate: % %', names[i], phones[i];
            end if;

        else
            raise notice 'invalid phone for %: %', names[i], phones[i];
        end if;
    end loop;
end;
$$;
create or replace procedure delete_con(p_value varchar)
language plpgsql
as $$
begin
    delete from contacts
    where name=p_value or phone=p_value;

end;
$$;
create or replace function search_con(p text)
returns  table (name varchar,phone varchar) as $$
begin
    return query
    select c.name ,c.phone
    from contacts c
where c.name ilike '%' || p || '%'
or c.phone ilike '%' || p  || '%';
end;
$$ language plpgsql;
create  or replace function get_con_pag(limit_val int ,off_val int)
returns table (name varchar, phone varchar) as $$
begin
              return query
              select c.name,c.phone
              from contacts c
              limit limit_val offset off_val;
end;
$$  language plpgsql;
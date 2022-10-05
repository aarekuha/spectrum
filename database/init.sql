create table sites_info(
    id bigserial,
    url varchar(1000),
    html text,
    title varchar(1000)
);

create unique index i_sites_info_url on sites_info(url);

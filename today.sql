drop table if exists today;
create table today (
    id integer primary key autoincrement,
    content string not null,
    timestamp datetime not null default (datetime('now', 'localtime')),
    status boolean not null default 0
);
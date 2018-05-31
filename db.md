## user

> 用户表


`InnoDB` `utf8_general_ci`

字段名 | 类型 | 是否可NULL | 描述
:--- | :--- | :--- | :---
id | int(11) | NO | 
name | char(20) | NO | 用户姓名
department | char(20) | NO | 部门名称
image | char(20) | NO | 图片
votes | int(11) | NO | 投票数
is_newbie | tinyint(4) | NO | 是否新人
sort_order | int(11) | NO | 排序


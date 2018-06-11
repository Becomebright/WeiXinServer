# ConferenceServer
**Web server for a WeiXin conference app, powered by Python Flask**



[TOC]

## 配置方式

- Python 3.5

- Flask

  - Flask
  - Flask-Bootstrap
  - Flask-Login
  - Flask-Migrate
  - Flask-MySQLdb
  - Flask-RESTful
  - Flask-SQLAlchemy
  - Flask-WTF
  - Jinja2

- 在`app`文件夹下创建`static/uploads`文件夹

- 在`WeiXinServer`文件夹下创建数据库：

  ```
  flask db init
  flask db migrate
  flask db upgrade
  ```

- 在`WeiXinServer`文件夹下启动服务器：`python run.py`

## V1.0

- 登录 / 注册 / 注销
- 添加会议
- 预览会议
- 查看会议详情 / 修改会议
- 审核报名人员
- 发布 / 查看会议回顾
- 文件上传 / 下载
- 与小程序端的交互

备注：数据库维护使用`flask-migrate`，原先`db`文件夹下的脚本
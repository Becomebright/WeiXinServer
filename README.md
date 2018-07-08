# ConferenceServer
**A Web server for a WeiXin conference mini program, powered by Python Flask**



## Configuration

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

- Create subdirectory `static/uploads` under `app` directory, that is you need to first create a directory `static` under `app`, then create a directory `uploads` under `static`

- Create database under `WeiXinServer` directory：

  ```
  flask db init
  flask db migrate
  flask db upgrade
  ```

- Run server in the background under `WeiXinServer` directory：`nohup python run.py &`
  - The logs will be stored at `nohup.out`

## V1.1

- Log in / Register / Log out
- Add conference
- Preview conference
- Check conference detail / Amend conference
- Verify enrollment
- Publish / Check conference review
- Document uploads / downloads
- Interact with WeiXin mini program

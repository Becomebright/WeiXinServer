#!flask/bin/python
# -*- coding: UTF-8 -*-

from app import app
# app.run(host='0.0.0.0',debug=True
#         , port=443, ssl_context=(
#     "1_dszdsz.cn_bundle.crt",
#     "2_dszdsz.cn.key")
# )
app.run(host='0.0.0.0',debug=True)
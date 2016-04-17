# -*- coding: utf-8 -*-
import cymysql
import requests
import Config
import json

url = "http://api.sendcloud.net/apiv2/mail/sendtemplate"

API_USER = 'Anybfans_apiuser'
API_KEY = '0Wr8ryOqy7CGXsss'

class Email():
	def __init__(self):
		self.conn = cymysql.connect(
					host=Config.MYSQL_HOST,
					port=Config.MYSQL_PORT,
					user=Config.MYSQL_USER,
					passwd=Config.MYSQL_PASS,
					db=Config.MYSQL_DB,
					charset='utf8'
				)
		self.cur = self.conn.cursor()

	def fetchall(self, sql):
		self.cur.execute(sql)
		ret = self.cur.fetchall()
		return ret

	def execute(self, uid_list):
		format_strings = ','.join(['%s'] * len(uid_list))
		sql = "UPDATE email set is_send=1 where uid in (%s)"
		self.cur.execute(sql % format_strings, tuple(uid_list))
		self.conn.commit()

   	def send(self, email_list, uid_list):
		xsmtpapi = {'to': []}
		for email in email_list:
			xsmtpapi['to'].append(email)
		params = {                                                                      
			"apiUser": API_USER, # 使用api_user和api_key进行验证                       
			"apiKey" : API_KEY,                                             
			"xsmtpapi" : json.dumps(xsmtpapi), # 收件人地址, 用正确邮件地址替代, 多个地址用';'分隔  
			"from" : "admin@anybfans.com", # 发信人, 用正确邮件地址替代     
			"fromname" : "Anybfans",                                                    
			"subject" : "Shadowsocks服务提醒【Anybfans】",                              
			"templateInvokeName" : "time_out",
		}
		r = requests.post(url, data=params)
		result = json.loads(r.text)
		
		if result['result'] == True:
			self.execute(uid_list)

	def user_list(self):
		sql = "SELECT u.email, u.uid FROM email e inner join user u on e.uid=u.uid where is_send=0"
		data_list = self.fetchall(sql)

		email_list = [d[0] for d in data_list]
		uid_list = [d[1] for d in data_list]
		return email_list, uid_list

if __name__ == '__main__':
	email = Email()
	user_list, uid_list = email.user_list()
	email.send(user_list, uid_list)

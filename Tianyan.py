# -*- coding: utf-8 -*-
import random
import time
import json
import pymysql

from PIL import Image
from selenium import webdriver
from selenium.webdriver import ActionChains
from pyquery import PyQuery as pq



class Tyc(object):
	def __init__(self):
		global Url
		#browser = webdriver.Chrome()
		Url = 'https://www.tianyancha.com/'
		chrome_path = 'E:\chromedriver_win32\chromedriver.exe'
		self.conn = pymysql.connect(host="127.0.0.1",user="root",passwd="",db="cms",port=3306)
		self.driver = webdriver.Chrome(executable_path=chrome_path)
		self.cursor = self.conn.cursor()
		self.driver.get(Url)

	def __del__(self):
		self.driver.close()

	def show_element(self, element):  # 让验证码图片迅速还原成完整图片
		self.driver.execute_script("arguments[0].style=arguments[1]", element, "display: block;")

	def hide_element(self, element):  # 暂不知用处
		self.driver.execute_script("arguments[0].style=arguments[1]", element, "display: none;")

	def open_login(self):
		try:
			t = random.uniform(0.5, 1)
			time.sleep(3)
			login_button = self.driver.find_element_by_xpath('//a[@class="link-white"]')
			login_button.click()
			time.sleep(2)
			pwd_button = self.driver.find_element_by_xpath('//div[@class="module module1 module2 loginmodule collapse in"]/div[1]/div[2]')
			pwd_button.click()
			time.sleep(3)
			username = self.driver.find_element_by_xpath('//div/div[2]/div/div/div[3]/div[2]/div[2]/input')
			username.send_keys('')
			time.sleep(t)
			password = self.driver.find_element_by_xpath('//input[@class="input contactword input-pwd"]')
			password.send_keys('')
			time.sleep(1)
			click_button = self.driver.find_element_by_xpath('//div[@onclick="loginObj.loginByPhone(event);"]')
			click_button.click()
			time.sleep(2)

		except Exception as e:
			print(e)

	def get_image_location(self):
		# 获取验证码图片路径--->调用get_images截取图片
		fullbg = self.driver.find_element_by_xpath('//div[10]/div[2]/div[2]/div[1]/div[2]/div[1]')
		self.hide_element(fullbg)
		self.show_element(fullbg)
		# 获取完整图片
		self.get_images(fullbg, 'tyc_full.png')
		# 点击一下滑动按钮触发出来带缺口的图片
		self.driver.find_element_by_xpath('//div[@class="gt_slider_knob gt_show"]').click()
		time.sleep(2)
		# 获取带缺口的图片
		bg = self.driver.find_element_by_xpath('//div[10]/div[2]/div[2]/div[1]/div[2]/div[1]')
		self.show_element(bg)
		self.get_images(bg, 'tyc_bg.png')

	def get_images(self, img, name):
		# 截图整个网页
		self.driver.save_screenshot(r'./Images/Tyc.png')
		# 验证码路径
		location = img.location
		# 验证码尺寸
		size = img.size
		top, bottom, left, right = location['y']+3, location['y'] + size['height'], location['x']-325, location['x'] + size['width']-328
		picture = Image.open(r'./Images/Tyc.png')
		picture = picture.crop((left, top, right, bottom))
		picture.save(r'./Images/%s' % name)
		time.sleep(0.5)

	def is_pixel_equal(self, tyc_bg, tyc_full, x, y ):
		"""
		:param tyc_bg: 带缺口图片
		:param tyc_full: 完整图片
		:param x: (Int) x位置
		:param y: (Int) y位置
		:return: (Boolean) 像素是否相同
		"""
		# 获取缺口图片的像素点（按RGE格式）
		bg_pixel = tyc_bg.load()[x, y]
		# 获取完整图片的像素点（按RGB格式）
		full_pixel = tyc_full.load()[x, y]
		threshold = 60
		if (abs(full_pixel[0] - bg_pixel[0] < threshold) and abs(full_pixel[1] - bg_pixel[1] < threshold) and abs(
				full_pixel[2] - bg_pixel[2] < threshold)):
			# 如果差值在判断值之内，返回是相同像素
			return True

	def get_distance(self, tyc_bg, tyc_full):
		"""
		:param tyc_bg: 带缺口图片
		:param tyc_full: 完整图片
		:return: (Int) 滑块与缺口的距离
		"""
		# 滑块位置初始设置为 60 (这个是去掉开始的一部分)
		left_dist = 60
		# 遍历像素点横坐标
		for i in range(left_dist, tyc_full.size[0]):
			# 遍历像素点纵坐标
			for j in range(tyc_full.size[1]):
				if not self.is_pixel_equal(tyc_bg, tyc_full, i, j):
					# 返回此时横轴坐标就是滑块需要移动的距离
					return i

	def get_trace(self, distance):
		"""
		:param distrance: (Int)缺口与滑块之间的距离
		:return: (List)移动轨迹
		"""
		# 创建存放轨迹信息的列表
		trace = []
		# 设置加速的距离
		faster_distance = distance * 1.5
		# 设置初始位置、初始速度、时间间隔
		start, v0, t = 0, 0, 0.1
		# 当尚未移动到终点时
		while start < distance:
			# 如果处于加速阶段
			if start < faster_distance:
				# 设置加速度为2
				a = 12
			# 如果处于减速阶段
			else:
				# 设置加速度为-3
				a = -4
			# 移动的距离公式
			move = v0 * t + 1 / 2 * a * t * t
			# 此刻速度
			v = v0 + a * t
			# 重置初速度
			v0 = v
			# 重置起点
			start += move
			# 将移动的距离加入轨迹列表
			trace.append(round(move))
		# 返回轨迹信息
		return trace

	def move_to_gap(self, trace):
		t = random.uniform(0, 0.5)
		# 得到滑块标签
		slider = self.driver.find_element_by_xpath('//div[@class="gt_slider_knob gt_show"]')
		# 使用click_and_hold()方法悬停在滑块上，perform()方法用于执行
		ActionChains(self.driver).click_and_hold(slider).perform()
		for x in trace:
			# 使用move_by_offset()方法拖动滑块，perform()方法用于执行
			ActionChains(self.driver).move_by_offset(xoffset=x, yoffset=0).perform()
		# 模拟人类对准时间
		time.sleep(t)
		# 释放滑块
		ActionChains(self.driver).release().perform()

	def slice(self):
		bg_image = Image.open(r'./Images/tyc_bg.png')
		full_image = Image.open(r'./Images/tyc_full.png')
		try:
			distance = self.get_distance(bg_image, full_image)
			print('计算偏移量为：%s Px' % distance)
			trace = self.get_trace(int(distance)-5)
			print(trace)
			# 移动滑块
			self.move_to_gap(trace)
			time.sleep(0.5)
			while True:
				for i in range(6, 10):
					mspan = self.driver.find_element_by_xpath('//div[@class="gt_info_text"]/span[2]').text
					print(mspan)
					if '拖动滑块' in mspan:
						time.sleep(1)
						distance = self.get_distance(bg_image, full_image)
						print('计算偏移量为：%s Px' % distance)
						trace = self.get_trace(int(distance)-int(i))
						print('减值%s' % i)
						print(trace)
						# 移动滑块
						self.move_to_gap(trace)
						time.sleep(0.5)
					else:
						if '怪物' in mspan:
							time.sleep(5)
							self.get_image_location()
							self.slice()
						else:
							break
				break
		except Exception as e:
			if '//span[@class="gt_info_content"]' in str(e):
				pass
			else:
				print(e)

	def get_html(self):
		Title = self.driver.find_element_by_xpath('//div[@class="home-title"]').text
		print(Title)


	def parser_one_page(self,u):
		try:
			#browser.get(u)
			self.driver.get(u)
			# 获得页面
			html = self.driver.page_source
			doc = pq(html)
			items = doc('.result-list .search-item').items()
			for item in items:
				company_name = item.find('.content .header a').text()  # 公司名称
				company_link = item.find('.content .header a').attr('href') #详细链接
				zhuangtai = item.find('.content .header div').text()  # 公司状态
				daibiao = item.find('.content .info .title').eq(0).text().replace("法定代表人：","")  # 法定代表人
				zhuceziben = item.find('.content .info .title').eq(1).text().replace("注册资本：","")  # 注册资本
				chengli = item.find('.content .info .title').eq(2).text().replace("成立日期：","")  # 成立日期
				dianhua = item.find('.content .contact div').eq(0).find('span').eq(1).text().replace("查看更多","") # 电话
				if item.find('.content .contact div').eq(0).find("script").text() != '':
                                        dianhua = item.find('.content .contact div').eq(0).find("script").text().replace("[","").replace("]","").replace("\"","")
				youxiang = item.find('.content .contact div').eq(1).find('span').eq(1).text()  # 邮箱
				if item.find('.content .contact div').eq(1).find('script').text() != '':
					youxiang = item.find('.content .contact div').eq(1).find('script').text().replace("[","").replace("]","").replace("\"","")
				qita = item.find('.content .match span').eq(1).text()  # 其他信息
				shengfen = item.find('.site').text() #省份
				score = item.find('.score').text() #评分
				#print(company_name)
				#print(company_link)
				#print(zhuangtai)
				#print(daibiao)
				#print(zhuceziben)
				#print(chengli)
				#print(dianhua)
				#print(youxiang)
				#print(qita)
				#print(shengfen)
				#print(score)

				yield {
					'name': company_name,
					'homepage': company_link,
					'biz_status': zhuangtai,
					'representative': daibiao,
					'registered_capital': zhuceziben,
					'setup_time': chengli,
					'phone': dianhua,
					'email': youxiang,
					'other': qita,
					'region': shengfen,
					'score': score,
					'address' : '-',
					'city' : '-',
					'district' : '-',
					'lat_long' : '-',
					'register_code' : '-',
					'industry' : '-',
					'biz_scope' : '-',
					'company_type' : '-',
					'actual_capital' : '-',
					'taxpayer_code' : '-',
					'organization_code' : '-',
					'english_name' : '-',
					'authorization' : '-',
					'used_name' : '-',
					'credit_code' : '-'
				}
		except IndexError as e:
			self.parser_one_page(u)

	# 写入文件
	def write_to_file(self,c):  # 写入文本
		with open('tianyancha.txt', 'a', encoding='utf-8') as f:
			f.write(json.dumps(c, ensure_ascii=False) + '\n')

	def insertdb(self,data):
		sql = 'insert into enterprise(`name`,`representative`,`address`,`region`,`city`,`district`,' \
			  '`lat_long`,`biz_status`,`credit_code`,`register_code`,`phone`,`email`,`setup_time`,' \
			  '`industry`, `biz_scope`,`company_type`,`registered_capital`,`actual_capital`,' \
			  '`taxpayer_code`, `organization_code`,`english_name`,`authorization`,`homepage`,' \
			  '`used_name`,`gmt_create`, `gmt_modify`) ' \
			  'values(%(name)s,%(representative)s,%(address)s,%(region)s,%(city)s,%(district)s,' \
			  '%(lat_long)s,%(biz_status)s,%(credit_code)s,%(register_code)s,%(phone)s,%(email)s,' \
			  '%(setup_time)s, %(industry)s,%(biz_scope)s,%(company_type)s,%(registered_capital)s,' \
			  '%(actual_capital)s, %(taxpayer_code)s,%(organization_code)s,%(english_name)s,' \
			  '%(authorization)s,%(homepage)s, %(used_name)s,now(),now()) '
			  
		self.write_tx(sql, data)

	def write_tx(self, sql, data):
		self.cursor.execute(sql, data)
		#try:
		#	connection.commit()
		#except RuntimeError as error:
		#	connection.rollback()
		#	log.error('事务提交失败！已回滚')
		#	raise error

		self.conn.commit()

	def entrace(self):
		self.open_login()
		self.get_image_location()
		self.slice()
		self.get_html()
		for i in range(1, 2):
			#抓取医院信息
			u = Url +'search/p'+str(i)+'?key=管道'
			#self.driver.get(u)
			for item in self.parser_one_page(u):
				#print(item)
				#self.write_to_file(item)
				self.insertdb(item)
		self.cursor.close()
		self.conn.close()


if __name__ == '__main__':
	tyc = Tyc()
	tyc.entrace()



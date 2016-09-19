#!/usr/bin/env python
# -*- coding: utf-8 -*-

import urllib
#import httplib
import sys
import re
import os
import psycopg2
import psycopg2.extras
import db_config as config
import math
import tempfile

def add_changesets_for_deleted_nodes(changesets,bbox):
	try:
		# Получаем список отношений, в которых состоят линии, которым принадлежит искомая точка:
		sql="""select changeset_id from nodes where visible!='t' and latitude > %(left_down_lat)d and latitude < %(right_up_lat)d and longitude > %(left_down_lon)d and longitude < %(right_up_lon)d GROUP BY changeset_id;""" % \
			{"left_down_lat":bbox["left_down"]["lat"], "left_down_lon":bbox["left_down"]["lon"], "right_up_lat":bbox["right_up"]["lat"],"right_up_lon":bbox["right_up"]["lon"]}
		if config.debug==True:
			print("""sql: %s""" % sql)
		cur.execute(sql)
		changeset_ids = cur.fetchall()
	except:
		print ("I am unable fetch data from db");sys.exit(1)
	# Получаем имена отношений:
	for changeset_id in changeset_ids:
		changesets.add(int(changeset_id[0]))
	return changesets


def print_html_changesets(changesets,base_url):
	print("""
		<TABLE BORDER>
		<TR>    
				<TH COLSPAN=2>Список правок, в которых были удалены данные в этой области</TH>
		</TR>
		<TR>
		<TH>№</TH>
		<TH>Ссылка на правку</TH>
		</TR>
		""")
	index=0	
	for changeset_id in changesets:
		index+=1
		url="%s/%d" % (base_url,changeset_id)
		print("""<TR>
					 <TD>%(index)d</TD>
					 <TD>
<a target="_self" href="%(url)s">Правка №%(changeset_id)d</a>
					 </TD>
				 </TR>""" % \
					 {"index":index, \
					 "url":url, \
					 "changeset_id":changeset_id, \
					 } )

	print("</TABLE>")


# ======================================= main() ===========================

# параметры, переданные скрипту через url:
# http://angel07.webservis.ru/perl/env.html
#param=os.getenv("QUERY_STRING_UNESCAPED")
param=os.getenv("QUERY_STRING")
#param=os.getenv("HTTP_USER_AGENT")
bbox={}
bbox["left_down"]={}
bbox["right_up"]={}

# Убираем 'n':
if config.debug:
	bbox["left_down"]["lat"]=433686200
	bbox["left_down"]["lon"]=1321324000
	bbox["right_up"]["lat"]=434292820
	bbox["right_up"]["lon"]=1322277500
else:
	success_params={}
	list_param=param.split("&")
	for item in list_param:
		success_params[item.split("=")[0]]=item.split("=")[1]
	bbox["left_down"]["lat"]=int(float(success_params["left_down_lat"])*10000000)
	bbox["left_down"]["lon"]=int(float(success_params["left_down_lon"])*10000000)
	bbox["right_up"]["lat"]=int(float(success_params["right_up_lat"])*10000000)
	bbox["right_up"]["lon"]=int(float(success_params["right_up_lon"])*10000000)


#print "Content-Type: text/html\n\n"; 
print"""
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0 Transitional//EN">
<HTML>
<HEAD>
<META HTTP-EQUIV="CONTENT-TYPE" CONTENT="text/html; charset=utf-8">
<TITLE></TITLE>
<META NAME="GENERATOR" CONTENT="OpenOffice.org 3.1  (Linux)">
<META NAME="AUTHOR" CONTENT="Сергей Семёнов">
<META NAME="CREATED" CONTENT="20100319;10431100">
<META NAME="CHANGEDBY" CONTENT="Сергей Семёнов">
<META NAME="CHANGED" CONTENT="20100319;10441400">
<STYLE TYPE="text/css">
<!--
@page { size: 21cm 29.7cm; margin: 2cm }
P { margin-bottom: 0.21cm }
-->
</STYLE>

<style>
   .normaltext {
   }
</style>
<style>
   .ele_null {
    color: red; /* Красный цвет выделения */
   }
</style>
<style>
   .selected_node {
    color: green; /* Зелёный цвет выделения */
	background: #D9FFAD;
	font-size: 150%;
   }
</style>

</HEAD>
<BODY LANG="ru-RU" LINK="#000080" VLINK="#800000" DIR="LTR">
"""
#print("parameters: %s" % (param) )
#print("bbox:",  bbox )


try:
	if config.debug:
		print("connect to: dbname='" + config.db_name + "' user='" +config.db_user + "' host='" + config.db_host + "' password='" + config.db_passwd + "'")
	conn = psycopg2.connect("dbname='" + config.db_name + "' user='" +config.db_user + "' host='" + config.db_host + "' password='" + config.db_passwd + "'")
	cur = conn.cursor()
except:
    print ("I am unable to connect to the database");sys.exit(1)

changesets=set()

add_changesets_for_deleted_nodes(changesets,bbox)

if config.debug:
	#print_text_line_profile(lines)
	print("d")
	print_html_changesets(changesets,config.base_url)
else:
	print_html_changesets(changesets,config.base_url)


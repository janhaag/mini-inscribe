#!/usr/bin/python

# Copyright (C) 2013  Jan Haag
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

print("Content-Type: text/html")
print()

import cgitb
cgitb.enable()

import sys
import sqlite3

from cgi import FieldStorage
from html import escape

form = FieldStorage()
conn = sqlite3.connect("db/result.db", detect_types=sqlite3.PARSE_DECLTYPES)
cur = conn.cursor()

def init_assist_stage1():
    cur.execute("drop table if exists system")
    cur.execute("create table system (keys text)")
    print_user_form()
    print("<h1>WARNING: Setup mode, values WILL NOT be stored!</h1>")

def init_assist_stage2():
    keys = ""
    for key in form.keys():
        val = form.getvalue(key)
        try:
            int(val)
            keys += key + " INTEGER, "
            continue
        except:
            pass
        try:
            float(val)
            keys += key + " REAL, "
            continue
        except:
            pass
        keys += key + " TEXT, "
    keys = keys[:-2]
    cur.execute("delete from system")
    cur.execute("insert into system values (?)", [keys,])
    cur.execute("drop table if exists data")
    cur.execute("create table data (" + keys + ")")
    print("<html><head><title>Init results:</title></head>")
    print("<body><h1>Init results</h1>")
    print(keys)
    print("<a href=\"index.py\">Finish setup</a></body></html>")
    print("</body></html>")

def process_form():
    known_keys = get_keys()
    vals = []
    for (key, t) in known_keys:
        if key not in form.keys():
            if t == "INTEGER":
                vals.append(0)
            elif t == "REAL":
                vals.append(0.0)
            else:
                vals.append("")
            continue
        val = form.getfirst(key)
        if t == "INTEGER":
            try:
                val = int(val)
                vals.append(val)
            except:
                bail(key + " should be an int, but isn't.")
        elif t == "REAL":
            try:
                val = float(val)
                vals.append(val)
            except:
                bail(key + " should be a float, but isn't.")
        else:
            vals.append(val)
    query = "insert into data values ("
    for i in range(len(vals) - 1):
        query += "?, "
    query += "?)"
    cur.execute(query, vals)
    conn.commit()

def query():
    settings = {}
    settings["query.columns"] = form.getfirst("query.columns", default="*")
    settings["query.limits"] = form.getfirst("query.limits", default="")
    settings["table.prefix"] = form.getfirst("table.prefix", default="")
    settings["table.postfix"] = form.getfirst("table.postfix", default="")
    settings["table.preline"] = form.getfirst("table.preline", default="\"")
    settings["table.postline"] = form.getfirst("table.postline", default="\"")
    settings["table.colsep"] = form.getfirst("table.colsep", default="\",\"")
    settings["table.headsep"] = form.getfirst("table.headsep", default="")
    settings["table.hidehead"] = form.getfirst("table.hidehead", default="false")
    print("<html><head><title>Query mode</title></head>")
    print("<body><h1>Query mode</h1>")
    print_query_form(settings)
    print("<pre>")
    print_table(settings)
    print("</pre><br/><a href=\"index.py\">Leave query mode</a></body></html>")

def print_table(settings):
    if settings["table.prefix"] != "":
        print(settings["table.prefix"])
    if settings["table.hidehead"] == "false":
        keys = get_keys()
        print_table_line(settings, keys.keys())
        if settings["table.headsep"] != "":
            print(settings["table.headsep"])
    query = "select "
    query += settings["query.columns"]
    query += " from data "
    if settings["query.limits"] != "":
        query += "where "
        query += settings["query.limits"]
    cur.execute(query)
    res = cur.fetchall()
    for line in res:
        print_table_line(settings, line)
    if settings["table.postfix"] != "":
        print(settings["table.postfix"])

def print_table_line(settings, fields):
    line = settings["table.preline"]
    line += settings["table.colsep"].join(fields)
    line += settings["table.postline"]
    print(line)

def print_query_form(settings):
    print("<form name=\"query\" action=\"index.py\" method=\"post\">")
    print("<input type=\"hidden\" name=\"system.query\" value=\"true\"/>")
    print("Select columns (SQL):</br>")
    print("<input type=\"text\" name=\"query.columns\" size=100 value=\""
            + escape(settings["query.columns"]) + "\"/>")
    print("<br/><br/>Limits, grouping and other stuff (SQL):<br/>")
    print("<input type=\"text\" name=\"query.limits\" size=100 value=\""
            + escape(settings["query.limits"]) + "\"/>")
    print("<br/><br/>Prefix to the table:<br/>")
    print("<input type=\"text\" name=\"table.prefix\" size=100 value=\""
            + escape(settings["table.prefix"]) + "\"/>")
    print("<br/><br/>Postfix to the table:<br/>")
    print("<input type=\"text\" name=\"table.postfix\" size=100 value=\""
            + escape(settings["table.postfix"]) + "\"/>")
    print("<br/><br/>Prefix to each line:<br/>")
    print("<input type=\"text\" name=\"table.preline\" size=100 value=\""
            + escape(settings["table.preline"]) + "\"/>")
    print("<br/><br/>Postfix to each line:<br/>")
    print("<input type=\"text\" name=\"table.postline\" size=100 value=\""
            + escape(settings["table.postline"]) + "\"/>")
    print("<br/><br/>Column separator:<br/>")
    print("<input type=\"text\" name=\"table.colsep\" size=100 value=\""
            + escape(settings["table.colsep"]) + "\"/>")
    print("<br/><br/>Separator between head and body:<br/>")
    print("<input type=\"text\" name=\"table.headsep\" size=100 value=\""
            + escape(settings["table.headsep"]) + "\"/>")
    print("<br/><br/>Should the table's header line be hidden?")
    print("<input type=\"checkbox\" name=\"table.hidehead\" value=\"true\""
            + ( " checked=\"checked\"" if settings["table.hidehead"] == "true" else "") + "/>")
    print("<br/><br/><input type=\"submit\" value=\"Query\"/>")
    print("</form><br/>")

def get_keys():
    cur.execute("select keys from system")
    keys_db = cur.fetchone()[0]
    keys_db = keys_db.split(", ")
    keys = []
    for typedkey in keys_db:
        (key, t) = typedkey.split(" ")
        keys.append((key, t))
    return keys

def print_user_form():
    with open("form.html") as f:
        print(f.read(-1))

def bail(msg):
    print("<html><head><title>Error!</title></head>")
    print("<body><h1>Error!</h1>")
    print(msg)
    print("<br/><form><input type=\"submit\" value=\"Try again...\"/>")
    print("</form></body></html>")
    sys.exit(0)

cur.execute("select name from SQLITE_MASTER where type='table' and name='system'")

if len(form) == 0:
    print_user_form()
elif "system.init" in form:
    init_assist_stage1()
elif "system.query" in form:
    query()
elif cur.fetchall()[0][0] == 'system':
    cur.execute("select keys from system")
    res = cur.fetchall()
    if len(res) == 0:
        init_assist_stage2()
    else:
        process_form()
        print_user_form()
else:
    bail("Database not initialized and \"system.init\" not given.")

